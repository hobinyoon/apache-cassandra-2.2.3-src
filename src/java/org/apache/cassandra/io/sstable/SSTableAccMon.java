package org.apache.cassandra.io.sstable;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.Iterator;

import org.apache.cassandra.io.sstable.format.SSTableReader;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SSTableAccMon
{
    // Map<sstable_generation, value>
    private static Map<Long, Value> map = new ConcurrentHashMap();

    private static long tsLastOutput = 0L;
    private static boolean updatedSinceLastOutput = false;
    private static Thread outThread = null;
    private static final Logger logger = LoggerFactory.getLogger(SSTableAccMon.class);

    private static class Value {
        long read_cnt;
        long bf_fp_cnt;
        long bf_tp_cnt;
        // bf_negative can be calculated

        public Value(long read_cnt_, long bf_fp_cnt_, long bf_tp_cnt_) {
            read_cnt = read_cnt_;
            bf_fp_cnt = bf_fp_cnt_;
            bf_tp_cnt = bf_tp_cnt_;
        }

        public boolean equals(Value v) {
            if (read_cnt != v.read_cnt)
                return false;
            if (bf_fp_cnt != v.bf_fp_cnt)
                return false;
            if (bf_tp_cnt != v.bf_tp_cnt)
                return false;
            return true;
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder(40);
            sb.append(read_cnt).append(",").append(bf_fp_cnt).append(",").append(bf_tp_cnt);
            return sb.toString();
        }
    }

    static {
        outThread = new Thread(new MessageLoop());
        outThread.start();
        // TODO: Clean up outThread when Cassandra closes. Do you need a join?
    }

    public static void Update(SSTableReader r) {
        long key = r.descriptor.generation;
        Value value = new Value(r.getReadMeter().count()
                , r.getBloomFilterFalsePositiveCount()
                , r.getBloomFilterTruePositiveCount());

        if (! map.containsKey(key)) {
            map.put(key, value);
            updatedSinceLastOutput = true;
        } else {
            if (value.equals(map.get(key))) {
                // No changes. Do nothing.
            } else {
                map.put(key, value);
                updatedSinceLastOutput = true;
            }
        }
    }

    private static class MessageLoop implements Runnable {
        public void run() {
            try {
                while (true) {
                    Thread.sleep(1000);
                    // a practical (not a strict) serialization for low contention
                    if (! updatedSinceLastOutput)
                        continue;
                    updatedSinceLastOutput = false;

                    StringBuilder sb = new StringBuilder(1000);
                    Iterator it = map.entrySet().iterator();
                    while (it.hasNext()) {
                        Map.Entry pair = (Map.Entry) it.next();

                        if (sb.length() > 0)
                            sb.append(" ");
                        sb.append(pair.getKey()).append(":").append(pair.getValue().toString());
                        // TODO: remove when a SSTable is removed
                        //it.remove(); // avoids a ConcurrentModificationException
                    }

                    if (sb.length() > 0)
                        logger.warn("MTDB: {}", sb.toString());
                }
            } catch (InterruptedException e) {
                logger.warn("MTDB: {}", e);
            }
        }
    }
}
