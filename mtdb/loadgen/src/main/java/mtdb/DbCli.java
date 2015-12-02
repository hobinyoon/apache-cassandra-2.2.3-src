package mtdb;

import java.util.concurrent.BlockingQueue;
import java.util.concurrent.PriorityBlockingQueue;

public class DbCli
{
	// TODO: Monitor progress by the number of requested writes / all writes.

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

	public static void Run() throws InterruptedException {
		try (Cons.MeasureTime _ = new Cons.MeasureTime("Making requests ...")) {
			try {
				for (Reqs.WRs wrs: Reqs._WRs)
					_q.put(new OpW(wrs));
				_q.put(new OpEndmarkW());

				// TODO: take() and put() elements in parallel
				while (true) {
					Op op = _q.take();
					Cons.P(op);

					if (op instanceof OpW) {
						for (long res: op.wrs.r_epoch_sec) {
							_q.put(new OpR(op.wrs, res));
						}
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
}
