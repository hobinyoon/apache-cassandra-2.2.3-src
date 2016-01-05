package mtdb;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.lang3.time.DurationFormatUtils;

class SimTime {
	// Simulation time is the wall-clock time in which this simulator is running.
	// Simulated time is the time that this simulator simulates, e.g., from
	// 2010-01-01 to 2015-01-01.
	private static LocalDateTime _simulatedTimeBegin;
	private static LocalDateTime _simulatedTimeEnd;
	// In seconds from Epoch
	private static long _simulatedTimeBeginEs;
	private static long _simulatedTimeEndEs;
	private static long _simulatedTimeDurEs;

	private static ZoneId _zoneId;

	// In nano seconds
	private static long _simulationTimeBegin;
	private static long _simulationTimeEnd;
	private static long _simulationTimeDur;

	public static void Init() {
		_simulatedTimeBegin = LocalDateTime.of(2010, 1, 1, 0, 0);
		_simulatedTimeEnd = LocalDateTime.of(2010 + Conf.global.simulated_time_in_year, 1, 1, 0, 0);

		_zoneId = ZoneId.systemDefault();

		// Convert to Epoch seconds. Ignore sub-second resolution
		_simulatedTimeBeginEs = _simulatedTimeBegin.atZone(_zoneId).toEpochSecond();
		_simulatedTimeEndEs = _simulatedTimeEnd.atZone(_zoneId).toEpochSecond();
		_simulatedTimeDurEs = _simulatedTimeEndEs - _simulatedTimeBeginEs;

		Cons.P(String.format("Simulated datetime:"
					+ "\n  begin: %16s %10d"
					+ "\n  end:   %16s %10d"
					//+ "\n  dur:   %16s %10d"
					, _simulatedTimeBegin, _simulatedTimeBeginEs
					, _simulatedTimeEnd, _simulatedTimeEndEs
					//, DurationFormatUtils.formatDurationHMS(_simulatedTimeDurEs * 1000), _simulatedTimeDurEs
					));
	}

	public static long SimulatedTimeBeginEs() {
		return _simulatedTimeBeginEs;
	}

	public static long SimulatedTimeEndEs() {
		return _simulatedTimeEndEs;
	}

	public static long SimulatedTimeDurEs() {
		return _simulatedTimeDurEs;
	}

	public static long SimulationTimeBeginNano() {
		return _simulationTimeBegin;
	}

	public static void StartSimulation() {
		_simulationTimeDur = (long) (Conf.global.simulation_time_in_min * 60 * 1000000000);
		_simulationTimeBegin = System.nanoTime();
		_simulationTimeEnd = _simulationTimeBegin + _simulationTimeDur;
		Cons.P(String.format("Simulation time:"
					+ "\n  begin: %16d"
					+ "\n  end:   %16d"
					+ "\n  dur:   %16d"
					, _simulationTimeBegin
					, _simulationTimeEnd
					, _simulationTimeDur
					));
	}

	// Average Thread.sleep(0, 1) time is 1.1 ms on a 8 core Xeon E5420 @ 2.50GHz
	// machine
	final private static long _minSleepNano = 2000000;

	public static void SleepUntilSimulatedTime(long simulatedTimeEs) throws InterruptedException {
		long durSinceSimulatedTimeBegin = simulatedTimeEs - _simulatedTimeBeginEs;

		// _simulationTimeDur : _simulatedTimeDurEs
		//   = targetDurSinceSimulationTimeBegin : durSinceSimulatedTimeBegin
		//
		// targetDurSinceSimulationTimeBegin = (targetSimulationTime - _simulationTimeBegin)
		//
		// sleep for (targetSimulationTime - curTime)

		//targetDurSinceSimulationTimeBegin = _simulationTimeDur * durSinceSimulatedTimeBegin / _simulatedTimeDurEs;
		//(targetSimulationTime - _simulationTimeBegin) = _simulationTimeDur * durSinceSimulatedTimeBegin / _simulatedTimeDurEs;
		long targetSimulationTime = (long) (((double) _simulationTimeDur) * durSinceSimulatedTimeBegin
				/ _simulatedTimeDurEs + _simulationTimeBegin);
		long curTime = System.nanoTime();
		long extraSleep = targetSimulationTime - curTime;
		//Cons.P(String.format("extraSleep: %10d %4d %7d"
		//			, extraSleep
		//			, extraSleep / 1000000
		//			, extraSleep % 1000000
		//			));
		if (extraSleep > 0) {
			ProgMon.SimulatorRunningOnTime(extraSleep);
		} else {
			ProgMon.SimulatorRunningBehind(extraSleep);
		}
		if (extraSleep <= _minSleepNano)
			return;
		Thread.sleep(extraSleep / 1000000, (int) (extraSleep % 1000000));
	}

	public static void TestMinimumSleeptime() throws InterruptedException {
		try (Cons.MeasureTime _ = new Cons.MeasureTime("Testing minimum Thread.sleep() time ...")) {
			int runs = 1000;
			List<Long> sleepTimes = new ArrayList();
			for (int i = 0; i < runs; i ++) {
				long before = System.nanoTime();
				Thread.sleep(0, 1);
				long after = System.nanoTime();
				sleepTimes.add(after - before);
			}

			long min = -1;
			long max = -1;
			long sum = 0;
			boolean first = true;
			for (long st: sleepTimes) {
				if (first) {
					min = max = st;
					first = false;
				} else {
					if (st < min) {
						min = st;
					} else if (max < st) {
						max = st;
					}
				}
				sum += st;
			}
			double avg = ((double) sum) / runs;

			Cons.P(String.format(
						"In nano seconds"
						+ "\navg: %f"
						+ "\nmin: %d"
						+ "\nmax: %d"
						+ "\nruns: %d"
						, avg
						, min
						, max
						, runs
						));
		}
	}
}
