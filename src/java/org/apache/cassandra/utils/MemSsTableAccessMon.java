package org.apache.cassandra.utils;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.ConcurrentHashMap;
import java.util.Iterator;
import java.util.List;

import org.apache.cassandra.db.Memtable;
import org.apache.cassandra.db.ColumnFamily;
import org.apache.cassandra.io.sstable.Descriptor;
import org.apache.cassandra.io.sstable.format.SSTableReader;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MemSsTableAccessMon
{
    private static Map<Memtable, _MemTableAccCnt> _memTableAccCnt = new ConcurrentHashMap();
    private static Map<Descriptor, _SSTableAccCnt> _ssTableAccCnt = new ConcurrentHashMap();

    private static boolean _updatedSinceLastOutput = false;
    private static Thread _outThread = null;
    private static final Logger logger = LoggerFactory.getLogger(MemSsTableAccessMon.class);

    private static class _MemTableAccCnt {
        private AtomicLong accesses;
        private AtomicLong hits;
        private boolean discarded = false;
        private boolean loggedAfterDiscarded = false;

        public _MemTableAccCnt(boolean hit) {
            this.accesses = new AtomicLong(1);
            this.hits = new AtomicLong(hit ? 1 : 0);
        }

        public void Increment(boolean hit) {
            this.accesses.incrementAndGet();
            if (hit)
                this.hits.incrementAndGet();
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder(40);
            sb.append(accesses.get()).append(",").append(hits.get());
            return sb.toString();
        }
    }

    private static class _SSTableAccCnt {
        private SSTableReader _sstr;
        private long _bytesOnDisk = -1;
        private boolean discarded = false;
        private boolean loggedAfterDiscarded = false;

        public _SSTableAccCnt(SSTableReader sstr) {
            _sstr = sstr;
        }

        @Override
        public String toString() {
            if (_bytesOnDisk == -1)
                _bytesOnDisk = _sstr.bytesOnDisk();

            StringBuilder sb = new StringBuilder(40);
            // TODO MTDB: Update the plot script. The order has changed.
            sb.append(_bytesOnDisk)
                .append(",").append(_sstr.getReadMeter().count())
                .append(",").append(_sstr.getBloomFilterTruePositiveCount())
                .append(",").append(_sstr.getBloomFilterFalsePositiveCount())
                ;
            return sb.toString();
        }
    }

    static {
        _outThread = new Thread(new OutputThread());
        _outThread.start();
        // TODO MTDB: join() and clean up _outThread when Cassandra closes.
    }

    public static void Clear() {
        _memTableAccCnt.clear();
        _ssTableAccCnt.clear();
        logger.warn("MTDB: ClearAccStat");
    }

    public static void Update(Memtable m, ColumnFamily cf) {
        // There is a race condition here, but harmless.  It happens only when
        // m is not in the map yet, which is very rare.
        _MemTableAccCnt v = _memTableAccCnt.get(m);
        if (v != null) {
            v.Increment(cf != null);
        } else {
            _memTableAccCnt.put(m, new _MemTableAccCnt(cf != null));
        }
        _updatedSinceLastOutput = true;
    }


    public static void Update(SSTableReader r) {
        Descriptor key = r.descriptor;

        // The race condition (time of check and modify) that may overwrite the
        // first put() is harmless. It avoids an expensive locking.
        if (_ssTableAccCnt.get(key) == null)
            _ssTableAccCnt.put(key, new _SSTableAccCnt(r));

        _updatedSinceLastOutput = true;
    }

    // Discard a MemTable
    public static void Discard(Memtable m) {
        logger.warn("MTDB: MemtableDiscard {}", m);

        _MemTableAccCnt v = _memTableAccCnt.get(m);
        if (v == null) {
            // Can a memtable be discarded without being accessed at all? I'm
            // not sure, but let's not throw an exception.
            return;
        }
        v.discarded = true;

        _updatedSinceLastOutput = true;
    }

    // Delete a SSTable
    public static void Delete(Descriptor d) {
        logger.warn("MTDB: SstDeleted {}", d);

        _SSTableAccCnt v = _ssTableAccCnt.get(d);
        if (v == null) {
            // A SSTable can be deleted without having been accessed by
            // starting Cassandra, dropping an existing keyspace.
            return;
        }
        v.discarded = true;

        _updatedSinceLastOutput = true;
    }

    private static class OutputThread implements Runnable {
        public void run() {

            // Sort lexicographcally with Memtables go first
            class OutputComparator implements Comparator<String> {
                @Override
                public int compare(String s1, String s2) {
                    if (s1.startsWith("Memtable-")) {
                        if (s2.startsWith("Memtable-")) {
                            return s1.compareTo(s2);
                        } else {
                            return -1;
                        }
                    } else {
                        if (s2.startsWith("Memtable-")) {
                            return 1;
                        } else {
                            return s1.compareTo(s2);
                        }
                    }
                }
            }
            OutputComparator oc = new OutputComparator();

            try {
                while (true) {
                    // TODO MTDB: make it configurable
                    Thread.sleep(500);
                    // a non-strict but low-overhead serialization
                    if (! _updatedSinceLastOutput)
                        continue;
                    _updatedSinceLastOutput = false;

                    // Remove discarded MemTables after logging for the last time
                    for (Iterator it = _memTableAccCnt.entrySet().iterator(); it.hasNext(); ) {
                        Map.Entry pair = (Map.Entry) it.next();
                        _MemTableAccCnt v = (_MemTableAccCnt) pair.getValue();
                        if (v.loggedAfterDiscarded)
                            it.remove();
                    }
                    for (Iterator it = _memTableAccCnt.entrySet().iterator(); it.hasNext(); ) {
                        Map.Entry pair = (Map.Entry) it.next();
                        _MemTableAccCnt v = (_MemTableAccCnt) pair.getValue();
                        if (v.discarded)
                            v.loggedAfterDiscarded = true;
                    }

                    // Remove deleted SSTables in the same way
                    for (Iterator it = _ssTableAccCnt.entrySet().iterator(); it.hasNext(); ) {
                        Map.Entry pair = (Map.Entry) it.next();
                        _SSTableAccCnt v = (_SSTableAccCnt) pair.getValue();
                        if (v.loggedAfterDiscarded)
                            it.remove();
                    }
                    for (Iterator it = _ssTableAccCnt.entrySet().iterator(); it.hasNext(); ) {
                        Map.Entry pair = (Map.Entry) it.next();
                        _SSTableAccCnt v = (_SSTableAccCnt) pair.getValue();
                        if (v.discarded)
                            v.loggedAfterDiscarded = true;
                    }

                    List<String> outEntries = new ArrayList();
                    for (Iterator it = _memTableAccCnt.entrySet().iterator(); it.hasNext(); ) {
                        Map.Entry pair = (Map.Entry) it.next();
                        Memtable m = (Memtable) pair.getKey();
                        outEntries.add(String.format("%s-%s"
                                    , m.toString()
                                    , pair.getValue().toString()));
                    }

                    for (Iterator it = _ssTableAccCnt.entrySet().iterator(); it.hasNext(); ) {
                        Map.Entry pair = (Map.Entry) it.next();
                        Descriptor d = (Descriptor) pair.getKey();
                        outEntries.add(String.format("%02d:%s"
                                    //, d.cfname.substring(0, 2)
                                    , d.generation
                                    , pair.getValue().toString()));
                    }

                    if (outEntries.size() == 0)
                        continue;

                    Collections.sort(outEntries, oc);

                    StringBuilder sb = new StringBuilder(1000);
                    boolean first = true;
                    for (String i: outEntries) {
                        if (first) {
                            first = false;
                        } else {
                            sb.append(" ");
                        }
                        sb.append(i);
                    }

                    logger.warn("MTDB: TabletAccessStat {}", sb.toString());
                }
            } catch (InterruptedException e) {
                logger.warn("MTDB: {}", e);
            }
        }
    }
}
