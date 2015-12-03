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
				String fmt = "%7d %5.1f %4d %4d %8d %4d %8d";
				Cons.P(Util.BuildHeader(fmt, 0
							, "num_OpW_requested"
							, "percent_completed"
							, "OpW_per_sec"
							, "running_on_time_cnt"
							, "running_on_time_sleep_avg_in_us"
							, "running_behind_cnt"
							, "running_behind_avg_in_us"
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
						0 : (_extraSleepRunningOnTimeSum.get() / extraSleepRunningOnTimeCnt / 1000);
					int extraSleepRunningBehindCnt = _extraSleepRunningBehindCnt.get();
					long extraSleepRunningBehindAvg = (extraSleepRunningBehindCnt == 0) ?
						0 : (_extraSleepRunningBehindSum.get() / extraSleepRunningBehindCnt / 1000);
					Cons.P(String.format(fmt
								, w
								, 100.0 * w / w_total
								, w - w_prev
								, extraSleepRunningOnTimeCnt
								, extraSleepRunningOnTimeAvg
								, extraSleepRunningBehindCnt
								, extraSleepRunningBehindAvg
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
				//System.out.printf("\n");
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
