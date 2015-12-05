package org.apache.cassandra.io.sstable;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.Iterator;
import java.util.List;

import org.apache.cassandra.io.sstable.format.SSTableReader;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SSTableAccMon
{
    private static Map<Descriptor, Value> _map = new ConcurrentHashMap();

    private static long tsLastOutput = 0L;
    private static boolean updatedSinceLastOutput = false;
    private static Thread _outThread = null;
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
        _outThread = new Thread(new OutputThread());
        _outThread.start();
        // TODO: join() and clean up _outThread when Cassandra closes.
    }

    public static void Update(SSTableReader r) {
        //long key = r.descriptor.generation;
        Descriptor key = r.descriptor;
        Value value = new Value(r.getReadMeter().count()
                , r.getBloomFilterFalsePositiveCount()
                , r.getBloomFilterTruePositiveCount());

        if (! _map.containsKey(key)) {
            _map.put(key, value);
            updatedSinceLastOutput = true;
        } else {
            if (value.equals(_map.get(key))) {
                // No changes. Do nothing.
            } else {
                _map.put(key, value);
                updatedSinceLastOutput = true;
            }
        }
    }

    private static class OutputThread implements Runnable {
        public void run() {
            try {
                while (true) {
                    Thread.sleep(1000);
                    // a practical (not a strict) serialization for a low overhead
                    if (! updatedSinceLastOutput)
                        continue;
                    updatedSinceLastOutput = false;

                    List<String> items = new ArrayList();
                    Iterator it = _map.entrySet().iterator();
                    while (it.hasNext()) {
                        Map.Entry pair = (Map.Entry) it.next();
                        Descriptor d = (Descriptor) pair.getKey();
                        items.add(String.format("%s-%02d:%s"
                                , d.cfname.substring(0, 2)
                                , d.generation
                                , pair.getValue().toString()));
                        // TODO: remove when a SSTable is removed
                        //it.remove(); // avoids a ConcurrentModificationException
                    }

                    if (items.size() == 0)
                        continue;
                    Collections.sort(items);

                    StringBuilder sb = new StringBuilder(1000);
                    boolean first = true;
                    for (String i: items) {
                        if (first) {
                            first = false;
                        } else {
                            sb.append(" ");
                        }
                        sb.append(i);
                    }

                    logger.warn("MTDB: {}", sb.toString());
                }
            } catch (InterruptedException e) {
                logger.warn("MTDB: {}", e);
            }
        }
    }
}
