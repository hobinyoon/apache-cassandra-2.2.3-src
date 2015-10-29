package mtdb;

// Console output utility
// - Not thread-safe. Doesn't guarantee ordering. It is by design

public class Cons
{
	public static int _ind_len = 0;
	public static StringBuilder _ind = new StringBuilder();

	public static void P(String msg) {
		if (_ind_len > 0) {
			System.out.println(msg.replaceAll("(?m)^", _ind.toString()));
		} else {
			System.out.println(msg);
		}

		//StringBuilder sb = new StringBuilder(200);
		//for (int i = 0; i < _ind_len; i ++) {
		//	sb.append(" ");
		//}
		//sb.append(msg);
		//System.out.println(sb);
	}

	public static class MeasureTime implements AutoCloseable
	{
		//StackTraceElement _ste;
		long _start_time;

		public MeasureTime(String name)
		{
			//_ste = Thread.currentThread().getStackTrace()[2];
			P(name);
			_ind_len += 2;
			_ind.append("  ");
			_start_time = System.nanoTime();
		}

		@Override
		public void close()
		{
			double duration = (System.nanoTime() - _start_time) / 1000000.0;
			P(String.format("%.0f ms", duration));
			_ind_len -=2;
			_ind.setLength(_ind_len);

			//StringBuilder sb = new StringBuilder();
			//sb.append(Thread.currentThread().getId());
			//sb.append(" ");
			//sb.append(_ste.getClassName());
			//sb.append(".");
			//sb.append(_ste.getMethodName());
			//sb.append("()");
			//sb.append(" [");
			//sb.append(_ste.getFileName());
			//sb.append(":");
			//sb.append(_ste.getLineNumber());
			//sb.append("]");
			//System.err.printf("%s %f sec\n", sb.toString(), duration);
		}
	}
}
