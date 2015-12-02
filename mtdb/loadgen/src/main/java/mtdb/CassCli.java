package mtdb;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.List;

import com.datastax.driver.core.Cluster;
import com.datastax.driver.core.ResultSet;
import com.datastax.driver.core.Row;
import com.datastax.driver.core.Session;

public class CassCli
{
	private static volatile boolean _shutdown_requested = false;

	private static void Insert() {
		// Insert one record into the users table
		_session.execute("INSERT INTO users (lastname, age, city, email, firstname) "
				+ "VALUES ('Jones', 35, 'Austin', 'bob@example.com', 'Bob')");
	}

	private static class ReaderThread implements Runnable
	{
		public void run() {
			try {
				// TODO
				//int keys_size = LoadGen._WRs.size();
				//while (true) {
				//	//Thread.sleep(1000);
				//	int i = _key_idx.getAndIncrement();
				//	if (keys_size <= i)
				//		break;

				//	//System.out.format("%d\n", i);
				//	ResultSet results = _session.execute("SELECT * FROM table1 WHERE key=" + 1);
				//}
			} catch (Exception e) {
				System.out.printf("Exception: %s\n%s\n", e, Util.getStackTrace(e));
			}
		}
	}

	private static class ReaderMonitor implements Runnable
	{
		private static volatile boolean _stop_requested = false;
		public void run() {
			try {
				// TODO
				//int keys_size = LoadGen._WRs.size();
				//int prev_i = 0;
				//while (! _stop_requested) {
				//	Thread.sleep(1000);
				//	int i = _key_idx.get();

				//	System.out.format("\033[1K");
				//	System.out.format("\033[1G");
				//	System.out.format("  read %d keys. %d reads/sec. %.2f%%",
				//			i,
				//			i - prev_i,
				//			100.0 * i / keys_size);
				//	System.out.flush();

				//	prev_i = i;
				//}
				//System.out.format("\n");

				// Leave last numbers as they are. Not a big deal.
			} catch (Exception e) {
				System.out.printf("Exception: %s\n%s\n", e, Util.getStackTrace(e));
			}
		}

		public void RequestStop() {
			_stop_requested = true;
		}
	}

	private static void ReadAllKeysInRandomOrder() throws InterruptedException {
		// TODO
		//int keys_size = LoadGen._WRs.size();

		//try (Cons.MeasureTime _ = new Cons.MeasureTime(
		//			String.format("Reading %d keys with %d threads..."
		//				, keys_size
		//				, Conf.cassandra.num_readers
		//				))) {
		//	ReaderMonitor rMon = new ReaderMonitor();
		//	Thread trMon = new Thread(rMon);
		//	trMon.start();

		//	List<Thread> threads = new ArrayList();
		//	for (int i = 0; i < Conf.cassandra.num_readers; ++ i) {
		//		Thread t = new Thread(new ReaderThread());
		//		t.start();
		//		threads.add(t);
		//	}

		//	for (Thread t: threads) {
		//		t.join();
		//	}
		//	rMon.RequestStop();
		//	trMon.join();

		//	// TODO: not sure the shutdown hook is the right way. it doesn't seem to
		//	// resume execution. check what i did with the PBR Cassandra client.
		//	System.out.printf("Joined all threads\n");
		//				}
	}




	private static Cluster _cluster = null;
	private static Session _session = null;
	private static AtomicInteger _wr_idx = new AtomicInteger(0);

	private static void _CassInit() throws InterruptedException {
		try (Cons.MeasureTime _ = new Cons.MeasureTime("Connect to Cassandra server ...")) {
			// Connect to the cluster and keyspace "demo"
			_cluster = Cluster.builder().addContactPoint("127.0.0.1").build();
			_session = _cluster.connect("mtdb1");
		}

		ReadAllKeysInRandomOrder();
	}

	private static void _CassClose() {
		if (_session != null)
			_session.close();

		// close() takes too long like 2.2 secs. System.exit() instead to save
		// time. Not sure what's the implication of this.
		//if (_cluster != null)
		//	_cluster.close();
	}

	public static void Run() throws InterruptedException {
		// TODO
		//_CassInit();

		//Cons.P(String.format("%d", LoadGen._WRs.hashCode()));

		//ReaderMonitor rMon = new ReaderMonitor();
		//Thread trMon = new Thread(rMon);
		//trMon.start();

		//List<Thread> threads = new ArrayList();
		//for (int i = 0; i < Conf.cassandra.num_readers; ++ i) {
		//	Thread t = new Thread(new ReaderThread());
		//	t.start();
		//	threads.add(t);
		//}
		//for (Thread t: threads)
		//	t.join();

		//rMon.RequestStop();
		//trMon.join();

		//_CassClose();
	}


	//public static void main(String[] args) {
	//	// TODO: gradeful shutdown. what I need is a SIGINT handler, not this one.
	//	Runtime.getRuntime().addShutdownHook(new Thread() {
	//		@Override
	//		public void run() {
	//			_shutdown_requested = true;
	//			System.out.printf("Shutdown requested\n");
	//		}
	//	});

	//	Cluster cluster = null;
	//	try {
	//		Conf.Init(args);

	//		try (Cons.MeasureTime _ = new Cons.MeasureTime("Connect to Cassandra server ...")) {
	//			// Connect to the cluster and keyspace "demo"
	//			cluster = Cluster.builder().addContactPoint("127.0.0.1").build();
	//			_session = cluster.connect("keyspace1");
	//		}

	//		ReadAllKeysInRandomOrder();

	//		System.out.printf("Normal exit\n");
	//	} catch (Exception e) {
	//		System.out.printf("Exception: %s\n%s\n", e, Util.getStackTrace(e));
	//	} finally {
	//		if (_session != null)
	//			_session.close();

	//		// close() takes 2.2 secs. System.exit() instead to save time. Not sure
	//		// what's the implication of this.
	//		//if (cluster != null)
	//		//	cluster.close();
	//	}
	//	System.exit(0);
	//}
}
