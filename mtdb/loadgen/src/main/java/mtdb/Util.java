package mtdb;

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
}
