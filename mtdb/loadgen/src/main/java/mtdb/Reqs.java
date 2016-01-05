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
		long wEpochSec;
		List<Long> rEpochSecs;

		WRs(long wEpochSec) {
			key = _nextKey ++;
			this.wEpochSec = wEpochSec;
		}

		public void PopulateRs() {
			// Populate rEpochSecs
			int num_reads = NumReadsPerObj.GetNext();
			//Cons.P(String.format("num_reads=%d", num_reads));
			rEpochSecs = new ArrayList(num_reads);
			for (int i = 0; i < num_reads; i ++) {
				// Do not add reads after the last write, which is the end of the
				// simulation.
				long r = wEpochSec + ReadTimes.GetNext();
				if (r >= SimTime.SimulatedTimeEndEs())
					continue;
				rEpochSecs.add(r);
			}
			Collections.sort(rEpochSecs);
			//Cons.P(String.format("rEpochSecs.size()=%d", rEpochSecs.size()));
		}

		@Override
		public int compareTo(WRs r) {
			return (int)(wEpochSec - r.wEpochSec);
		}

		@Override
		public String toString() {
			StringBuilder sb = new StringBuilder(1000);
			sb.append("key: ").append(key).append("\n");
			sb.append("w: ").append(wEpochSec);
			boolean first = true;
			for (long r: rEpochSecs) {
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
			//		wEpochSec,
			//		LocalDateTime.ofEpochSecond(wEpochSec, 0, ZoneOffset.UTC));
		}

		public String toStringForPlot() {
			StringBuilder sb = new StringBuilder(1000);
			sb.append(key);
			sb.append(" W ");
			sb.append(wEpochSec);
			for (long r: rEpochSecs) {
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

	public static class NumReadsPerWriteStat {
		int cnt;
		int min;
		int max;
		double avg;
		int _50;
		int _90;
		int _95;
		int _99;
		int _995;
		int _999;

		NumReadsPerWriteStat() {
			List<Integer> numReadsPerWrite = new ArrayList();
			for (WRs wrs: _WRs)
				numReadsPerWrite.add(wrs.rEpochSecs.size());

			Collections.sort(numReadsPerWrite);
			min = numReadsPerWrite.get(0);
			max = numReadsPerWrite.get(numReadsPerWrite.size() - 1);

			boolean set_50 = false;
			boolean set_90 = false;
			boolean set_95 = false;
			boolean set_99 = false;
			boolean set_995 = false;
			boolean set_999 = false;
			int sum = 0;
			cnt = 0;
			int v_size = numReadsPerWrite.size();
			for (int i = 0; i < v_size; i ++) {
				if ((set_50 == false) && (i >= 0.5 * v_size)) {
					_50 = numReadsPerWrite.get(i);
					set_50 = true;
				}
				if ((set_90 == false) && (i >= 0.90 * v_size)) {
					_90 = numReadsPerWrite.get(i);
					set_90 = true;
				}
				if ((set_95 == false) && (i >= 0.95 * v_size)) {
					_95 = numReadsPerWrite.get(i);
					set_95 = true;
				}
				if ((set_99 == false) && (i >= 0.99 * v_size)) {
					_99 = numReadsPerWrite.get(i);
					set_99 = true;
				}
				if ((set_995 == false) && (i >= 0.995 * v_size)) {
					_995 = numReadsPerWrite.get(i);
					set_995 = true;
				}
				if ((set_999 == false) && (i >= 0.999 * v_size)) {
					_999 = numReadsPerWrite.get(i);
					set_999 = true;
				}
				sum += numReadsPerWrite.get(i);
				cnt ++;
			}
			avg = (cnt == 0) ? 0 : ((double) sum / cnt);
		}
	}

	public static NumReadsPerWriteStat GetNumReadsPerWriteStat() {
		NumReadsPerWriteStat stat = new NumReadsPerWriteStat();
		return stat;
	}
}
