package mtdb;

// Progress monitor
class ProgMon {
	private static class MonThread implements Runnable
	{
		public void run() {
			// Monitor the progress by the number of requested writes / all writes.
			try {
				int w_total = Reqs._WRs.size();
				int w_prev = 0;
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
					Cons.P(String.format("%d %d op/s %.2f%%",
								w, w - w_prev, 100.0 * w / w_total));
					if (w == w_total)
						break;
					w_prev = w;
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
}
