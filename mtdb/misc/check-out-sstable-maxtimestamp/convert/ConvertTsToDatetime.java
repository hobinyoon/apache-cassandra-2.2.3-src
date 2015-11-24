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
		String strDate = sdfDate.format(now);
		return strDate;
	}

	public static void main(String args[]) {
		try {
			String fn = "../data";
			try (BufferedReader br = new BufferedReader(new FileReader(fn))) {
				String line;
				while ((line = br.readLine()) != null) {
					//System.out.printf("[%s]\n", line);
					String[] tokens = line.split(" ");
					if (tokens.length != 4)
						throw new RuntimeException(String.format("Unexpected format [%s]", line));
					int sstgen = Integer.parseInt(tokens[1]);
					long ts = Long.parseLong(tokens[3]);
					System.out.printf("%2d %d %s\n", sstgen, ts, toDateTime(ts));
				}
			}
		} catch (Exception e) {
			e.printStackTrace(new PrintStream(System.out));
		}
	}
}
