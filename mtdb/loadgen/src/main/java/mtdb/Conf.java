package mtdb;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.IOException;
import java.util.List;
import java.util.Map;

import joptsimple.OptionParser;
import joptsimple.OptionSet;

import org.yaml.snakeyaml.Yaml;


public class Conf
{
	// Command line options
	private static OptionParser _opt_parser = null;

	public static class Global {
		String fn_test_num_reads_per_obj = "";
		String fn_test_obj_ages = "";
		String fn_dump_wrs = "";

		double simulated_time_years;
		double simulation_time_mins;
		int writes;
		String write_time_dist;

		// Init with a YAML obj. Can be overwritten by command line options.
		Global(Object obj_) {
			Map obj = (Map) obj_;
			writes = Integer.parseInt(obj.get("writes").toString());
			write_time_dist = obj.get("write_time_dist").toString();
		}

		public void AddCassandraMutantsOptions(Object obj_) {
			Map obj = (Map) obj_;
			simulated_time_years = Double.parseDouble(obj.get("simulated_time_years").toString());
			simulation_time_mins = Double.parseDouble(obj.get("simulation_time_mins").toString());
		}

		@Override
		public String toString() {
			return String.format(
					"simulated_time_years: %.1f"
					+ "\nsimulation_time_in_min: %.1f"
					+ "\nwrites: %d"
					+ "\nwrite_time_dist: %s"
					, simulated_time_years
					, simulation_time_mins
					, writes
					, write_time_dist
					);
		}
	}

	public static class PerObj {
		double avg_reads;
		String num_reads_dist;
		String read_time_dist;
		int obj_size;

		PerObj(Object obj_) {
			Map obj = (Map) obj_;
			avg_reads = Double.parseDouble(obj.get("avg_reads").toString());
			num_reads_dist = obj.get("num_reads_dist").toString();
			read_time_dist = obj.get("read_time_dist").toString();
			obj_size = Integer.parseInt(obj.get("obj_size").toString());
		}

		@Override
		public String toString() {
			return String.format(
					"avg_reads: %f"
					+ "\nnum_reads_dist: %s"
					+ "\nread_time_dist: %s"
					+ "\nobj_size: %d"
					, avg_reads
					, num_reads_dist
					, read_time_dist
					, obj_size
					);
		}
	}

	public static class Db {
		boolean requests;
		int num_threads;

		Db(Object obj_) {
			Map obj = (Map) obj_;
			requests = Boolean.parseBoolean(obj.get("requests").toString());
			num_threads = Integer.parseInt(obj.get("num_threads").toString());
		}

		@Override
		public String toString() {
			return String.format(
					"requests: %s"
					+ "\nnum_threads: %d"
					, requests
					, num_threads
					);
		}
	}

	public static Global global;
	public static PerObj per_obj;
	public static Db db;

	private static void LoadYamls() throws IOException {
		LoadLoadgenYaml();
		LoadCassandraYaml();
	}

	private static void LoadLoadgenYaml() throws IOException {
		InputStream input = new FileInputStream(new File("conf/loadgen.yaml"));
		Yaml yaml = new Yaml();
		Map root = (Map) yaml.load(input);
		//System.out.println(yaml.dump(root));
		//System.out.println(root.getClass().getName());

		global = new Global(root.get("global"));
		per_obj = new PerObj(root.get("per_obj"));
		db = new Db(root.get("db"));
	}

	private static void LoadCassandraYaml() throws IOException {
		InputStream input = new FileInputStream(new File("../../conf/cassandra.yaml"));
		Yaml yaml = new Yaml();
		Map root = (Map) yaml.load(input);
		global.AddCassandraMutantsOptions(root.get("mutants_options"));
	}

	private static void _Dump() {
		StringBuilder sb = new StringBuilder(1000);
		sb.append("global:\n");
		sb.append(global.toString().replaceAll("(?m)^", "  "));
		sb.append("\nper_obj:\n");
		sb.append(per_obj.toString().replaceAll("(?m)^", "  "));
		sb.append("\ndb:\n");
		sb.append(db.toString().replaceAll("(?m)^", "  "));
		//System.out.println(sb);
		Cons.P(sb);
	}

	private static void _PrintHelp() throws IOException {
		System.out.println("Usage: LoadGen [<option>]*");
		_opt_parser.printHelpOn(System.out);
	}

	private static void _ParseCmdlnOptions(String[] args)
		throws IOException, java.text.ParseException, InterruptedException {
		if (args == null)
			return;

		_opt_parser = new OptionParser() {{
			accepts("help", "Show this help message");
			accepts("writes", "Number of writes")
				.withRequiredArg().ofType(Integer.class).defaultsTo(global.writes);
			accepts("test_num_reads_per_obj", "Test number of reads per obj. Specify a file name to dump data.")
				.withRequiredArg().ofType(String.class).defaultsTo(global.fn_test_num_reads_per_obj);
			accepts("test_obj_ages", "When a file name is specified, loadgen dumps all obj ages when accessed.")
				.withRequiredArg().ofType(String.class).defaultsTo(global.fn_test_obj_ages);
			accepts("dump_wr", "When a file name is specified, loadgen dumps all WRs to the file.")
				.withRequiredArg().ofType(String.class).defaultsTo(global.fn_dump_wrs);
			accepts("db", "Issue requests to the database server")
				.withRequiredArg().ofType(Boolean.class).defaultsTo(db.requests);
			accepts("db_threads", "Number of client threads that make requests to the database server")
				.withRequiredArg().ofType(Integer.class).defaultsTo(db.num_threads);
			accepts("obj_size", "Object size in bytes.")
				.withRequiredArg().ofType(Integer.class).defaultsTo(per_obj.obj_size);
		}};

		OptionSet options = _opt_parser.parse(args);
		if (options.has("help")) {
			_PrintHelp();
			System.exit(0);
		}
		List<?> nonop_args = options.nonOptionArguments();
		if (nonop_args.size() != 0) {
			_PrintHelp();
			System.exit(1);
		}

		global.writes = (int) options.valueOf("writes");
		if (global.writes <= 0)
			throw new RuntimeException("Unexpected global.writes=" + global.writes);

		global.fn_test_num_reads_per_obj = (String) options.valueOf("test_num_reads_per_obj");
		global.fn_test_obj_ages = (String) options.valueOf("test_obj_ages");
		global.fn_dump_wrs = (String) options.valueOf("dump_wr");
		db.requests = (boolean) options.valueOf("db");
		db.num_threads = (int) options.valueOf("db_threads");
		per_obj.obj_size = (int) options.valueOf("obj_size");
	}

	public static void Init(String[] args)
		throws IOException, java.text.ParseException, InterruptedException {
		try (Cons.MeasureTime _ = new Cons.MeasureTime("Conf.Init ...")) {
			LoadYamls();
			_ParseCmdlnOptions(args);
			_Dump();
		}
	}
}
