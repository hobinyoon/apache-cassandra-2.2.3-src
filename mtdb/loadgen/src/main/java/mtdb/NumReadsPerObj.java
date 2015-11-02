package mtdb;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.lang.Math;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

public class NumReadsPerObj
{
	private static class ObjRankNumReqs {
		long obj_rank;
		double num_reqs;

		ObjRankNumReqs(long o, double n) {
			obj_rank = o;
			num_reqs = n;
		}

		@Override
		public String toString() {
			return String.format("%d %f", obj_rank, num_reqs);
		}
	}

	static List<ObjRankNumReqs> _ornrs;
	static long _obj_rank_min = -1;
	static long _obj_rank_max = -1;
	private static double _raw_avg_num_reqs;

	public static void Init() throws FileNotFoundException, IOException {
		try (Cons.MeasureTime _ = new Cons.MeasureTime("NumReadsPerObj.Init ...")) {
			_ornrs = new ArrayList();
			if (Conf.per_obj.num_reads_dist.startsWith("Custom: ")) {
				//                                       01234567
				String fn = "data/" + Conf.per_obj.num_reads_dist.substring(8);
				long sum = 0;
				long obj_rank = 0;
				long obj_rank_prev = 0;
				double num_reqs = 0.0;
				try (BufferedReader br = new BufferedReader(new FileReader(fn))) {
					String line;
					while ((line = br.readLine()) != null) {
						if (line.length() == 0)
							continue;
						if (line.charAt(0) == '#')
							continue;

						//String[] tokens = line.split(" +");
						String[] tokens = line.split("\t");
						if (tokens.length != 2)
							throw new RuntimeException("Unexpected format: " + line);

						obj_rank = Long.parseLong(tokens[0]);
						if (obj_rank_prev == obj_rank)
							continue;

						num_reqs = Double.parseDouble(tokens[1]);
						sum += ((obj_rank - obj_rank_prev) * num_reqs);

						_ornrs.add(new ObjRankNumReqs(obj_rank, num_reqs));
						if (_obj_rank_min == -1)
							_obj_rank_min = obj_rank;
						_obj_rank_max = obj_rank;
						obj_rank_prev = obj_rank;
					}

					if (obj_rank_prev != obj_rank) {
						sum += ((obj_rank - obj_rank_prev) * num_reqs);
					}
				}

				_raw_avg_num_reqs = ((double)sum) / _obj_rank_max;

				Cons.P(String.format("_obj_rank_min=%d _obj_rank_max=%d _raw_avg_num_reqs=%f",
							_obj_rank_min, _obj_rank_max, _raw_avg_num_reqs));

				//_RescaleData();
			}
		}
	}

	private static void _RescaleData() {
		// NewR_i = a (R_i - 1) + 1
		//
		// target_avg = a * (cur_avg - 1) + 1
		//
		// a = (target_avg - 1) / (cur_avg - 1)

		double a = (Conf.per_obj.avg_reads - 1.0) / (_raw_avg_num_reqs - 1.0);
		Cons.P(String.format("a=%f", a));

		for (ObjRankNumReqs o: _ornrs) {
			o.num_reqs = a * (o.num_reqs - 1.0) + 1.0;
		}

		//for (ObjRankNumReqs o: _ornrs)
		//	Cons.P(String.format("%d %f", o.obj_rank, o.num_reqs));
	}

	public static long GetNext() {
		// Sequential search
		ThreadLocalRandom tlr = ThreadLocalRandom.current();
		long rank = tlr.nextLong(_obj_rank_min, _obj_rank_max + 1);

		// Return the upper bound (, which is smaller than the lower bound)
		if (false) {
			// A sequential search from the end. Won't be too bad. It might be better than the
			// binary search since most of the random numbers will fall in the
			// buckets toward the end.
			int _ornrs_size = _ornrs.size();
			double num_reqs = -1.0;
			for (int i = _ornrs_size - 1; i >= 0; i --) {
				if (_ornrs.get(i).obj_rank <= rank) {
					if (i == _ornrs_size - 1) {
						num_reqs = _ornrs.get(i).num_reqs;
					} else {
						num_reqs = _ornrs.get(i+1).num_reqs;
					}
					//Cons.P(String.format("%d %f %d", rank, num_reqs, Math.round(num_reqs)));
					return Math.round(num_reqs);
				}
			}
		}

		// Interpolate between lower and upper bound
		if (true) {
			int _ornrs_size = _ornrs.size();
			double num_reqs = -1.0;
			for (int i = _ornrs_size - 1; i >= 0; i --) {
				if (_ornrs.get(i).obj_rank <= rank) {
					if (i == _ornrs_size - 1) {
						num_reqs = _ornrs.get(i).num_reqs;
					} else {
						// rank is always != _ornrs[i+1].obj_rank, since the same rank is
						// filtered out when loading the file
						num_reqs = (_ornrs.get(i+1).num_reqs - _ornrs.get(i).num_reqs)
							* (rank - _ornrs.get(i).obj_rank) / (_ornrs.get(i+1).obj_rank - _ornrs.get(i).obj_rank)
							+ _ornrs.get(i).num_reqs;
						//Cons.P(String.format("rank=%d i=%d num_reqs=%f %d | %d %d %f %f"
						//			, rank, i, num_reqs, Math.round(num_reqs)
						//			, _ornrs.get(i).obj_rank, _ornrs.get(i+1).obj_rank
						//			, _ornrs.get(i).num_reqs, _ornrs.get(i+1).num_reqs));
					}
					return Math.round(num_reqs);
				}
			}
		}

		throw new RuntimeException(
				String.format("Unexpected rank=%d _obj_rank_min=%d _obj_rank_max=%d",
					rank, _obj_rank_min, _obj_rank_max));
	}

	private static void _Dump() {
		for (ObjRankNumReqs o: _ornrs) {
			Cons.P(o.toString());
		}
	}

	private static void _Test() {
		try {
			Conf.Load();
			Init();
			//_Dump();

			for (int i = 0; i < 30; i ++) {
				Cons.P(GetNext());
			}
		} catch (Exception e) {
			System.out.printf("Exception: %s\n%s\n", e, Util.getStackTrace(e));
		}
	}

	public static void main(String[] args) {
		_Test();
	}
}
