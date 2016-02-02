package org.apache.cassandra.config;

public class MutantsOptions
{
    public double simulated_time_years;
    public double simulation_time_mins;

    public int tablet_temperature_monitor_interval_simulation_time_ms;

    public String cold_storage_dir;

    public double tablet_coldness_monitor_time_window_simulated_time_days;
    public double tablet_coldness_threshold;

    public long tablet_access_stat_report_interval_simulation_time_ms;
}
