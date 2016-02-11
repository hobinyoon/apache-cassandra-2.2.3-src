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


// Load YAML first. Overwritten later by command line options when specified.
public class Conf
{
	public static class MutantsOptions {
		// Keep underscore notations for the future when parsing is automated
		double simulated_time_years;
		double simulation_time_mins;

		MutantsOptions(Object obj) {
			Map o = (Map) obj;
			simulated_time_years = Double.parseDouble(o.get("simulated_time_years").toString());
			simulation_time_mins = Double.parseDouble(o.get("simulation_time_mins").toString());
		}

		@Override
		public String toString() {
			return String.format(
					"mutants_options:"
					+ "\n  simulated_time_years: %.1f"
					+ "\n  simulation_time_in_min: %.1f"
					, simulated_time_years
					, simulation_time_mins
					);
		}
	}

	public static class MutantsLoadgenOptions {
		public final Global global;
		public final PerObj per_obj;
		public final Db db;

		MutantsLoadgenOptions(Object obj) {
			Map o = (Map) obj;
			global = new Global((Map) o.get("global"));
			per_obj = new PerObj((Map) o.get("per_obj"));
			db = new Db((Map) o.get("db"));
		}

		@Override
		public String toString() {
			return String.format(
					"mutants_loadgen_options:"
					+ "\n%s"
					+ "\n%s"
					+ "\n%s"
					, global.toString().replaceAll("(?m)^", "  ")
					, per_obj.toString().replaceAll("(?m)^", "  ")
					, db.toString().replaceAll("(?m)^", "  ")
					);
		}

		public class Global {
			// For test plotting
			String fn_test_num_reads_per_obj = "";
			String fn_test_obj_ages = "";
			String fn_dump_wrs = "";

			String server_addr = "";
			double num_writes_per_simulation_time_mins;
			int progress_report_interval_ms;
			String write_time_dist;

			Global(Map m) {
				num_writes_per_simulation_time_mins = Double.parseDouble(m.get("num_writes_per_simulation_time_mins").toString());
				progress_report_interval_ms = Integer.parseInt(m.get("progress_report_interval_ms").toString());
				write_time_dist = m.get("write_time_dist").toString();
			}

			@Override
			public String toString() {
				return String.format(
						"global:"
						+ "\n  server_addr: %s"
						+ "\n  num_writes_per_simulation_time_mins: %.1f"
						+ "\n  progress_report_interval_ms: %d"
						+ "\n  write_time_dist: %s"
						, server_addr
						, num_writes_per_simulation_time_mins
						, progress_report_interval_ms
						, write_time_dist
						);
			}
		}

		public class PerObj {
			double avg_reads;
			String num_reads_dist;
			String read_time_dist;
			int obj_size;

			PerObj(Map m) {
				avg_reads = Double.parseDouble(m.get("avg_reads").toString());
				num_reads_dist = m.get("num_reads_dist").toString();
				read_time_dist = m.get("read_time_dist").toString();
				obj_size = Integer.parseInt(m.get("obj_size").toString());
			}

			@Override
				public String toString() {
					return String.format(
							"per_obj:"
							+ "\n  avg_reads: %.1f"
							+ "\n  num_reads_dist: %s"
							+ "\n  read_time_dist: %s"
							+ "\n  obj_size: %d"
							, avg_reads
							, num_reads_dist
							, read_time_dist
							, obj_size
							);
				}
		}

		public class Db {
			boolean requests;
			int num_threads;

			Db(Map m) {
				requests = Boolean.parseBoolean(m.get("requests").toString());
				num_threads = Integer.parseInt(m.get("num_threads").toString());
			}

			@Override
				public String toString() {
					return String.format(
							"db:"
							+ "\n  requests: %s"
							+ "\n  num_threads: %d"
							, requests
							, num_threads
							);
				}
		}
	}

	public static MutantsOptions mutantsOptions = null;
	public static MutantsLoadgenOptions mutantsLoadgenOptions = null;

	// Command line options
	private static OptionParser _opt_parser = null;

	private static void LoadYamls() throws IOException {
		Map root = (Map) ((new Yaml()).load(new FileInputStream(new File("../../conf/cassandra.yaml"))));

		mutantsOptions = new MutantsOptions(root.get("mutants_options"));
		mutantsLoadgenOptions = new MutantsLoadgenOptions(root.get("mutants_loadgen_options"));
	}

	public static int NumWrites() {
		return (int) (mutantsOptions.simulation_time_mins * mutantsLoadgenOptions.global.num_writes_per_simulation_time_mins);
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
			accepts("num_writes_per_simulation_time_mins", "Number of writes per simulation time in munites")
				.withRequiredArg().ofType(Double.class).defaultsTo(mutantsLoadgenOptions.global.num_writes_per_simulation_time_mins);
			accepts("test_num_reads_per_obj", "Test number of reads per obj. Specify a file name to dump data.")
				.withRequiredArg().ofType(String.class).defaultsTo(mutantsLoadgenOptions.global.fn_test_num_reads_per_obj);
			accepts("test_obj_ages", "When a file name is specified, loadgen dumps all obj ages when accessed.")
				.withRequiredArg().ofType(String.class).defaultsTo(mutantsLoadgenOptions.global.fn_test_obj_ages);
			accepts("dump_wr", "When a file name is specified, loadgen dumps all WRs to the file.")
				.withRequiredArg().ofType(String.class).defaultsTo(mutantsLoadgenOptions.global.fn_dump_wrs);
			accepts("db", "Issue requests to the database server")
				.withRequiredArg().ofType(Boolean.class).defaultsTo(mutantsLoadgenOptions.db.requests);
			accepts("db_threads", "Number of client threads that make requests to the database server")
				.withRequiredArg().ofType(Integer.class).defaultsTo(mutantsLoadgenOptions.db.num_threads);
			accepts("obj_size", "Object size in bytes.")
				.withRequiredArg().ofType(Integer.class).defaultsTo(mutantsLoadgenOptions.per_obj.obj_size);
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

		mutantsLoadgenOptions.global.num_writes_per_simulation_time_mins
			= (double) options.valueOf("num_writes_per_simulation_time_mins");
		if (mutantsLoadgenOptions.global.num_writes_per_simulation_time_mins <= 0)
			throw new RuntimeException("Unexpected global.num_writes_per_simulation_time_mins="
					+ mutantsLoadgenOptions.global.num_writes_per_simulation_time_mins);

		mutantsLoadgenOptions.global.fn_test_num_reads_per_obj = (String) options.valueOf("test_num_reads_per_obj");
		mutantsLoadgenOptions.global.fn_test_obj_ages = (String) options.valueOf("test_obj_ages");
		mutantsLoadgenOptions.global.fn_dump_wrs = (String) options.valueOf("dump_wr");

		String server_addr = System.getenv("CASSANDRA_SERVER_ADDR");
		if (server_addr == null)
			throw new RuntimeException("CASSANDRA_SERVER_ADDR is not set");
		mutantsLoadgenOptions.global.server_addr = server_addr;

		mutantsLoadgenOptions.db.requests = (boolean) options.valueOf("db");
		mutantsLoadgenOptions.db.num_threads = (int) options.valueOf("db_threads");
		mutantsLoadgenOptions.per_obj.obj_size = (int) options.valueOf("obj_size");
	}

	public static void Init(String[] args)
		throws IOException, java.text.ParseException, InterruptedException {
		try (Cons.MeasureTime _ = new Cons.MeasureTime("Conf.Init ...")) {
			LoadYamls();
			_ParseCmdlnOptions(args);
			Cons.P(mutantsOptions);
			Cons.P(mutantsLoadgenOptions);
		}
	}
}
