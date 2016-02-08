package mtdb;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.lang.Math;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;


public class ReadTimes
{
	private static class AgeAccess {
		double age;	// in month
		double access;	// accesses in CDF

		AgeAccess(double ag, double ac) {
			age = ag;
			access = ac;
		}

		@Override
		public String toString() {
			return String.format("%f %f", age, access);
		}
	}

	static List<AgeAccess> _aas;
	static double _cdf_min = 0.0;
	static double _cdf_max = 1.0;

	public static void Init() throws FileNotFoundException, IOException {
		try (Cons.MeasureTime _ = new Cons.MeasureTime("ReadTimes.Init ...")) {
			_aas = new ArrayList();
			if (Conf.mutantsLoadgenOptions.per_obj.read_time_dist.startsWith("Custom: ")) {
				//                                       01234567
				String fn = "data/" + Conf.mutantsLoadgenOptions.per_obj.read_time_dist.substring(8);
				try (BufferedReader br = new BufferedReader(new FileReader(fn))) {
					String line;
					while ((line = br.readLine()) != null) {
						if (line.length() == 0)
							continue;
						if (line.charAt(0) == '#')
							continue;

						String[] tokens = line.split("\t");
						if (tokens.length != 2)
							throw new RuntimeException("Unexpected format: " + line);

						double age = Double.parseDouble(tokens[0]);
						double access = Double.parseDouble(tokens[1]);

						_aas.add(new AgeAccess(age, access));
					}
				}

				Cons.P(String.format("_cdf_min=%f _cdf_max=%f", _cdf_min, _cdf_max));
			}
		}
	}

	// 'U': take the upper bound
	// 'I': interpolate between the lower and the upper bound
	// Interesting that they don't have a meaningful performance difference.
	private static char _GETNEXT_METHOD = 'I';

	// Get next object age in sec
	public static long GetNext() {
		ThreadLocalRandom tlr = ThreadLocalRandom.current();
		double cdf = tlr.nextDouble(_cdf_min, _cdf_max);
		//Cons.P(String.format("cdf=%f", cdf));

		// y is age and x is CDF, up to 85.5450236966824
		//
		// y = 253.4513624 * POWER(F7, 8)
		// - 151.1600273 * POWER(F7, 7)
		// - 1134.730892 * POWER(F7, 6)
		// + 2232.128304 * POWER(F7, 5)
		// - 1769.212169 * POWER(F7, 4)
		// + 708.5013089 * POWER(F7, 3)
		// - 140.4471272 * POWER(F7, 2)
		// + 10.98698267 * F7
		// - 1.87247002e-4
		// + 0.000187247002

		double age = -1.0;
		if (cdf <= 0.855450236966824) {
			age =
				253.4513624 * Math.pow(cdf, 8)
				- 151.1600273 * Math.pow(cdf, 7)
				- 1134.730892 * Math.pow(cdf, 6)
				+ 2232.128304 * Math.pow(cdf, 5)
				- 1769.212169 * Math.pow(cdf, 4)
				+ 708.5013089 * Math.pow(cdf, 3)
				- 140.4471272 * Math.pow(cdf, 2)
				+ 10.98698267 * cdf
				- 1.87247002e-4F
				+ 0.000187247002;
		} else {
			// Interpolate between lower and upper bound
			int _aas_size = _aas.size();
			// Start from the left, which has bigger ranges.
			for (int i = 0; i < _aas_size; i ++) {
				if (cdf <= _aas.get(i).access) {
					if (i == 0) {
						// Dont' think it happens, since the outer if covers this range.
						// Just leaving it.
						age = _aas.get(i).age;
					} else {
						// cdf is always != _aas[i+1].access, since the same cdf is
						// filtered out when loading the file
						age = (_aas.get(i).age - _aas.get(i-1).age)
							* (cdf - _aas.get(i-1).access) / (_aas.get(i).access - _aas.get(i-1).access)
							+ _aas.get(i-1).age;
						if (age < 0)
							Cons.P(String.format("cdf=%f i=%d age=%f %d | %f %f %f %f"
										, cdf, i, age, Math.round(age)
										, _aas.get(i-1).access, _aas.get(i).access
										, _aas.get(i-1).age, _aas.get(i).age));
					}
					break;
				}
			}
		}

		// Convert to secs
		age *= (365.2425f / 12 * 24 * 3600);
		return Math.round(age);
	}

	private static void _Dump() {
		for (AgeAccess aa: _aas) {
			Cons.P(aa.toString());
		}
	}

	private static void _TestReadTimes() throws FileNotFoundException {
		try (Cons.MeasureTime _ = new Cons.MeasureTime("Test GetNext() ...")) {
			String fn = Conf.mutantsLoadgenOptions.global.fn_test_obj_ages;
			PrintWriter writer = new PrintWriter(fn);
			for (int i = 0; i < 1000000; i ++) {
				long age = GetNext();
				writer.println(age);
				//Cons.P(String.format("%10d %s", age,
				//			LocalDateTime.ofEpochSecond(age, 0, ZoneOffset.UTC)
				//			));
			}
			writer.close();
			Cons.P(String.format("Created file %s %d", fn, Util.getFileSize(fn)));
		}
	}

	public static void Test() throws Exception {
		Init();
		_TestReadTimes();
	}
}
