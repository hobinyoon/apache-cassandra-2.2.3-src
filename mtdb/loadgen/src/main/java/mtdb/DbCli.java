package mtdb;

import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.PriorityBlockingQueue;
import java.util.ArrayList;
import java.util.List;

public class DbCli
{
	private BlockingQueue<Op> _q = new PriorityBlockingQueue();

	protected class Op implements Comparable<Op> {
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

	protected class OpW extends Op {
		OpW(Reqs.WRs wrs) {
			this.wrs = wrs;
			epoch_sec = wrs.wEpochSec;
		}

		@Override
		public String toString() {
			return String.format("W  %d %d", epoch_sec, wrs.key);
		}
	}

	protected class OpR extends Op {
		OpR(Reqs.WRs wrs, long epoch_sec) {
			this.wrs = wrs;
			this.epoch_sec = epoch_sec;
		}

		@Override
		public String toString() {
			return String.format("R  %d %d", epoch_sec, wrs.key);
		}
	}

	private class OpEndmark extends Op {
		OpEndmark() {
			wrs = null;
			// Assign the biggest (youngest) epoch value
			epoch_sec = SimTime.SimulatedTimeEndEs() + 100;
		}
	}

	private class OpEndmarkW extends OpEndmark {
		@Override
		public String toString() {
			return String.format("EW %d %d", epoch_sec, this.hashCode());
		}
	}

	private class OpEndmarkR extends OpEndmark {
		@Override
		public String toString() {
			return String.format("ER %d %d", epoch_sec, this.hashCode());
		}
	}

	private AtomicInteger _numOpWsProcessed = new AtomicInteger();
	private Object _allOpWsProcessed = new Object();

	private class DbClientThread implements Runnable
	{
		private DbCli dbCli;

		DbClientThread(DbCli dbCli) {
			this.dbCli = dbCli;
		}

		public void run() {
			try {
				while (true) {
					Op op = dbCli._q.take();
					//Cons.P(String.format("%s tid=%d", op, Thread.currentThread().getId()));

					if (op instanceof OpW) {
						SimTime.SleepUntilSimulatedTime(op.epoch_sec);
						dbCli.DbWriteMeasureTime(op);

						// Reads operations of the object are enqueued after the write to
						// make sure the records are returned from the database server.
						op.wrs.PopulateRs();
						for (long res: op.wrs.rEpochSecs)
							dbCli._q.put(new OpR(op.wrs, res));

						dbCli.StartDbClient();

						if (dbCli._numOpWsProcessed.incrementAndGet() == Reqs._WRs.size()) {
							// No more DbClient thread is created at this point. Notify
							// the main thread to join them all.
							synchronized (_allOpWsProcessed) {
								_allOpWsProcessed.notify();
							}
						}
					} else if (op instanceof OpR) {
						SimTime.SleepUntilSimulatedTime(op.epoch_sec);
						dbCli.DbReadMeasureTime(op);
					} else if (op instanceof OpEndmarkW) {
						for (int i = 0; i < Conf.db.num_threads; i ++) {
							dbCli._q.put(new OpEndmarkR());
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

	public static int NumOpWsRequested() {
		if (_instance == null)
			throw new RuntimeException("No _instance yet");
		return _instance._numOpWsProcessed.get();
	}

	private List<Thread> _threads = new ArrayList();

	private void StartDbClient() {
		// Start a consumer (DB client) thread one by one to prevent a bunch of
		// writes happening before any reads. Design is similar to test and
		// test-and-set.
		if (Conf.db.num_threads <= _threads.size())
			return;
		Thread t;
		synchronized (_threads) {
			if (Conf.db.num_threads <= _threads.size())
				return;
			t = new Thread(new DbClientThread(this));
			_threads.add(t);
		}
		t.start();
	}

	private void JoinAllDbClients() throws InterruptedException {
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
		synchronized (_allOpWsProcessed) {
			_allOpWsProcessed.wait();
		}

		synchronized (_threads) {
			// All DbClient threads can be joined here, even though they are created
			// in a hierarchical manner.
			for (Thread t: _threads)
				t.join();
		}
	}

	public void Run() throws InterruptedException {
		try (Cons.MeasureTime _ = new Cons.MeasureTime(
					String.format("Making %d WRs requests ...", Reqs._WRs.size()))) {
			for (Reqs.WRs wrs: Reqs._WRs)
				_q.put(new OpW(wrs));
			_q.put(new OpEndmarkW());

			// This can run in parallel with the conf init process, saving 200 ms.
			// Not worth the effort for now.
			DbInit();

			SimTime.StartSimulation();

			StartDbClient();
			ProgMon.Start();

			JoinAllDbClients();

			ProgMon.Stop();
			DbClose();
		}
	}

	protected static final Integer _instance_mutex = new Integer(0);
	protected static DbCli _instance = null;

	protected DbCli() {
	}

	protected void DbInit() {
	}

	protected void DbClose() {
	}

	protected void DbReadMeasureTime(Op op) throws InterruptedException {
		long begin = System.nanoTime();
		DbRead(op);
		long end = System.nanoTime();
		LatMon.Read(end - begin);
	}

	protected void DbWriteMeasureTime(Op op) throws InterruptedException {
		long begin = System.nanoTime();
		DbWrite(op);
		long end = System.nanoTime();
		LatMon.Write(end - begin);
	}

	protected void DbWrite(Op op) throws InterruptedException {
		// Simulate a write
		Thread.sleep(10);
	}

	protected void DbRead(Op op) throws InterruptedException {
		// Simulate a read, which is slower than write
		Thread.sleep(20);
	}
}
