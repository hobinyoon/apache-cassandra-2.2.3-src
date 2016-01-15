package mtdb;

import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

// Progress monitor
class ProgMon {
	private static AtomicInteger _extraSleepRunningOnTimeCnt = new AtomicInteger(0);
	private static AtomicLong _extraSleepRunningOnTimeSum = new AtomicLong(0);
	private static AtomicInteger _extraSleepRunningBehindCnt = new AtomicInteger(0);
	private static AtomicLong _extraSleepRunningBehindSum = new AtomicLong(0);

	private static class MonThread implements Runnable
	{
		public void run() {
			// Monitor the progress by the number of requested writes / all writes.
			try {
				int w_total = Reqs._WRs.size();
				int w_prev = 0;
				String fmt = "%7d %17s %7d %5.1f %5d %5d %8d %5d %8d %4d %4d %4d %4d";
				Cons.P(Util.BuildHeader(fmt, 0
							, "simulation_time_ms"
							, "simulated_time"
							, "num_OpW_requested"
							, "percent_completed"
							, "OpW_per_sec"
							, "running_on_time_cnt"
							, "running_on_time_sleep_avg_in_ms"
							, "running_behind_cnt"
							, "running_behind_avg_in_ms"
							, "write_latency_ms"
							, "read_latency_ms"
							, "write_cnt"
							, "read_cnt"
							));
				while (true) {
					try {
						Thread.sleep(1000);
					} catch (InterruptedException e) {
						// sleep() can be interrupted when w == w_total
					}

					int w = DbCli.NumOpWsRequested();
					//System.out.printf("\033[1K");
					//System.out.printf("\033[1G");
					//System.out.printf("  %d/%d %.2f%%", w, w_total, (100.0 * w / w_total));
					int extraSleepRunningOnTimeCnt = _extraSleepRunningOnTimeCnt.get();
					long extraSleepRunningOnTimeAvg = (extraSleepRunningOnTimeCnt == 0) ?
						0 : (_extraSleepRunningOnTimeSum.get() / extraSleepRunningOnTimeCnt / 1000000);
					int extraSleepRunningBehindCnt = _extraSleepRunningBehindCnt.get();
					long extraSleepRunningBehindAvg = (extraSleepRunningBehindCnt == 0) ?
						0 : (_extraSleepRunningBehindSum.get() / extraSleepRunningBehindCnt / 1000000);
					LatMon.Result latency = LatMon.GetAndReset();

					long curTime = System.nanoTime();
					Cons.P(String.format(fmt
								, (curTime - SimTime.SimulationTimeBeginNano()) / 1000000
								, SimTime.GetSimulatedTime(curTime)
								, w
								, 100.0 * w / w_total
								, w - w_prev
								, extraSleepRunningOnTimeCnt
								, extraSleepRunningOnTimeAvg
								, extraSleepRunningBehindCnt
								, extraSleepRunningBehindAvg
								, latency.avgWriteTime / 1000000
								, latency.avgReadTime / 1000000
								, latency.writeCnt
								, latency.readCnt
								));
					if (w == w_total)
						break;

					w_prev = w;
					_extraSleepRunningOnTimeCnt.set(0);
					_extraSleepRunningOnTimeSum.set(0);
					_extraSleepRunningBehindCnt.set(0);
					_extraSleepRunningBehindSum.set(0);

					//System.out.flush();
				}

				// Overall stat
				//   Total # of writes
				//   Total # of reads
				//   # of reads / write: min, max, avg, 50, 90, 95, and 99-th percentiles.
				//     min can be 0, because towards the end of the simulation period,
				//     some Ws don't have corresponding Rs.
				//
				//   Read/write latency: min, max, avg, 50, 90, 95, and 99-th percentiles.

				LatMon.Stat wStat = LatMon.GetWriteStat();
				LatMon.Stat rStat = LatMon.GetReadStat();

				Cons.P(String.format("#"));
				Cons.P(String.format("# # of writes: %d", Reqs._WRs.size()));
				Cons.P(String.format("# # of reads : %d", rStat.cnt));
				Reqs.NumReadsPerWriteStat nrpwStat = Reqs.GetNumReadsPerWriteStat();
				Cons.P(String.format("# # reads / write:"));
				Cons.P(String.format("#   avg=%6.3f min=%5d max=%4d 50=%4d 90=%4d 95=%4d 99=%4d 995=%4d 999=%4d"
							, nrpwStat.avg
							, nrpwStat.min
							, nrpwStat.max
							, nrpwStat._50
							, nrpwStat._90
							, nrpwStat._95
							, nrpwStat._99
							, nrpwStat._995
							, nrpwStat._999
							));
				Cons.P(String.format("#"));
				Cons.P(String.format("# Write latency:"));
				Cons.P(String.format("#   avg=%6.3f min=%5.3f max=%4d 50=%4d 90=%4d 95=%4d 99=%4d 995=%4d 999=%4d"
							, wStat.avg  / 1000000.0
							, wStat.min  / 1000000.0
							, wStat.max  / 1000000
							, wStat._50  / 1000000
							, wStat._90  / 1000000
							, wStat._95  / 1000000
							, wStat._99  / 1000000
							, wStat._995 / 1000000
							, wStat._999 / 1000000
							));
				Cons.P(String.format("# Read latency:"));
				Cons.P(String.format("#   avg=%6.3f min=%5.3f max=%4d 50=%4d 90=%4d 95=%4d 99=%4d 995=%4d 999=%4d"
							, rStat.avg  / 1000000.0
							, rStat.min  / 1000000.0
							, rStat.max  / 1000000
							, rStat._50  / 1000000
							, rStat._90  / 1000000
							, rStat._95  / 1000000
							, rStat._99  / 1000000
							, rStat._995 / 1000000
							, rStat._999 / 1000000
							));
			} catch (Exception e) {
				System.out.printf("Exception: %s\n%s\n", e, Util.getStackTrace(e));
			}
		}
	}

	private static Thread _monThread = new Thread(new MonThread());

	public static void Start() {
		_monThread.start();
	}

	public static void Stop() throws InterruptedException {
		// Interrupt the monitoring thread so that it finishes sleep() early.
		_monThread.interrupt();
		_monThread.join();
	}

	public static void SimulatorRunningOnTime(long extraSleep) {
		_extraSleepRunningOnTimeCnt.incrementAndGet();
		_extraSleepRunningOnTimeSum.addAndGet(extraSleep);
	}

	public static void SimulatorRunningBehind(long extraSleep) {
		_extraSleepRunningBehindCnt.incrementAndGet();
		_extraSleepRunningBehindSum.addAndGet(extraSleep);
	}
}
