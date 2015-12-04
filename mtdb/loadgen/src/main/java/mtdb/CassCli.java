package mtdb;

import com.datastax.driver.core.Cluster;
import com.datastax.driver.core.ResultSet;
import com.datastax.driver.core.Row;
import com.datastax.driver.core.Session;

public class CassCli extends DbCli
{
	private String _c0;

	public CassCli() {
		synchronized (_mutex) {
			if (_instance == null) {
				_instance = this;
			}
		}

		BuildC0();
	}

	private void BuildC0() {
		StringBuilder sb = new StringBuilder(1001);
		int j = 0;
		while (true) {
			for (int i = 0; (i < 26 && j != 1000); i ++, j ++) {
				sb.append((char) ('a' + i));
			}
			if (j == 1000)
				break;
		}
		_c0 = sb.toString();
		Cons.P(_c0);
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
					+ "VALUES (%d, %d, '%s')"
					, op.wrs.key
					, op.wrs.wEpochSec
					, _c0
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
