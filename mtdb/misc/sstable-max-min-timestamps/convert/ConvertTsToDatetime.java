import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.text.SimpleDateFormat;
import java.util.Date;

public class ConvertTsToDatetime
{
	private static SimpleDateFormat sdfDate = new SimpleDateFormat("yyyy-MM-dd-HH:mm:ss.SSS");

	private static String fnIn = null;
	private static String fnOut = null;

	private static String toDateTime(long ts) {
		Date now = new java.util.Date((long)(ts/1000.0));
		return sdfDate.format(now);
	}

	public static void main(String args[]) {
		try {
			if (args.length != 2) {
				System.out.printf("Usage: ConvertTsToDatetime fnIn fnOut\n");
				System.exit(1);
			}

			fnIn = args[0];
			fnOut = args[1];

			try (BufferedReader brIn = new BufferedReader(new FileReader(fnIn))) {
				try (PrintWriter pw = new PrintWriter(fnOut)) {
					pw.printf("# sst_gen ts_min ts_max\n");
					String line;
					while ((line = brIn.readLine()) != null) {
						//pw.printf("[%s]\n", line);
						String[] tokens = line.split(" ");
						if (tokens.length != 6)
							throw new RuntimeException(String.format("Unexpected format [%s]", line));
						int sstgen = Integer.parseInt(tokens[1]);
						long ts_max = Long.parseLong(tokens[3]);
						long ts_min = Long.parseLong(tokens[5]);
						pw.printf("%2d %s %s %6d\n"
								, sstgen
								, toDateTime(ts_min), toDateTime(ts_max)
								, ts_max - ts_min
								);
					}
				}
			}
			System.out.printf("Created file %s %d\n"
					, fnOut
					, (new File(fnOut)).length());
		} catch (Exception e) {
			e.printStackTrace(new PrintStream(System.out));
		}
	}
}
