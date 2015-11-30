package mtdb;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.IOException;
import java.util.List;
import java.util.Map;

import joptsimple.OptionParser;
import joptsimple.OptionSet;


public class Conf
{
	// Command line options
	private static final OptionParser _opt_parser = new OptionParser() {{
		accepts("help", "Show this help message");
		accepts("readers", "Number of reader threads")
			.withRequiredArg().ofType(Long.class);
		accepts("max_reads", "Max read requests")
			.withRequiredArg().ofType(Long.class);
	}};

	public static long num_readers = 100;
	public static long max_reads = -1;

	private static void _Dump() {
		StringBuilder sb = new StringBuilder(1000);
		sb.append("num_readers: ").append(num_readers);
		sb.append("max_reads: ").append(max_reads);
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

		if (options.has("readers"))
			num_readers = (long) options.valueOf("readers");
		if (options.has("max_reads"))
			max_reads = (long) options.valueOf("max_reads");
	}

	public static void Init(String[] args)
		throws IOException, java.text.ParseException, InterruptedException {
		try (Cons.MeasureTime _ = new Cons.MeasureTime("Conf.Init ...")) {
			_ParseCmdlnOptions(args);
			//_Dump();
		}
	}
}
