package mtdb;

import java.nio.ByteBuffer;
import java.util.concurrent.ThreadLocalRandom;

import com.datastax.driver.core.Cluster;
import com.datastax.driver.core.ResultSet;
import com.datastax.driver.core.Row;
import com.datastax.driver.core.Session;

public class CassCli extends DbCli
{
	private CassCli() {
	}

	public static DbCli GetInstance() {
		if (_instance != null)
			return _instance;

		synchronized (_instance_mutex) {
			if (_instance == null) {
				_instance = new CassCli();
				return _instance;
			} else {
				return _instance;
			}
		}
	}

	// Generate random uncompressible data
	private String BuildC0(int length) {
		ThreadLocalRandom tlr = ThreadLocalRandom.current();
		// 64-bit, 8-byte
		long l = tlr.nextLong();

		ByteBuffer bb = ByteBuffer.allocate(length);
		//b.order(ByteOrder.BIG_ENDIAN); // optional, the initial order of a byte buffer is always BIG_ENDIAN.
		// bb is padded with 0s for the remainders of 8-byte blocks.
		for (int i = 0; i < (length / 8); i ++)
			bb.putLong(l);
		//Cons.P(Util.toHex(bb.array()));
		return Util.toHex(bb.array());
	}

	private Cluster _cluster = null;
	private Session _session = null;

	@Override
	protected void DbInit() {
		try (Cons.MeasureTime _ = new Cons.MeasureTime("Connecting to Cassandra server ...")) {
			_cluster = Cluster.builder().addContactPoint("127.0.0.1").build();
			_session = _cluster.connect("mtdb1");
		}
	}

	@Override
	protected void DbClose() {
		if (_session != null)
			_session.close();

		// Cluster.close() takes 2.2 secs. System.exit() instead to save time. Not sure
		// what's the implication of this.
		//if (_cluster != null)
		//	_cluster.close();
	}

	@Override
	protected void DbWrite(Op op) {
		_session.execute(String.format(
					"INSERT INTO table1 (key, epoch_sec, c0) "
					+ "VALUES (%d, %d, 0x%s)"
					, op.wrs.key
					, op.wrs.wEpochSec
					, BuildC0(Conf.per_obj.obj_size)
					));
	}

	@Override
	protected void DbRead(Op op) throws InterruptedException {
		ResultSet rs = _session.execute("SELECT * FROM table1 WHERE key=" + op.wrs.key);
		//Cons.P(String.format("fetched %d rows", rs.all().size()));
		int rsSize = rs.all().size();
		if (rsSize != 1) {
			// 0 is dangerous. It scans all SStables and some of them will cause the
			// bloom filter false positives.
			throw new RuntimeException("Unexpected rsSize=" + rsSize);
		}
	}
}
