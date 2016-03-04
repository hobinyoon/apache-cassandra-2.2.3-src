import math
import os
import subprocess
import sys

sys.path.insert(0, "../../util/python")
import Cons

import ExpData


def Plot():
	_Baseline()


def _Baseline():
	with Cons.MeasureTime("Baseline ..."):
		# Give some room for the top label by multiplying by y_alpha
		y_alpha = 1.18
		y_max = ExpData.LastExpAttr("ebs-mag", "lat_r_avg") * y_alpha
		_Baseline0("Avg write", "lat_w_avg", 6, y_max)
		_Baseline0("Avg read" , "lat_r_avg", 9, y_max)

		y_max = ExpData.LastExpAttr("ebs-mag", "lat_r__99") * y_alpha
		_Baseline0("99th write", "lat_w__99",  8, y_max)
		_Baseline0("99th read" , "lat_r__99", 11, y_max)


def _Baseline0(label_y_prefix, y_metric, col_idx_lat, y_max):
	env = os.environ.copy()
	env["FN_IN_EBS_MAG"] =           "plot-data/ebs-mag"
	env["FN_IN_EBS_SSD"] =           "plot-data/ebs-ssd"
	env["FN_IN_LOCAL_SSD"] =         "plot-data/local-ssd"
	env["FN_IN_LOCAL_SSD_EBS_MAG"] = "plot-data/local-ssd-ebs-mag"
	env["FN_IN_LOCAL_SSD_EBS_SSD"] = "plot-data/local-ssd-ebs-ssd"
	fn_out = "throughput-%s-ebs-mag-ebs-ssd-local-ssd.pdf" % y_metric
	env["FN_OUT"] = fn_out
	env["LABEL_Y"] = label_y_prefix + " latency (ms)"

	env["EBS_MAG_LAST_X"] =   str(ExpData.LastExpAttr("ebs-mag",   "throughput"))
	env["EBS_MAG_LAST_Y"] =   str(ExpData.LastExpAttr("ebs-mag",   y_metric))
	env["EBS_SSD_LAST_X"] =   str(ExpData.LastExpAttr("ebs-ssd",   "throughput"))
	env["EBS_SSD_LAST_Y"] =   str(ExpData.LastExpAttr("ebs-ssd",   y_metric))
	env["LOCAL_SSD_LAST_X"] = str(ExpData.LastExpAttr("local-ssd", "throughput"))
	env["LOCAL_SSD_LAST_Y"] = str(ExpData.LastExpAttr("local-ssd", y_metric))
	env["COL_IDX_LAT"] = str(col_idx_lat)

	env["Y_MAX"] = str(y_max)
	env["X_TICS_INTERVAL"] = str(_TicsInterval(ExpData.LastExpAttr("local-ssd", "throughput") / 1000.0))
	env["Y_TICS_INTERVAL"] = str(_TicsInterval(y_max))

	_RunSubp("gnuplot %s/throughput-latency.gnuplot" % os.path.dirname(__file__), env)
	Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def _RunSubp(cmd, env_, print_cmd=False):
	if print_cmd:
		Cons.P(cmd)
	p = subprocess.Popen(cmd, shell=True, env=env_, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	# communidate() waits for termination
	stdouterr = p.communicate()[0]
	rc = p.returncode
	if rc != 0:
		raise RuntimeError("Error: cmd=[%s] rc=%d stdouterr=[%s]" % (cmd, rc, stdouterr))
	if len(stdouterr) > 0:
		Cons.P(stdouterr)


def _TicsInterval(v_max):
	# Get most-significant digit
	# 1 -> 0.4 : 2 tic marks
	# 2 -> 0.5 : 4 tic marks
	# 3 -> 1   : 3 tic marks
	# 4 -> 2   : 2 tic marks
	# 5 -> 2   : 2 tic marks
	# 6 -> 2   : 3 tic marks
	# 7 -> 2   : 3 tic marks
	# 8 -> 2   : 4 tic marks
	# 9 -> 2   : 4 tic marks
	a = [0.4, 0.5, 1, 2, 2, 2, 2, 4, 2]

	v_max = float(v_max)
	#Cons.P("v_max=%f" % v_max)
	v = v_max
	v_prev = v
	while v > 1.0:
		v_prev = v
		v /= 10.0
	msd = int(v_prev)

	base = math.pow(10, int(math.log10(v_max)))
	ti = a[msd - 1] * base
	#Cons.P("ti=%f" % ti)
	return ti
