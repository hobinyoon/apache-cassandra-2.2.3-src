package org.apache.cassandra.mutants;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.apache.cassandra.config.DatabaseDescriptor;


public class SimTime {
    private static final Logger logger = LoggerFactory.getLogger(SimTime.class);
    private static double simulationOverSimulatedTime;
    private static double simulatedOverSimulationTime;

    // Should be initialized after DatabaseDescriptor class
    static {
        simulationOverSimulatedTime =
            (DatabaseDescriptor.getMutantsOptions().simulation_time_mins)
            / (DatabaseDescriptor.getMutantsOptions().simulated_time_years * 365.25 * 24 * 60);
        simulatedOverSimulationTime =
            (DatabaseDescriptor.getMutantsOptions().simulated_time_years * 365.25 * 24 * 60)
            / (DatabaseDescriptor.getMutantsOptions().simulation_time_mins);

        //logger.warn("MTDB: simulationOverSimulatedTime={} simulatedOverSimulationTime={}"
        //        , simulationOverSimulatedTime, simulatedOverSimulationTime);
	}

    public static long toSimulationTimeDurNs(long simulatedTimeDurNs) {
        return (long) (simulatedTimeDurNs * simulationOverSimulatedTime);
    }

    public static long toSimulatedTimeDurNs(long simulationTimeDurNs) {
        return (long) (simulationTimeDurNs * simulatedOverSimulationTime);
    }
}
