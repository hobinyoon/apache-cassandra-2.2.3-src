package mtdb;

import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.lang.InterruptedException;
import java.time.Duration;
import java.time.ZoneOffset;
import java.util.concurrent.ThreadLocalRandom;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Reqs
{
	// Write and reads operations to an object
	public static class WRs implements Comparable<WRs> {
		// Primary key of the record
		long key;
		// All WRs instances are created serially. No need to be atomic.
		static long _nextKey = 0;
		long w_epoch_sec;
		List<Long> r_epoch_sec;

		WRs(long w_epoch_sec_) {
			key = _nextKey ++;
			w_epoch_sec = w_epoch_sec_;
		}

		public void PopulateRs() {
			// Populate r_epoch_sec
			long num_reads = NumReadsPerObj.GetNext();
			//Cons.P(String.format("num_reads=%d", num_reads));
			r_epoch_sec = new ArrayList((int)num_reads);
			for (long i = 0; i < num_reads; i ++) {
				// Do not add reads after the last write, which is the end of the
				// simulation.
				long r = w_epoch_sec + ReadTimes.GetNext();
				if (r >= SimTime.SimulatedTimeEndEs())
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
			_WRs = new ArrayList(Conf.global.writes);
			if (Conf.global.write_time_dist.equals("Same")) {
				for (int i = 1; i <= Conf.global.writes; i ++) {
					long es = SimTime.SimulatedTimeBeginEs() + SimTime.SimulatedTimeDurEs() * i / Conf.global.writes;
					_WRs.add(new WRs(es));
				}
			} else if (Conf.global.write_time_dist.equals("Uniform")) {
				ThreadLocalRandom tlr = ThreadLocalRandom.current();
				for (int i = 1; i <= Conf.global.writes; i ++) {
					long es = tlr.nextLong(SimTime.SimulatedTimeBeginEs(), SimTime.SimulatedTimeEndEs() + 1);
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
