package mtdb;

public class LoadGen
{
	public static void main(String[] args) {
		try {
			Conf.Init(args);
			if (Conf.global.fn_test_num_reads_per_obj.length() > 0) {
				NumReadsPerObj.Test();
				return;
			}
			if (Conf.global.fn_test_obj_ages.length() > 0) {
				ReadTimes.Test();
				return;
			}

			NumReadsPerObj.Init();
			ReadTimes.Init();
			Reqs.GenWRs();

			if (Conf.global.fn_dump_wrs.length() > 0) {
				Reqs.DumpWRsForPlot();
			}
			if (Conf.db.requests) {
				DbCli.Run();
				// TODO: Let CassCli inherit DbCli
				//CassCli.Run();
			}
		} catch (Exception e) {
			System.out.printf("Exception: %s\n%s\n", e, Util.getStackTrace(e));
		}

		// Cassandra Cluster.close() takes too long. A quick and dirty hack.
		System.exit(0);
	}
}
