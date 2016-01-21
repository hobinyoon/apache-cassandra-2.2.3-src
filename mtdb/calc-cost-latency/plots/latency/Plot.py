import os
import subprocess
import sys

sys.path.insert(0, "../../../util/python")
import Cons

import LoadgenLogReader


def Plot():
	with Cons.MeasureTime("Plotting ..."):
		fn_in = os.path.dirname(__file__) + "/plot-data/" + LoadgenLogReader.LogFilename()
		fn_out = os.path.dirname(__file__) + "/" + LoadgenLogReader.LogFilename() + "-latency.pdf"
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out
		#Cons.P(fn_out)
		_RunSubp("gnuplot %s/latency-by-time.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def _RunSubp(cmd, env_, print_=True):
	if print_:
		Cons.P(cmd)
	p = subprocess.Popen(cmd, shell=True, env=env_, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	# communidate() waits for termination
	stdouterr = p.communicate()[0]
	rc = p.returncode
	if rc != 0:
		raise RuntimeError("Error: cmd=[%s] rc=%d stdouterr=[%s]" % (cmd, rc, stdouterr))
	if len(stdouterr) > 0:
		Cons.P(stdouterr)