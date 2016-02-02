package org.apache.cassandra.mutants;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.apache.cassandra.config.DatabaseDescriptor;


public class SimTime {
    private static final Logger logger = LoggerFactory.getLogger(SimTime.class);
    private static double simulatedOverSimulationTime;

    // Should be initialized after DatabaseDescriptor class
    static {
        simulatedOverSimulationTime =
            (DatabaseDescriptor.getMutantsOptions().simulated_time_years * 365.25 * 24 * 60)
            / (DatabaseDescriptor.getMutantsOptions().simulation_time_mins);
        logger.warn("MTDB: simulatedOverSimulationTime={}", simulatedOverSimulationTime);
	}

    public static long toSimulationTimeDurNs(long simulatedTimeDurNs) {
        //return simulatedTimeDurNs
        //    * (DatabaseDescriptor.getMutantsOptions().simulated_time_time_years * 365.25 * 24 * 60)
        //    / (DatabaseDescriptor.getMutantsOptions().simulation_time_mins);
        return (long) (simulatedTimeDurNs * simulatedOverSimulationTime);
    }
}
