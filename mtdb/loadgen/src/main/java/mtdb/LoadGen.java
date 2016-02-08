package mtdb;

public class LoadGen
{
	public static void main(String[] args) {
		try {
			Conf.Init(args);
			if (Conf.mutantsLoadgenOptions.global.fn_test_num_reads_per_obj.length() > 0) {
				NumReadsPerObj.Test();
				return;
			}
			if (Conf.mutantsLoadgenOptions.global.fn_test_obj_ages.length() > 0) {
				ReadTimes.Test();
				return;
			}

			NumReadsPerObj.Init();
			ReadTimes.Init();
			SimTime.Init();

			Reqs.GenWRs();

			if (Conf.mutantsLoadgenOptions.global.fn_dump_wrs.length() > 0) {
				Reqs.DumpWRsForPlot();
			}
			if (Conf.mutantsLoadgenOptions.db.requests) {
				DbCli dbCli = CassCli.GetInstance();
				dbCli.Run();
			}
		} catch (Exception e) {
			System.out.printf("Exception: %s\n%s\n", e, Util.getStackTrace(e));
		}

		// Cassandra Cluster.close() takes too long. A quick hack.
		System.exit(0);
	}
}
