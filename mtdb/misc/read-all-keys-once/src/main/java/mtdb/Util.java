package mtdb;

import java.io.File;
import java.io.StringWriter;
import java.io.PrintWriter;
import java.lang.Throwable;

class Util
{
	// http://stackoverflow.com/questions/1149703/how-can-i-convert-a-stack-trace-to-a-string
	public static String getStackTrace(Throwable t) {
		StringWriter sw = new StringWriter();
		PrintWriter pw = new PrintWriter(sw);
		t.printStackTrace(pw);
		return sw.toString();
	}

	public static long getFileSize(String fn) {
		File f = new File(fn);
		if (! f.exists())
			return 0;
		return f.length();
	}
}
