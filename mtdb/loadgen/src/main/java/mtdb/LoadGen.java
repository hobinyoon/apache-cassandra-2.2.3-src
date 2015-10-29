package mtdb;

import java.lang.InterruptedException;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.concurrent.ThreadLocalRandom;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class LoadGen
{
	public static void SimulatedTime() {
	}

	public static void GenWrites() throws InterruptedException {
		try (Cons.MeasureTime _ = new Cons.MeasureTime("GenWrites ...")) {
			// Simulated datetime begin and end
			LocalDateTime dt_b = LocalDateTime.of(2010, 1, 1, 0, 0);
			LocalDateTime dt_e = LocalDateTime.of(2010 + Conf.global.simulated_time_in_year, 1, 1, 0, 0);

			ZoneId zoneId = ZoneId.systemDefault();
			// Ignore sub-second resolution
			long epoch_sec_b = dt_b.atZone(zoneId).toEpochSecond();
			long epoch_sec_e = dt_e.atZone(zoneId).toEpochSecond();
			long epoch_sec_dur = epoch_sec_e - epoch_sec_b;

			Cons.P(String.format("Simulated datetime:\n"
						+ "  begin: %s %d\n"
						+ "  end:   %s %d\n"
						+ "  dur:   %d"
						, dt_b, epoch_sec_b
						, dt_e, epoch_sec_e
						, epoch_sec_dur
						));

			Cons.P(String.format("Write times (%s):", Conf.global.write_time_dist));
			if (Conf.global.write_time_dist.equals("Same")) {
				for (int i = 1; i <= Conf.global.writes; i ++) {
					long es = epoch_sec_b + epoch_sec_dur * i / Conf.global.writes;
					Cons.P(String.format("  %s %d",
								LocalDateTime.ofEpochSecond(es, 0, ZoneOffset.UTC),
								es));
				}
			} else if (Conf.global.write_time_dist.equals("Uniform")) {
				ThreadLocalRandom tlr = ThreadLocalRandom.current();
				List<Long> epoch_secs = new ArrayList(Conf.global.writes);
				for (int i = 1; i <= Conf.global.writes; i ++) {
					long es = tlr.nextLong(epoch_sec_b, epoch_sec_e + 1);
					epoch_secs.add(es);
				}
				Collections.sort(epoch_secs);
				for (long es: epoch_secs) {
					Cons.P(String.format("  %s %d",
								LocalDateTime.ofEpochSecond(es, 0, ZoneOffset.UTC),
								es));
				}
			}

			// TODO: primary keys. you can assign sequential numbers.
		}
	}

	public static void main(String[] args)
	{
		try {
			Conf.Load();

			GenWrites();

			// TODO: GenReads() online
		} catch (Exception e) {
			System.out.println("Exception: " + e);
		}
	}
}
