import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.PrintStream;
import java.text.SimpleDateFormat;
import java.util.Date;

public class ConvertTsToDatetime
{
	private static SimpleDateFormat sdfDate = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");

	private static String toDateTime(long ts) {
		Date now = new java.util.Date((long)(ts/1000.0));
		return sdfDate.format(now);
	}

	public static void main(String args[]) {
		try {
			String fn = "../data";
			try (BufferedReader br = new BufferedReader(new FileReader(fn))) {
				String line;
				while ((line = br.readLine()) != null) {
					//System.out.printf("[%s]\n", line);
					String[] tokens = line.split(" ");
					if (tokens.length != 6)
						throw new RuntimeException(String.format("Unexpected format [%s]", line));
					int sstgen = Integer.parseInt(tokens[1]);
					long ts_max = Long.parseLong(tokens[3]);
					long ts_min = Long.parseLong(tokens[5]);
					System.out.printf("%2d %d %d %s %s\n"
							, sstgen
							, ts_max , ts_min
							, toDateTime(ts_max) , toDateTime(ts_min)
							);
				}
			}
		} catch (Exception e) {
			e.printStackTrace(new PrintStream(System.out));
		}
	}
}
