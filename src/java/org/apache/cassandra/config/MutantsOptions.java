package org.apache.cassandra.config;

public class MutantsOptions
{
    public double simulated_time_years;
    public double simulation_time_mins;

    public int tablet_temperature_monitor_interval_ms;

    public String cold_storage_dir;

    // Number of need-to-read-dfiles per day. In simulated time.
    public double tablet_coldness_migration_threshold;

    public double min_tablet_age_days_for_migration_to_cold_storage;

    // Tablet access stat report interval. Plotting tools use this report
    public long tablet_access_stat_report_interval_ms;
}
