package org.apache.cassandra.config;

public class MutantsLoadgenOptions
{
    public Global global = new Global();
    public PerObj per_obj = new PerObj();
    public DB db = new DB();
}

class Global {
    public long num_writes_per_simulation_time_mins;
    public int progress_report_interval_ms;
    public String write_time_dist;
}

class PerObj {
    public double avg_reads;
    public String num_reads_dist;
    public String read_time_dist;
    public long obj_size;
}

class DB {
    public boolean requests;
    public long num_threads;
}
