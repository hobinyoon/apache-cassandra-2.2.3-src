package mtdb;

import java.time.LocalDateTime;
import java.time.ZoneId;

import org.apache.commons.lang3.time.DurationFormatUtils;

class SimTime {
	// Simulation time is the wall-clock time in which this simulator is running.
	// Simulated time is the time that this simulator simulates, e.g., from
	// 2010-01-01 to 2015-01-01.
	private static LocalDateTime _simulatedTimeBegin;
	private static LocalDateTime _simulatedTimeEnd;
	// In epoch second
	private static long _simulatedTimeBeginEs;
	private static long _simulatedTimeEndEs;
	private static long _simulatedTimeDurEs;

	private static ZoneId _zoneId;

	private static long _simulationTimeBegin;

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

	public static void StartSimulation() {
		_simulationTimeBegin = System.nanoTime();
	}

	public static void SleepUntilSimulatedTime(long simulatedTime) {
		long curTime = System.nanoTime();
		long durSinceSimulationTimeBegin = _simulationTimeBegin - curTime;
		// TODO: sleep
	}
}
