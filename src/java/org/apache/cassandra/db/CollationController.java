/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.cassandra.db;

import java.io.Closeable;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.TreeSet;

import com.google.common.base.Function;
import com.google.common.collect.Iterables;
import com.google.common.collect.Iterators;

import org.apache.cassandra.concurrent.Stage;
import org.apache.cassandra.concurrent.StageManager;
import org.apache.cassandra.db.columniterator.OnDiskAtomIterator;
import org.apache.cassandra.db.composites.CellName;
import org.apache.cassandra.db.filter.NamesQueryFilter;
import org.apache.cassandra.db.filter.QueryFilter;
import org.apache.cassandra.db.marshal.CounterColumnType;
import org.apache.cassandra.io.sstable.format.SSTableReader;
import org.apache.cassandra.io.util.FileUtils;
import org.apache.cassandra.mutants.MemSsTableAccessMon;
import org.apache.cassandra.tracing.Tracing;
import org.apache.cassandra.utils.SearchIterator;
import org.apache.cassandra.utils.memory.HeapAllocator;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CollationController
{
    private static final Logger logger = LoggerFactory.getLogger(CollationController.class);

    private final ColumnFamilyStore cfs;
    private final QueryFilter filter;
    private final int gcBefore;

    private int sstablesIterated = 0;

    public CollationController(ColumnFamilyStore cfs, QueryFilter filter, int gcBefore)
    {
        this.cfs = cfs;
        this.filter = filter;
        this.gcBefore = gcBefore;
    }

    public ColumnFamily getTopLevelColumns(boolean copyOnHeap)
    {
        return getTopLevelColumns(copyOnHeap, false);
    }

    public ColumnFamily getTopLevelColumns(boolean copyOnHeap, boolean mtdb_trace)
    {
        //if (mtdb_trace)
        //    logger.warn("MTDB:");

        return filter.filter instanceof NamesQueryFilter
               && cfs.metadata.getDefaultValidator() != CounterColumnType.instance
               ? collectTimeOrderedData(copyOnHeap, mtdb_trace)
               : collectAllData(copyOnHeap, mtdb_trace);
    }

    /**
     * Collects data in order of recency, using the sstable maxtimestamp data.
     * Once we have data for all requests columns that is newer than the newest remaining maxtimestamp,
     * we stop.
     */
    private ColumnFamily collectTimeOrderedData(boolean copyOnHeap, boolean mtdb_trace)
    {
        final ColumnFamily container = ArrayBackedSortedColumns.factory.create(cfs.metadata, filter.filter.isReversed());
        if (mtdb_trace) {
            logger.warn("MTDB: container={} container.deletionInfo={}", container, container.deletionInfo());
        }
        List<OnDiskAtomIterator> iterators = new ArrayList<>();
        boolean isEmpty = true;
        Tracing.trace("Acquiring sstable references");
        ColumnFamilyStore.ViewFragment view = cfs.select(cfs.viewFilter(filter.key), mtdb_trace);
        DeletionInfo returnDeletionInfo = container.deletionInfo();

        try
        {
            Tracing.trace("Merging memtable contents");
            for (Memtable memtable : view.memtables)
            {
                if (mtdb_trace) {
                    logger.warn("MTDB: {}", memtable);
                }
                ColumnFamily cf = memtable.getColumnFamily(filter.key);
                if (cf != null)
                {
                    if (mtdb_trace) {
                        logger.warn("MTDB: {}", cf);
                    }
                    filter.delete(container.deletionInfo(), cf);
                    isEmpty = false;
                    Iterator<Cell> iter = filter.getIterator(cf);
                    while (iter.hasNext())
                    {
                        Cell cell = iter.next();
                        if (copyOnHeap)
                            cell = cell.localCopy(cfs.metadata, HeapAllocator.instance);
                        container.addColumn(cell);
                        if (mtdb_trace) {
                            logger.warn("MTDB: {}", container);
                        }
                    }
                }
            }

            // avoid changing the filter columns of the original filter
            // (reduceNameFilter removes columns that are known to be irrelevant)
            NamesQueryFilter namesFilter = (NamesQueryFilter) filter.filter;
            TreeSet<CellName> filterColumns = new TreeSet<>(namesFilter.columns);
            QueryFilter reducedFilter = new QueryFilter(filter.key, filter.cfName, namesFilter.withUpdatedColumns(filterColumns), filter.timestamp);
            if (mtdb_trace) {
                logger.warn("MTDB: reducedFilter={} filter.timestamp={}", reducedFilter, filter.timestamp);
            }

            /* add the SSTables on disk */
            // Hobin: sstables with bigger gen (younger sstables) first
            Collections.sort(view.sstables, SSTableReader.maxTimestampComparator);
            if (mtdb_trace) {
                for (SSTableReader sstable : view.sstables)
                {
                    logger.warn("MTDB: sstable {} max_ts {} min_ts {}"
                            , sstable.descriptor.generation
                            , sstable.getMaxTimestamp()
                            , sstable.getMinTimestamp()
                            );
                }
            }

            // read sorted sstables
            // Hobin: view.sstables contains all sstables
            for (SSTableReader sstable : view.sstables)
            {
                if (mtdb_trace) {
                    logger.warn("MTDB: sstable {}", sstable.descriptor.generation);
                }

                // if we've already seen a row tombstone with a timestamp greater
                // than the most recent update to this sstable, we're done, since the rest of the sstables
                // will also be older
                if (sstable.getMaxTimestamp() < returnDeletionInfo.getTopLevelDeletion().markedForDeleteAt)
                    break;

                // Hobin: max ts makes sense, not min ts. You want a guarantee
                // that a SSTable doesn't have a key with a ts bigger than a
                // value.
                long currentMaxTs = sstable.getMaxTimestamp();
                reduceNameFilter(reducedFilter, container, currentMaxTs);
                // Hobin: reducedFilter.filter.columns becomes empty after
                // checking with the currentMaxTs
                if (((NamesQueryFilter) reducedFilter.filter).columns.isEmpty())
                    break;
                if (mtdb_trace) {
                    logger.warn("MTDB: sstable {}", sstable.descriptor.generation);
                }

                Tracing.trace("Merging data from sstable {}", sstable.descriptor.generation);
                sstable.incrementReadCount();
                OnDiskAtomIterator iter = reducedFilter.getSSTableColumnIterator(sstable);
                iterators.add(iter);
                isEmpty = false;
                if (mtdb_trace) {
                    //MemSsTableAccessMon.Update(this, readMeter.count());
                    MemSsTableAccessMon.Update(sstable);

                    // iter.getColumnFamily() == null means the sstable doesn't
                    // have the requested data. and probably by the bloom
                    // filter said so.
                    logger.warn("MTDB: sstable {} read_meter_count={} false_positive={} true_positive={} iter.getColumnFamily()={}"
                            , sstable.descriptor.generation
                            , sstable.getReadMeter().count()
                            , sstable.getBloomFilterFalsePositiveCount()
                            , sstable.getBloomFilterTruePositiveCount()
                            , iter.getColumnFamily()
                            );
                }
                if (iter.getColumnFamily() != null)
                {
                    //if (mtdb_trace) {
                    //    logger.warn("MTDB: {} {}", container, iter.getColumnFamily());
                    //}
                    container.delete(iter.getColumnFamily());
                    //if (mtdb_trace) {
                    //    logger.warn("MTDB: {}", container);
                    //}
                    sstablesIterated++;
                    // Seems like adding columns one by one
                    while (iter.hasNext()) {
                        container.addAtom(iter.next());
                        //if (mtdb_trace) {
                        //    logger.warn("MTDB: {}", container);
                        //}
                    }
                }
            }

            // we need to distinguish between "there is no data at all for this row" (BF will let us rebuild that efficiently)
            // and "there used to be data, but it's gone now" (we should cache the empty CF so we don't need to rebuild that slower)
            if (isEmpty)
                return null;

            // do a final collate.  toCollate is boilerplate required to provide a CloseableIterator
            ColumnFamily returnCF = container.cloneMeShallow();
            Tracing.trace("Collating all results");
            filter.collateOnDiskAtom(returnCF, container.iterator(), gcBefore);

            // "hoist up" the requested data into a more recent sstable
            if (sstablesIterated > cfs.getMinimumCompactionThreshold()
                && !cfs.isAutoCompactionDisabled()
                && cfs.getCompactionStrategy().shouldDefragment())
            {
                if (mtdb_trace) {
                    logger.warn("MTDB: what is \"hoist up\"?");
                }
                // !!WARNING!!   if we stop copying our data to a heap-managed object,
                //               we will need to track the lifetime of this mutation as well
                Tracing.trace("Defragmenting requested data");
                final Mutation mutation = new Mutation(cfs.keyspace.getName(), filter.key.getKey(), returnCF.cloneMe());
                StageManager.getStage(Stage.MUTATION).execute(new Runnable()
                {
                    public void run()
                    {
                        // skipping commitlog and index updates is fine since we're just de-fragmenting existing data
                        Keyspace.open(mutation.getKeyspaceName()).apply(mutation, false, false);
                    }
                });
            }

            // Caller is responsible for final removeDeletedCF.  This is important for cacheRow to work correctly:
            return returnCF;
        }
        finally
        {
            for (OnDiskAtomIterator iter : iterators)
                FileUtils.closeQuietly(iter);
        }
    }

    /**
     * remove columns from @param filter where we already have data in @param container newer than @param sstableTimestamp
     */
    private void reduceNameFilter(QueryFilter filter, ColumnFamily container, long sstableTimestamp)
    {
        if (container == null)
            return;

        SearchIterator<CellName, Cell> searchIter = container.searchIterator();
        for (Iterator<CellName> iterator = ((NamesQueryFilter) filter.filter).columns.iterator(); iterator.hasNext() && searchIter.hasNext(); )
        {
            CellName filterColumn = iterator.next();
            Cell cell = searchIter.next(filterColumn);
            if (cell != null && cell.timestamp() > sstableTimestamp)
                iterator.remove();
        }
    }

    /**
     * Collects data the brute-force way: gets an iterator for the filter in question
     * from every memtable and sstable, then merges them together.
     */
    private ColumnFamily collectAllData(boolean copyOnHeap, boolean mtdb_trace)
    {
        //if (mtdb_trace)
        //    logger.warn("MTDB:");

        Tracing.trace("Acquiring sstable references");
        ColumnFamilyStore.ViewFragment view = cfs.select(cfs.viewFilter(filter.key), mtdb_trace);
        // Hobin: sometimes view has a smaller number of SSTables, probably by
        // some kind of filtering using cache.
        List<Iterator<? extends OnDiskAtom>> iterators = new ArrayList<>(Iterables.size(view.memtables) + view.sstables.size());
        ColumnFamily returnCF = ArrayBackedSortedColumns.factory.create(cfs.metadata, filter.filter.isReversed());
        DeletionInfo returnDeletionInfo = returnCF.deletionInfo();
        try
        {
            Tracing.trace("Merging memtable tombstones");
            for (Memtable memtable : view.memtables)
            {
                // I wonder why
                //   select * from table1 where key=0; takes this path, but
                //   select * from table1; doesn't.
                final ColumnFamily cf = memtable.getColumnFamily(filter.key);
                if (mtdb_trace) {
                    //logger.warn("MTDB: memtable={} filter.key={}", memtable, filter.key);
                    MemSsTableAccessMon.Update(memtable, cf);
                }
                if (cf != null)
                {
                    filter.delete(returnDeletionInfo, cf);
                    Iterator<Cell> iter = filter.getIterator(cf);
                    //if (mtdb_trace) {
                    //    logger.warn("MTDB: cf={} filter={} iter={} copyOnHeap={}", cf, filter, iter, copyOnHeap);
                    //}
                    if (copyOnHeap)
                    {
                        iter = Iterators.transform(iter, new Function<Cell, Cell>()
                        {
                            public Cell apply(Cell cell)
                            {
                                return cell.localCopy(cf.metadata, HeapAllocator.instance);
                            }
                        });
                    }
                    iterators.add(iter);
                }
            }

            /*
             * We can't eliminate full sstables based on the timestamp of what we've already read like
             * in collectTimeOrderedData, but we still want to eliminate sstable whose maxTimestamp < mostRecentTombstone
             * we've read. We still rely on the sstable ordering by maxTimestamp since if
             *   maxTimestamp_s1 > maxTimestamp_s0,
             * we're guaranteed that s1 cannot have a row tombstone such that
             *   timestamp(tombstone) > maxTimestamp_s0
             * since we necessarily have
             *   timestamp(tombstone) <= maxTimestamp_s1
             * In other words, iterating in maxTimestamp order allow to do our mostRecentTombstone elimination
             * in one pass, and minimize the number of sstables for which we read a rowTombstone.
             */
            Collections.sort(view.sstables, SSTableReader.maxTimestampComparator);
            List<SSTableReader> skippedSSTables = null;
            long minTimestamp = Long.MAX_VALUE;
            int nonIntersectingSSTables = 0;

            for (SSTableReader sstable : view.sstables)
            {
                minTimestamp = Math.min(minTimestamp, sstable.getMinTimestamp());
                // if we've already seen a row tombstone with a timestamp greater
                // than the most recent update to this sstable, we can skip it
                if (sstable.getMaxTimestamp() < returnDeletionInfo.getTopLevelDeletion().markedForDeleteAt) {
                    //if (mtdb_trace)
                    //    logger.warn("MTDB: sstable={}", sstable);
                    break;
                } else {
                    //if (mtdb_trace)
                    //    logger.warn("MTDB: sstable={}", sstable);
                }

                if (!filter.shouldInclude(sstable))
                {
                    nonIntersectingSSTables++;
                    // sstable contains no tombstone if maxLocalDeletionTime == Integer.MAX_VALUE, so we can safely skip those entirely
                    if (sstable.getSSTableMetadata().maxLocalDeletionTime != Integer.MAX_VALUE)
                    {
                        if (skippedSSTables == null)
                            skippedSSTables = new ArrayList<>();
                        skippedSSTables.add(sstable);
                    }
                    continue;
                }

                sstable.incrementReadCount();
                OnDiskAtomIterator iter = filter.getSSTableColumnIterator(sstable);
                iterators.add(iter);

                if (mtdb_trace) {
                    MemSsTableAccessMon.Update(sstable);

                    // iter.getColumnFamily() == null means the sstable doesn't
                    // have the requested data. and probably by the bloom
                    // filter said so.
                    //logger.warn("MTDB: sstable {} read_meter_count={} false_positive={} true_positive={} iter.getColumnFamily()={}"
                    //        , sstable.descriptor.generation
                    //        , sstable.getReadMeter().count()
                    //        , sstable.getBloomFilterFalsePositiveCount()
                    //        , sstable.getBloomFilterTruePositiveCount()
                    //        , iter.getColumnFamily()
                    //        );
                }

                if (iter.getColumnFamily() != null)
                {
                    ColumnFamily cf = iter.getColumnFamily();
                    returnCF.delete(cf);
                    sstablesIterated++;
                }
            }

            int includedDueToTombstones = 0;
            // Check for row tombstone in the skipped sstables
            if (skippedSSTables != null)
            {
                for (SSTableReader sstable : skippedSSTables)
                {
                    if (sstable.getMaxTimestamp() <= minTimestamp)
                        continue;

                    sstable.incrementReadCount();
                    OnDiskAtomIterator iter = filter.getSSTableColumnIterator(sstable);
                    ColumnFamily cf = iter.getColumnFamily();
                    // we are only interested in row-level tombstones here, and only if markedForDeleteAt is larger than minTimestamp
                    if (cf != null && cf.deletionInfo().getTopLevelDeletion().markedForDeleteAt > minTimestamp)
                    {
                        includedDueToTombstones++;
                        iterators.add(iter);
                        returnCF.delete(cf.deletionInfo().getTopLevelDeletion());
                        sstablesIterated++;
                    }
                    else
                    {
                        FileUtils.closeQuietly(iter);
                    }
                }
            }

            if (Tracing.isTracing())
                Tracing.trace("Skipped {}/{} non-slice-intersecting sstables, included {} due to tombstones",
                              nonIntersectingSSTables, view.sstables.size(), includedDueToTombstones);

            // we need to distinguish between "there is no data at all for this row" (BF will let us rebuild that efficiently)
            // and "there used to be data, but it's gone now" (we should cache the empty CF so we don't need to rebuild that slower)
            if (iterators.isEmpty())
                return null;

            Tracing.trace("Merging data from memtables and {} sstables", sstablesIterated);
            filter.collateOnDiskAtom(returnCF, iterators, gcBefore);

            // Caller is responsible for final removeDeletedCF.  This is important for cacheRow to work correctly:
            return returnCF;
        }
        finally
        {
            for (Object iter : iterators)
                if (iter instanceof Closeable)
                    FileUtils.closeQuietly((Closeable) iter);
        }
    }

    public int getSstablesIterated()
    {
        return sstablesIterated;
    }
}
