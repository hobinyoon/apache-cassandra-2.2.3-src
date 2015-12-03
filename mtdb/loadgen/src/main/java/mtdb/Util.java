package mtdb;

import java.io.File;
import java.io.StringWriter;
import java.io.PrintWriter;
import java.lang.Throwable;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

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

	public static String BuildHeader(String fmt, int leftMargin, String... args) {
		// Get the end position of column header. fmt specifiers consist of float,
		// integer, or string
		Pattern p = Pattern.compile("%(([-+]?[0-9]*\\.?[0-9]*f)|([-+]?[0-9]*d)|([-+]?[0-9]*s))");
		Matcher m = p.matcher(fmt);
		List<Integer> nameEndPos = new ArrayList();
		int ep = leftMargin;
		while (m.find()) {
			// m.group() returns for example %5.1f
			//
			// remove all characters from .
			//   .replaceAll("\\..*", "")
			// remove all non-numeric characters
			//   .replaceAll("\\D", "")

			int width = Integer.parseInt(m.group().substring(1).replaceAll("\\..*", "").replaceAll("\\D", ""));
			// System.out.printf("[%s] %d\n", m.group(), width);

			if (ep != leftMargin)
				ep ++;
			ep += width;
			nameEndPos.add(ep);
		}
		//System.out.printf("nameEndPos:\n");
		//for (int i: nameEndPos)
		//	System.out.printf("  %d\n", i);
		//System.out.printf("args:\n");
		//for (String s: args)
		//	System.out.printf("  %s\n", s);

		StringBuilder colmneNamesFlat = new StringBuilder("#");
		for (String s: args)
			colmneNamesFlat.append(" ").append(s);

		// Header lines
		List<StringBuilder> headerLines = new ArrayList();
		for (int i = 0; i < args.length; i ++) {
			boolean fit = false;
			for (StringBuilder hl: headerLines) {
				if (hl.length() + 1 + args[i].length() > nameEndPos.get(i))
					continue;

				while (hl.length() + 1 + args[i].length() < nameEndPos.get(i))
					hl.append(" ");
				hl.append(" ").append(args[i]);
				fit = true;
				break;
			}
			if (fit)
				continue;

			StringBuilder hl = new StringBuilder("#");
			while (hl.length() + 1 + args[i].length() < nameEndPos.get(i))
				hl.append(" ");
			hl.append(" ").append(args[i]);
			headerLines.add(hl);
		}
		//System.out.printf("headerLines:\n");
		//for (StringBuilder hl: headerLines)
		//	System.out.printf("  %s\n", hl);

		// Indices for column headers starting from 1 for easy gnuplot indexing
		List<StringBuilder> headerLineIndices = new ArrayList();
		for (int i = 0; i < args.length; i ++) {
			String idxstr = Integer.toString(i + 1);
			boolean fit = false;
			for (StringBuilder hli: headerLineIndices) {
				if (hli.length() + 1 + idxstr.length() > nameEndPos.get(i))
					continue;

				while (hli.length() + 1 + idxstr.length() < nameEndPos.get(i))
					hli.append(" ");
				hli.append(" ").append(idxstr);
				fit = true;
				break;
			}
			if (fit)
				continue;

			StringBuilder hli = new StringBuilder("#");
			while (hli.length() + 1 + idxstr.length() < nameEndPos.get(i))
				hli.append(" ");
			hli.append(" ").append(idxstr);
			headerLineIndices.add(hli);
		}
		//System.out.printf("headerLineIndices:\n");
		//for (StringBuilder hli: headerLineIndices)
		//	System.out.printf("  %s\n", hli);

		StringBuilder header = new StringBuilder(colmneNamesFlat);
		header.append("\n#");

		for (StringBuilder l: headerLines)
			header.append("\n").append(l);
		for (StringBuilder l: headerLineIndices)
			header.append("\n").append(l);

		return header.toString();
	}
}
