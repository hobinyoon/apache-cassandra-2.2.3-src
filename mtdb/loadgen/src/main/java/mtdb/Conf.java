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
		accepts("dump", "Dump all WRss to a file")
			.withRequiredArg().ofType(Boolean.class);
		accepts("dumpfn", "Dump file name")
			.withRequiredArg().defaultsTo("");
	}};

	public static class Global {
		// LoadGen options
		boolean dump;
		String fn_dump;

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
					"simulated_time_in_year: %d\n"
					+ "simulation_time_in_min: %f\n"
					+ "writes: %d\n"
					+ "write_time_dist: %s\n"
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
					"avg_reads: %f\n"
					+ "num_reads_dist: %s\n"
					+ "read_time_dist: %s\n"
					, avg_reads
					, num_reads_dist
					, read_time_dist);
		}
	}

	public static Global global;
	public static PerObj per_obj;

	private static void _LoadYaml() throws IOException {
		InputStream input = new FileInputStream(new File("conf/loadgen.yaml"));
		Yaml yaml = new Yaml();
		Map root = (Map) yaml.load(input);
		//System.out.println(yaml.dump(root));
		//System.out.println(root.getClass().getName());

		global = new Global(root.get("global"));
		per_obj = new PerObj(root.get("per_obj"));
	}

	private static void _Dump() {
		StringBuilder sb = new StringBuilder(1000);
		sb.append("global:\n");
		sb.append(global.toString().replaceAll("(?m)^", "  "));
		sb.append("per_obj:\n");
		sb.append(per_obj.toString().replaceAll("(?m)^", "  "));
		System.out.println(sb);
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

		global.writes = (long) options.valueOf("writes");

		global.dump = (boolean) options.valueOf("dump");
		if (global.dump) {
			global.fn_dump = (String) options.valueOf("dumpfn");
			if (global.fn_dump.length() == 0) {
				System.out.println("  missing dumpfn\n");
				_PrintHelp();
				System.exit(1);
			}
		}
	}

	public static void Init()
		throws IOException, java.text.ParseException, InterruptedException {
		Init(null);
	}

	public static void Init(String[] args)
		throws IOException, java.text.ParseException, InterruptedException {
		try (Cons.MeasureTime _ = new Cons.MeasureTime("Conf.Init ...")) {
			_LoadYaml();
			_ParseCmdlnOptions(args);
			//_Dump();
		}
	}
}
