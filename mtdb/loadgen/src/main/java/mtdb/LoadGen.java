package mtdb;

import java.io.FileNotFoundException;
import java.io.PrintWriter;
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
	// Operations to an object
	public static class WRs implements Comparable<WRs> {
		long key;	// primary key of the record
		static long global_key = 0;
		long w_epoch_sec;
		List<Long> r_epoch_sec;

		WRs(long w_epoch_sec_) {
			key = global_key ++;
			w_epoch_sec = w_epoch_sec_;

			_PopulateRs();
		}

		void _PopulateRs() {
			// Populate r_epoch_sec
			// TODO: populate in advance? or online?
			long num_reads = NumReadsPerObj.GetNext();
			//Cons.P(String.format("num_reads=%d", num_reads));
			r_epoch_sec = new ArrayList((int)num_reads);
			for (long i = 0; i < num_reads; i ++)
				r_epoch_sec.add(w_epoch_sec + ReadTimes.GetNext());
			Collections.sort(r_epoch_sec);
		}

		@Override
		public int compareTo(WRs r) {
			return (int)(w_epoch_sec - r.w_epoch_sec);
		}

		@Override
		public String toString() {
			StringBuilder sb = new StringBuilder(1000);
			sb.append(key);
			sb.append(" ");
			sb.append(w_epoch_sec);
			sb.append("\n");
			for (long r: r_epoch_sec) {
				sb.append("  ");
				sb.append(r);
				sb.append("\n");
			}
			return sb.toString();
			//return String.format("%d %d %s",
			//		key,
			//		w_epoch_sec,
			//		LocalDateTime.ofEpochSecond(w_epoch_sec, 0, ZoneOffset.UTC));
		}

		public String toStringForPlot() {
			StringBuilder sb = new StringBuilder(1000);
			sb.append(key);
			sb.append(" W ");
			sb.append(w_epoch_sec);
			for (long r: r_epoch_sec) {
				sb.append("\n");
				sb.append(key);
				sb.append(" R ");
				sb.append(r);
			}
			return sb.toString();
		}
	}

	// TODO: is List ok? do you need a queue?
	static List<WRs> _WRs;

	public static void GenWRs() throws InterruptedException {
		try (Cons.MeasureTime _ = new Cons.MeasureTime("GenWRs ...")) {
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

			_WRs = new ArrayList((int) Conf.global.writes);
			if (Conf.global.write_time_dist.equals("Same")) {
				for (int i = 1; i <= Conf.global.writes; i ++) {
					long es = epoch_sec_b + epoch_sec_dur * i / Conf.global.writes;
					_WRs.add(new WRs(es));
				}
			} else if (Conf.global.write_time_dist.equals("Uniform")) {
				ThreadLocalRandom tlr = ThreadLocalRandom.current();
				for (int i = 1; i <= Conf.global.writes; i ++) {
					long es = tlr.nextLong(epoch_sec_b, epoch_sec_e + 1);
					_WRs.add(new WRs(es));
				}
				// By sorting, primary keys are randomly ordered.
				Collections.sort(_WRs);
			}

			Cons.P(String.format("Write times (%s):", Conf.global.write_time_dist));
			//for (WRs wrs: _WRs)
			//	Cons.P(String.format("  %s", wrs));
			Cons.P(String.format("  generated %d writes", Conf.global.writes));
		}
	}

	private static void _DumpWRsForPlot() throws FileNotFoundException {
		String fn = Conf.global.fn_dump_wrs;
		PrintWriter writer = new PrintWriter(fn);
		for (WRs wrs: _WRs)
			writer.println(wrs.toStringForPlot());
		writer.close();
		Cons.P(String.format("Created file %s %d", fn, Util.getFileSize(fn)));
	}

	public static void main(String[] args) {
		try {
			Conf.Init(args);
			NumReadsPerObj.Init();
			ReadTimes.Init();

			GenWRs();
			if (Conf.global.fn_dump_wrs.length() > 0) {
				_DumpWRsForPlot();
			}
		} catch (Exception e) {
			System.out.printf("Exception: %s\n%s\n", e, Util.getStackTrace(e));
		}
	}
}
