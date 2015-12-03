package mtdb;

import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.lang.InterruptedException;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.concurrent.ThreadLocalRandom;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.apache.commons.lang3.time.DurationFormatUtils;

public class Reqs
{
	static LocalDateTime _w_dt_b;
	static LocalDateTime _w_dt_e;
	static long _w_epoch_sec_b;
	public static long _w_epoch_sec_e;

	// Write and reads operations to an object
	public static class WRs implements Comparable<WRs> {
		long key;	// primary key of the record
		static long global_key = 0;
		long w_epoch_sec;
		List<Long> r_epoch_sec;

		WRs(long w_epoch_sec_) {
			key = global_key ++;
			w_epoch_sec = w_epoch_sec_;
		}

		public void PopulateRs() {
			// Populate r_epoch_sec
			long num_reads = NumReadsPerObj.GetNext();
			//Cons.P(String.format("num_reads=%d", num_reads));
			r_epoch_sec = new ArrayList((int)num_reads);
			for (long i = 0; i < num_reads; i ++) {
				// Reads after the last write doesn't need to be stored for the purpose
				// of the simulation
				long r = w_epoch_sec + ReadTimes.GetNext();
				if (r >= _w_epoch_sec_e)
					continue;
				r_epoch_sec.add(r);
			}
			Collections.sort(r_epoch_sec);
		}

		@Override
		public int compareTo(WRs r) {
			return (int)(w_epoch_sec - r.w_epoch_sec);
		}

		@Override
		public String toString() {
			StringBuilder sb = new StringBuilder(1000);
			sb.append("key: ").append(key).append("\n");
			sb.append("w: ").append(w_epoch_sec);
			boolean first = true;
			for (long r: r_epoch_sec) {
				if (first) {
					sb.append("\nr: ");
					first = false;
				} else {
					sb.append("\n   ");
				}
				sb.append(r);
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


	// Parallelize GenWRs() and see how much speed up you get. worth the time?
	// not sure. The fact that all CPUs are already busy makes me more skeptical
	// about this.
	// Before: 7104 ms with 1M WRs
	//
	// Java array takes longer than ArrayList<>. Interesting.
	//public static WRs[] _WRs = null;
	public static List<WRs> _WRs;

	public static void GenWRs() throws InterruptedException {
		try (Cons.MeasureTime _ = new Cons.MeasureTime(
					String.format("Generating %d WRs(s) ...", Conf.global.writes))) {
			// Simulated datetime begin and end
			_w_dt_b = LocalDateTime.of(2010, 1, 1, 0, 0);
			_w_dt_e = LocalDateTime.of(2010 + Conf.global.simulated_time_in_year, 1, 1, 0, 0);

			ZoneId zoneId = ZoneId.systemDefault();
			// Ignore sub-second resolution
			_w_epoch_sec_b = _w_dt_b.atZone(zoneId).toEpochSecond();
			_w_epoch_sec_e = _w_dt_e.atZone(zoneId).toEpochSecond();
			long epoch_sec_dur = _w_epoch_sec_e - _w_epoch_sec_b;

			Cons.P(String.format("Simulated datetime:"
						+ "\n  begin: %16s %10d"
						+ "\n  end:   %16s %10d"
						//+ "\n  dur:   %16s %10d"
						, _w_dt_b, _w_epoch_sec_b
						, _w_dt_e, _w_epoch_sec_e
						//, DurationFormatUtils.formatDurationHMS(epoch_sec_dur * 1000), epoch_sec_dur
						));

			_WRs = new ArrayList(Conf.global.writes);
			if (Conf.global.write_time_dist.equals("Same")) {
				for (int i = 1; i <= Conf.global.writes; i ++) {
					long es = _w_epoch_sec_b + epoch_sec_dur * i / Conf.global.writes;
					_WRs.add(new WRs(es));
				}
			} else if (Conf.global.write_time_dist.equals("Uniform")) {
				ThreadLocalRandom tlr = ThreadLocalRandom.current();
				for (int i = 1; i <= Conf.global.writes; i ++) {
					long es = tlr.nextLong(_w_epoch_sec_b, _w_epoch_sec_e + 1);
					_WRs.add(new WRs(es));
				}
				// Sort by their write epochs. Primary keys are randomly ordered after
				// sorting.
				//
				// Interesting. parallelSort() is slower with 1M items:
				//   sort()         7384 ms
				//   parallelSort() 7825 ms
				//Arrays.sort(_WRs);
				//Arrays.parallelSort(_WRs);
				Collections.sort(_WRs);
			}

			//Cons.P(String.format("Write times (%s):", Conf.global.write_time_dist));
			//for (WRs wrs: _WRs)
			//	Cons.P(wrs);
		}
	}

	public static void DumpWRsForPlot() throws FileNotFoundException {
		String fn = Conf.global.fn_dump_wrs;
		PrintWriter writer = new PrintWriter(fn);
		for (WRs wrs: _WRs)
			writer.println(wrs.toStringForPlot());
		writer.close();
		Cons.P(String.format("Created file %s %d", fn, Util.getFileSize(fn)));
	}
}
