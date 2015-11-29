package mtdb;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import com.datastax.driver.core.Cluster;
import com.datastax.driver.core.ResultSet;
import com.datastax.driver.core.Row;
import com.datastax.driver.core.Session;

public class CassCli
{
	private static Session _session = null;
	private static List<String> _keys = new ArrayList();

	private static void Insert() {
		// Insert one record into the users table
		_session.execute("INSERT INTO users (lastname, age, city, email, firstname) "
				+ "VALUES ('Jones', 35, 'Austin', 'bob@example.com', 'Bob')");
	}

	private static void Select() {
		// Use select to get the user we just entered
		ResultSet results = _session.execute("SELECT * FROM users WHERE lastname='Jones'");
		for (Row row : results) {
			System.out.format("%s %d\n", row.getString("firstname"), row.getInt("age"));
		}
	}

	private static void LoadKs1Keys() throws FileNotFoundException, IOException {
		try (Cons.MeasureTime _ = new Cons.MeasureTime("LoadKs1Keys ...")) {
			String fn = "../../data/write-keys-15-11-26-18:13:46";
			try (BufferedReader br = new BufferedReader(new FileReader(fn))) {
				String line;
				while ((line = br.readLine()) != null) {
					//System.out.printf("[%s]\n", line);
					_keys.add(line);
				}
			}
		}

		try (Cons.MeasureTime _ = new Cons.MeasureTime("Shuffle keys ...")) {
			Collections.shuffle(_keys);
		}
	}

	private static void ReadAllKeysInRandomOrder() {
		long keys_size = _keys.size();

		try (Cons.MeasureTime _ = new Cons.MeasureTime(
					String.format("Reading %d keys ...", keys_size))) {
			long i = 0;
			for (String k: _keys) {
				ResultSet results = _session.execute("SELECT * FROM standard1 WHERE key=0x" + k);
				//for (Row row : results) {
				//	System.out.format("key=[%s]\n", Tracer.toHex(row.getBytes("key")));
				//}
				i ++;
				if (i % 1000 == 0) {
					System.out.format("\033[1K");
					System.out.format("\033[1G");
					System.out.format("  read %d keys. %.2f%%", i, 100.0 * i / keys_size);
					System.out.flush();
				}
			}
			System.out.format("\n");
		}
	}
	
	public static void main(String[] args) {
		Cluster cluster = null;
		try {
			try (Cons.MeasureTime _ = new Cons.MeasureTime("Connect to Cassandra server ...")) {
				// Connect to the cluster and keyspace "demo"
				cluster = Cluster.builder().addContactPoint("127.0.0.1").build();
				_session = cluster.connect("keyspace1");
			}

			LoadKs1Keys();

			ReadAllKeysInRandomOrder();
		} catch (Exception e) {
			System.out.printf("Exception: %s\n%s\n", e, Util.getStackTrace(e));
		} finally {
			_session.close();

			// close() takes 2.2 secs. exit() to save time. Not sure what's the
			// implication of this.
			System.exit(0);
			cluster.close();
		}
	}
}
