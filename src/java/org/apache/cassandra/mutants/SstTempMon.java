package org.apache.cassandra.mutants;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.ConcurrentHashMap;
import java.util.LinkedList;
import java.util.Map;
import java.util.Queue;

import org.apache.cassandra.config.DatabaseDescriptor;
import org.apache.cassandra.io.sstable.format.SSTableReader;
import org.apache.cassandra.mutants.MemSsTableAccessMon;
import org.apache.cassandra.mutants.SimTime;


public class SstTempMon {
    private static final Logger logger = LoggerFactory.getLogger(SstTempMon.class);

    private static Map<SSTableReader, Monitor> monitors = new ConcurrentHashMap();

    // Called by DateTieredCompactionStrategy.addSSTable(SSTableReader
    // sstable). Seems like it is called at most once per sstable.
    public static void Add(SSTableReader sstr) {
        if (monitors.containsKey(sstr)) {
            throw new RuntimeException(String.format("Unexpected: SSTableReader for %d is already in the map"
                        , sstr.descriptor.generation));
        }
        monitors.put(sstr, new Monitor(sstr));
    }

    // It is called multiple times for a sstable, but harmless.
    public static void Remove(SSTableReader sstr) {
        Monitor m = monitors.remove(sstr);
        if (m != null) {
            m.Stop();
        }
    }

    private static class Monitor {
        private MonitorRunnable _tmr;
        private Thread _thread;

        // Start a temperature monitor thread. The initial thread name is
        // attached to make sure that there is only one instance per
        // SSTableReader instance.
        Monitor(SSTableReader sstr) {
            _tmr = new MonitorRunnable(sstr);
            _thread = new Thread(_tmr);
            _thread.setName(String.format("SstTempMon-%d-%s",
                        sstr.descriptor.generation, _thread.getName()));
            _thread.start();
        }

        // Stop the temperature monitor thread and join
        public void Stop() {
            if (_tmr != null)
                _tmr.Stop();
            try {
                if (_thread != null) {
                    _thread.join();
                    _thread = null;
                }
            } catch (InterruptedException e) {
                logger.warn("MTDB: InterruptedException {}", e);
            }
            _tmr = null;
        }
    }

    private static class MonitorRunnable implements Runnable {
        private static final long temperatureCheckIntervalMs;

        // It is in fact when a tablet becomes available for reading
        private final long _tabletCreationTimeNs;
        private final SSTableReader _sstr;
        private final Object _sleepLock = new Object();
        private volatile boolean _stopRequested = false;

        static {
            temperatureCheckIntervalMs = DatabaseDescriptor.getMutantsOptions().tablet_temperature_monitor_interval_simulation_time_ms;

            logger.warn("MTDB: temperatureCheckIntervalMs={} in simulated time days={}"
                    , temperatureCheckIntervalMs
                    , (SimTime.toSimulatedTimeDurNs(temperatureCheckIntervalMs * 1000000) / (24.0 * 3600 * 1000000000))
                    );
        }

        MonitorRunnable(SSTableReader sstr) {
            _tabletCreationTimeNs = System.nanoTime();
            _sstr = sstr;
        }

        void Stop() {
            synchronized (_sleepLock) {
                //logger.warn("MTDB: gen={} stop requested", _sstr.descriptor.generation);
                _stopRequested = true;
                _sleepLock.notify();
            }
        }

        // A sliding time window that monitors the number of
        // need-to-access-dfiles. This doesn't need to be multi-threaded.
        private static class AccessQueue {
            private static final long coldnessMonitorTimeWindowSimulationNs;
            private static final double coldnessThreshold;
            private static final double dayOverTimeWindowDays;

            static {
                double timeWindowSimulatedDays = DatabaseDescriptor.getMutantsOptions().tablet_coldness_monitor_time_window_simulated_time_days;
                coldnessMonitorTimeWindowSimulationNs =
                    SimTime.toSimulationTimeDurNs((long) (timeWindowSimulatedDays * 24.0 * 3600 * 1000000000));
                coldnessThreshold = DatabaseDescriptor.getMutantsOptions().tablet_coldness_threshold;
                dayOverTimeWindowDays = 1.0 / timeWindowSimulatedDays;
            }

            private class Element {
                // Simulation time
                private long timeNs;
                private long numAccesses;

                public Element(long timeNs, long numAccesses) {
                    this.timeNs = timeNs;
                    this.numAccesses = numAccesses;
                }
            }

            private long tabletCreationTimeNs;
            private Queue<Element> q;
            private long numAccessesInQ;

            public AccessQueue(long tabletCreationTimeNs) {
                this.tabletCreationTimeNs = tabletCreationTimeNs;
                q = new LinkedList();
                numAccessesInQ = 0;
            }

            public void DeqEnq(long curNs, long numAccesses) {
                // Delete expired elements
                while (true) {
                    Element e = q.peek();
                    if (e == null)
                        break;
                    long accessTimeAgeNs = curNs - e.timeNs;
                    if (accessTimeAgeNs > coldnessMonitorTimeWindowSimulationNs) {
                        numAccessesInQ -= e.numAccesses;
                        q.remove();
                    } else {
                        break;
                    }
                }

                // Add the new element
                if (numAccesses > 0) {
                    q.add(new Element(curNs, numAccesses));
                    numAccessesInQ += numAccesses;
                }
            }

            public boolean BelowColdnessThreshold(long curNano) {
                long monitorDurNs = curNano - tabletCreationTimeNs;
                if (monitorDurNs < coldnessMonitorTimeWindowSimulationNs) {
                    //logger.warn("MTDB: Not enough time has passed. monitorDurNs={}", monitorDurNs);
                    return false;
                }

                //double numAccessesPerDay = numAccessesInQ
                //    * SimTime.toSimulationTimeDurNs(24.0 * 3600 * 1000000000)
                //    / coldnessMonitorTimeWindowSimulationNs;
                double numAccessesPerDay = numAccessesInQ * dayOverTimeWindowDays;
                //logger.warn("MTDB: TempMon numAccessesPerDay={}", numAccessesPerDay);
                if (numAccessesPerDay < coldnessThreshold) {
                    return true;
                } else {
                    return false;
                }

            }
        }

        public void run() {
            logger.warn("MTDB: TempMon Start {}", _sstr.descriptor.generation);
            long prevNnrd = -1;
            long prevNano = -1;
            AccessQueue q = new AccessQueue(_tabletCreationTimeNs);

            while (! _stopRequested) {
                synchronized (_sleepLock) {
                    try {
                        _sleepLock.wait(temperatureCheckIntervalMs);
                    } catch(InterruptedException e) {
                    }
                }
                if (_stopRequested)
                    break;

                long curNano = System.nanoTime();
                // Number of need-to-read-datafiles
                long nnrd = MemSsTableAccessMon.GetNumSstNeedToReadDataFile(_sstr);

                if (prevNnrd == -1 || prevNano == -1) {
                    prevNnrd = nnrd;
                    prevNano = curNano;
                    continue;
                }

                q.DeqEnq(curNano, nnrd - prevNnrd);
                if (q.BelowColdnessThreshold(curNano) == true) {
                    logger.warn("MTDB: TempMon TabletBecomeCold {}. Implement migration!", _sstr.descriptor.generation);
                    // TODO: Stop monitoring the temperature after this.
                    // Tablet only age. No anti-aging.
                    break;
                }

                prevNnrd = nnrd;
                prevNano = curNano;
            }

            logger.warn("MTDB: TempMon Stop {}", _sstr.descriptor.generation);
        }
    }
}
