package org.apache.cassandra.utils;

import java.util.ArrayList;
import java.util.Collections;
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

    private static long tsLastOutput = 0L;
    private static boolean updatedSinceLastOutput = false;
    private static Thread _outThread = null;
    private static final Logger logger = LoggerFactory.getLogger(MemSsTableAccessMon.class);

    private static class _MemTableAccCnt {
        private AtomicLong accesses;
        private AtomicLong hits;

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
        long read_cnt;
        long bf_tp_cnt;
        long bf_fp_cnt;
        // bf_negative can be calculated

        // TODO: Update the plot script. The order of tp and fp has changed.
        public _SSTableAccCnt(long read_cnt, long bf_tp_cnt, long bf_fp_cnt) {
            this.read_cnt = read_cnt;
            this.bf_tp_cnt = bf_tp_cnt;
            this.bf_fp_cnt = bf_fp_cnt;
        }

        public boolean equals(_SSTableAccCnt v) {
            if (this == v)
                return true;
            if (read_cnt != v.read_cnt)
                return false;
            if (bf_tp_cnt != v.bf_tp_cnt)
                return false;
            if (bf_fp_cnt != v.bf_fp_cnt)
                return false;
            return true;
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder(40);
            sb.append(read_cnt).append(",").append(bf_tp_cnt).append(",").append(bf_fp_cnt);
            return sb.toString();
        }
    }

    static {
        _outThread = new Thread(new OutputThread());
        _outThread.start();
        // TODO: join() and clean up _outThread when Cassandra closes.
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
        updatedSinceLastOutput = true;
    }


    public static void Update(SSTableReader r) {
        //long key = r.descriptor.generation;
        Descriptor key = r.descriptor;
        _SSTableAccCnt value = new _SSTableAccCnt(r.getReadMeter().count()
                , r.getBloomFilterTruePositiveCount()
                , r.getBloomFilterFalsePositiveCount());

        // The race condition (time of check and modify. causes multiple
        // updates) here is harmless and better for performance.
        if (! _ssTableAccCnt.containsKey(key)) {
            _ssTableAccCnt.put(key, value);
            updatedSinceLastOutput = true;
        } else {
            if (value.equals(_ssTableAccCnt.get(key))) {
                // No changes. Do nothing.
            } else {
                _ssTableAccCnt.put(key, value);
                updatedSinceLastOutput = true;
            }
        }
    }


    public static void Discard(Memtable m) {
        logger.warn("MTDB: MemtableDiscard {}", m);
        // TODO: implement
    }

    // TODO: may want to have a SSTable removed event.

    private static class OutputThread implements Runnable {
        public void run() {
            try {
                while (true) {
                    // TODO: make it configurable
                    Thread.sleep(500);
                    // a non-strict but low-overhead serialization
                    if (! updatedSinceLastOutput)
                        continue;
                    updatedSinceLastOutput = false;

                    List<String> outEntries = new ArrayList();
                    for (Iterator it = _memTableAccCnt.entrySet().iterator(); it.hasNext(); ) {
                        Map.Entry pair = (Map.Entry) it.next();
                        Memtable m = (Memtable) pair.getKey();
                        outEntries.add(String.format("%s-%s"
                                    // TODO: more compact?
                                    , m.toString()
                                    , pair.getValue().toString()));
                    }

                    for (Iterator it = _ssTableAccCnt.entrySet().iterator(); it.hasNext(); ) {
                        Map.Entry pair = (Map.Entry) it.next();
                        Descriptor d = (Descriptor) pair.getKey();
                        outEntries.add(String.format("%s-%02d:%s"
                                    , d.cfname.substring(0, 2)
                                    , d.generation
                                    , pair.getValue().toString()));
                    }

                    // A SSTable removal can be done somewhere around here. It
                    // can't be run concurrently with the above loop.

                    if (outEntries.size() == 0)
                        continue;

                    // TODO: let memtable accesses go first
                    Collections.sort(outEntries);

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
