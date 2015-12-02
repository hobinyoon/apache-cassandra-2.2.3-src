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
	private static final OptionParser _opt_parser = new OptionParser() {{
		accepts("help", "Show this help message");
		accepts("writes", "Number of writes")
			.withRequiredArg().ofType(Long.class);
		accepts("test_num_reads_per_obj", "Test number of reads per obj. Specify a file name to dump data.")
			.withRequiredArg().defaultsTo("");
		accepts("test_obj_ages", "Test obj ages when accessed. Specify a file name to dump data.")
			.withRequiredArg().defaultsTo("");
		accepts("dump_wr", "Dump all WRs to a file. Specify a file name.")
			.withRequiredArg().defaultsTo("");
		accepts("db", "Issue requests to the database server.")
			.withRequiredArg();
		accepts("db_threads", "Number of client threads that make requests to the database server.")
			.withRequiredArg().ofType(Integer.class);
	}};

	public static class Global {
		String fn_test_num_reads_per_obj;
		String fn_test_obj_ages;
		String fn_dump_wrs;

		int simulated_time_in_year;
		double simulation_time_in_min;
		long writes;
		String write_time_dist;

		// Init with a YAML obj. Can be overwritten by command line options.
		Global(Object obj_) {
			Map obj = (Map) obj_;
			simulated_time_in_year = Integer.parseInt(obj.get("simulated_time_in_year").toString());
			simulation_time_in_min = Double.parseDouble(obj.get("simulation_time_in_min").toString());
			writes = Integer.parseInt(obj.get("writes").toString());
			write_time_dist = obj.get("write_time_dist").toString();
		}

		@Override
		public String toString() {
			return String.format(
					"simulated_time_in_year: %d"
					+ "\nsimulation_time_in_min: %f"
					+ "\nwrites: %d"
					+ "\nwrite_time_dist: %s"
					, simulated_time_in_year
					, simulation_time_in_min
					, writes
					, write_time_dist
					);
		}
	}

	public static class PerObj {
		double avg_reads;
		String num_reads_dist;
		String read_time_dist;

		PerObj(Object obj_) {
			Map obj = (Map) obj_;
			avg_reads = Double.parseDouble(obj.get("avg_reads").toString());
			num_reads_dist = obj.get("num_reads_dist").toString();
			read_time_dist = obj.get("read_time_dist").toString();
		}

		@Override
		public String toString() {
			return String.format(
					"avg_reads: %f"
					+ "\nnum_reads_dist: %s"
					+ "\nread_time_dist: %s"
					, avg_reads
					, num_reads_dist
					, read_time_dist);
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

	private static void _LoadYaml() throws IOException {
		InputStream input = new FileInputStream(new File("conf/loadgen.yaml"));
		Yaml yaml = new Yaml();
		Map root = (Map) yaml.load(input);
		//System.out.println(yaml.dump(root));
		//System.out.println(root.getClass().getName());

		global = new Global(root.get("global"));
		per_obj = new PerObj(root.get("per_obj"));
		db = new Db(root.get("db"));
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

		if (options.has("writes"))
			global.writes = (long) options.valueOf("writes");

		global.fn_test_num_reads_per_obj = (String) options.valueOf("test_num_reads_per_obj");
		global.fn_test_obj_ages = (String) options.valueOf("test_obj_ages");
		global.fn_dump_wrs = (String) options.valueOf("dump_wr");

		if (options.has("db"))
			db.requests = Boolean.parseBoolean((String) options.valueOf("db"));
		if (options.has("db_threads"))
			db.num_threads = (int) options.valueOf("db_threads");
	}

	public static void Init(String[] args)
		throws IOException, java.text.ParseException, InterruptedException {
		try (Cons.MeasureTime _ = new Cons.MeasureTime("Conf.Init ...")) {
			_LoadYaml();
			_ParseCmdlnOptions(args);
			_Dump();
		}
	}
}
