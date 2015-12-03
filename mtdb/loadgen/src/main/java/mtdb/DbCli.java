package mtdb;

import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.PriorityBlockingQueue;
import java.util.ArrayList;
import java.util.List;

public class DbCli
{
	private static BlockingQueue<Op> _q = new PriorityBlockingQueue();

	public static class Op implements Comparable<Op> {
		Reqs.WRs wrs;
		long epoch_sec;

		@Override
		public int compareTo(Op r) {
			return (int)(epoch_sec - r.epoch_sec);
		}

		@Override
		public String toString() {
			return String.format("%d %d", epoch_sec, this.hashCode());
			//LocalDateTime.ofEpochSecond(epoch_sec, 0, ZoneOffset.UTC));
		}
	}

	public static class OpW extends Op {
		OpW(Reqs.WRs wrs) {
			this.wrs = wrs;
			epoch_sec = wrs.w_epoch_sec;
		}

		@Override
		public String toString() {
			return String.format("W  %d %d", epoch_sec, wrs.key);
		}
	}

	public static class OpR extends Op {
		OpR(Reqs.WRs wrs, long epoch_sec) {
			this.wrs = wrs;
			this.epoch_sec = epoch_sec;
		}

		@Override
		public String toString() {
			return String.format("R  %d %d", epoch_sec, wrs.key);
		}
	}

	public static class OpEndmark extends Op {
		OpEndmark() {
			wrs = null;
			// Assign the biggest (youngest) epoch value
			epoch_sec = Reqs._w_epoch_sec_e + 100;
		}
	}

	public static class OpEndmarkW extends OpEndmark {
		@Override
		public String toString() {
			return String.format("EW %d %d", epoch_sec, this.hashCode());
		}
	}

	public static class OpEndmarkR extends OpEndmark {
		@Override
		public String toString() {
			return String.format("ER %d %d", epoch_sec, this.hashCode());
		}
	}

	private static AtomicInteger numOpWsProcessed = new AtomicInteger();
	private static Object allOpWsProcessed = new Object();

	private static class DbClientThread implements Runnable
	{
		public void run() {
			try {
				while (true) {
					Op op = _q.take();
					//Cons.P(String.format("%s tid=%d", op, Thread.currentThread().getId()));

					if (op instanceof OpW) {
						// Simulate a write
						Thread.sleep(10);

						// Reads operations of the object are enqueued after the write to
						// make sure the records are returned from the database server.
						op.wrs.PopulateRs();
						for (long res: op.wrs.r_epoch_sec)
							_q.put(new OpR(op.wrs, res));

						StartDbClient();

						if (numOpWsProcessed.incrementAndGet() == Reqs._WRs.size()) {
							// No more DbClient thread is created at this point. Notify
							// the main thread to join them all.
							synchronized (allOpWsProcessed) {
								allOpWsProcessed.notify();
							}

							// Interrupt the monitoring thread so that it finishes sleep()
							// early.
							_progMon.interrupt();
						}
					} else if (op instanceof OpR) {
						// Simulate a read
						Thread.sleep(20);
					} else if (op instanceof OpEndmarkW) {
						for (int i = 0; i < Conf.db.num_threads; i ++) {
							_q.put(new OpEndmarkR());
						}
					} else if (op instanceof OpEndmarkR) {
						break;
					}
				}
			} catch (Exception e) {
				System.out.printf("Exception: %s\n%s\n", e, Util.getStackTrace(e));
			}
		}
	}

	private static List<Thread> _threads = new ArrayList();

	private static void StartDbClient() {
		// Start a consumer (DB client) thread one by one to prevent a bunch of
		// writes happening before any reads. Design is similar to test and
		// test-and-set.
		if (Conf.db.num_threads <= _threads.size())
			return;
		Thread t;
		synchronized (_threads) {
			if (Conf.db.num_threads <= _threads.size())
				return;
			t = new Thread(new DbClientThread());
			_threads.add(t);
		}
		t.start();
	}

	private static void JoinAllDbClients() throws InterruptedException {
		// When can you start joining DbClient threads? How do you know when no
		// more thread is created?
		//  - How many OpW(s) are completed? We know this number and it's the
		//  easiest.
		//
		// More difficult alternatives:
		//  - How many DbClient threads are created? It depends on the maximum
		//  number of threads and the number of OpW(s).
		//  - How many EndmarkerRs are you expecting to be processed? Depends on
		//  the number of threads created.
		//
		// Not working:
		//  - Wail till after consuming the OpEndmarkW. Other threads may still be
		//  working an OpW, possibly creating more threads.
		//  - Wait till after all OpEndmarkR(s) are consumed. We don't know if they
		//  will ever be consumed all since we are starting DbClient threads
		//  dynamically.
		//
		// Wait till all DbClient threads are done with OpEndmarkR before joining
		// them.
		synchronized (allOpWsProcessed) {
			allOpWsProcessed.wait();
		}

		synchronized (_threads) {
			// All DbClient threads can be joined here, even though they are created
			// in a hierarchical manner.
			for (Thread t: _threads)
				t.join();
		}
	}

	private static class ProgMon implements Runnable
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

					int w = numOpWsProcessed.get();
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

	private static Thread _progMon = new Thread(new ProgMon());

	public static void Run() throws InterruptedException {
		try (Cons.MeasureTime _ = new Cons.MeasureTime(
					String.format("Making %d WRs requests ...", Reqs._WRs.size()))) {
			for (Reqs.WRs wrs: Reqs._WRs)
				_q.put(new OpW(wrs));
			_q.put(new OpEndmarkW());

			StartDbClient();
			_progMon.start();
			JoinAllDbClients();
			_progMon.join();
		}
	}
}
