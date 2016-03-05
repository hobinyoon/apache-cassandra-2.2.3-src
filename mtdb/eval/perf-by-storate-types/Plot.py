import math
import os
import subprocess
import sys

sys.path.insert(0, "../../util/python")
import Cons

import ExpData


def Plot():
	_ES_LS_LSES()

	# TODO
	#_ReqrateVsMetrics()
	#_ThroughputVsLatency()


# TODO: def _EM_LS_LSEM():

def _ES_LS_LSES():
	_ES_LS_LSES0_disk("read_kb" , 0, None)
	_ES_LS_LSES0_disk("read_io" , 1, None)
	_ES_LS_LSES0_disk("write_kb", 2, None)
	_ES_LS_LSES0_disk("write_io", 3, None)
	_ES_LS_LSES0_disk("rw_size" , 4, None)
	_ES_LS_LSES0_disk("q_len"   , 5, None)
	_ES_LS_LSES0_disk("wait"    , 6, None)
	_ES_LS_LSES0_disk("svc_time", 7, None)
	_ES_LS_LSES0_disk("util"    , 8, 100)

	# TODO: Dev plot layout is different from CPU, or network layout


def _ES_LS_LSES0_disk(y_metric, col_idx, y_max = None):
	bases = [18, 27, 36]
	devs = ["xvda", "xvdb", "xvdd"]
	_ES_LS_LSES0_disk0(
			y_metric
			, "disk_%s_%s" % (devs[0], y_metric)
			, "disk_%s_%s" % (devs[1], y_metric)
			, bases[0] + col_idx
			, bases[1] + col_idx,
			y_max)


def _ES_LS_LSES0_disk0(y_metric, y_metric0, y_metric1, col_idx0, col_idx1, y_max = None):
	egns = ["ebs-ssd", "local-ssd", "local-ssd-ebs-ssd"]
	what_to_compare = "-vs-".join(egns)

	fn_out = "plot-data/%s.num-reqs-vs-%s.pdf" % (what_to_compare, y_metric)

	env = os.environ.copy()
	env["FN_IN"] = " ".join(("plot-data/%s" % egns[i]) for i in range(len(egns)))
	env["TITLE"] = "disk " + y_metric.replace("_", "\\_")
	env["LEGEND_LABELS"] = "ES LS LSES"
	env["FN_OUT"] = fn_out
	env["LABEL_Y_0"] = "EBS SSD"
	env["LABEL_Y_1"] = "Local SSD"
	env["COL_IDX_0"] = str(col_idx0)
	env["COL_IDX_1"] = str(col_idx1)

	if y_max == None:
		y_max = max(ExpData.MaxExpAttr(y_metric0), ExpData.MaxExpAttr(y_metric1))
	y_alpha = 1.0
	y_max *= y_alpha
	env["Y_MAX"] = str(y_max)
	env["Y_TICS_INTERVAL"] = str(_TicsInterval(y_max))

	_RunSubp("gnuplot %s/3way.num-reqs-vs-dev-metric.gnuplot" % os.path.dirname(__file__), env)
	Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def _ReqrateVsMetrics():
	with Cons.MeasureTime("Resource usage by storage types ..."):
		_ReqrateVsMetric0("throughput", 5)
		_ReqrateVsMetric0("lat_w_avg",  6)
		_ReqrateVsMetric0("lat_w__99",  8)
		_ReqrateVsMetric0("lat_r_avg",  9)
		_ReqrateVsMetric0("lat_r__99", 11)

		_ReqrateVsMetric0("cpu_user", 15)
		_ReqrateVsMetric0("cpu_sys",  16)
		_ReqrateVsMetric0("cpu_wait", 17)

		bases = [18, 27, 36]
		devs = ["xvda", "xvdb", "xvdd"]
		for i in range(len(bases)):
			_ReqrateVsMetric0("disk_%s_read_kb"  % devs[i], bases[i] + 0)
			_ReqrateVsMetric0("disk_%s_read_io"  % devs[i], bases[i] + 1)
			_ReqrateVsMetric0("disk_%s_write_kb" % devs[i], bases[i] + 2)
			_ReqrateVsMetric0("disk_%s_write_io" % devs[i], bases[i] + 3)
			_ReqrateVsMetric0("disk_%s_rw_size"  % devs[i], bases[i] + 4)
			_ReqrateVsMetric0("disk_%s_q_len"    % devs[i], bases[i] + 5)
			_ReqrateVsMetric0("disk_%s_wait"     % devs[i], bases[i] + 6)
			_ReqrateVsMetric0("disk_%s_svc_time" % devs[i], bases[i] + 7)
			_ReqrateVsMetric0("disk_%s_util"     % devs[i], bases[i] + 8, y_max=100)

		_ReqrateVsMetric0("net_kb_in", 45)
		_ReqrateVsMetric0("net_kb_out", 46)


def _ReqrateVsMetric0(y_metric, col_idx_lat, y_max = None):
	egns = ["ebs-mag", "local-ssd-ebs-mag", "ebs-ssd", "local-ssd", "local-ssd-ebs-ssd"]
	# gnuplot word() doesn't work with new line
	#labels = ["EBS\\nMag", "LS+EM", "EBS\\nSSD", "Local\\nSSD", "LS+ES"]
	labels = ["EM", "LS+EM", "ES", "LS", "LS+ES"]

	fn_out = "plot-data/num-reqs-vs-%s-by-storage-types.pdf" % (y_metric)

	env = os.environ.copy()
	env["FN_IN"] = " ".join(("plot-data/%s" % egns[i]) for i in range(len(egns)))
	env["LABELS"] = " ".join(l for l in labels)
	env["FN_OUT"] = fn_out
	env["LABEL_Y"] = y_metric.replace("_", "\\_")
	env["COL_IDX_LAT"] = str(col_idx_lat)

	if y_max == None:
		y_max = ExpData.MaxExpAttr(y_metric)
	y_alpha = 1.0
	y_max *= y_alpha
	env["Y_MAX"] = str(y_max)
	env["Y_TICS_INTERVAL"] = str(_TicsInterval(y_max))

	_RunSubp("gnuplot %s/num-reqs-vs-metric.gnuplot" % os.path.dirname(__file__), env)
	Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def _ThroughputVsLatency():
	_Baseline()
	_Mutants()


def _Baseline():
	with Cons.MeasureTime("Baseline throughput vs latency ..."):
		# Give some room for the top label with y_alpha
		y_alpha = 1.18

		egns = ["ebs-mag", "ebs-ssd", "local-ssd"]
		labels = ["EBS\\nMag", "EBS\\nSSD", "Local\\nSSD"]
		y_max = ExpData.LastExpAttr("ebs-mag", "lat_r_avg") * y_alpha
		_ThroughputVsLatency0(egns, labels, "baseline", "Avg write", "lat_w_avg", 6, y_max)
		_ThroughputVsLatency0(egns, labels, "baseline", "Avg read" , "lat_r_avg", 9, y_max)

		y_max = ExpData.LastExpAttr("ebs-mag", "lat_r__99") * y_alpha
		_ThroughputVsLatency0(egns, labels, "baseline", "99th write", "lat_w__99",  8, y_max)
		_ThroughputVsLatency0(egns, labels, "baseline", "99th read" , "lat_r__99", 11, y_max)


def _Mutants():
	with Cons.MeasureTime("Mutants throughput vs latency ..."):
		y_alpha = 1.18

		egns = ["ebs-mag", "local-ssd-ebs-mag", "local-ssd"]
		labels = ["EBS\\nMag", "LS+EM", "Local\\nSSD"]
		y_max = ExpData.LastExpAttr("ebs-mag", "lat_r_avg") * y_alpha
		_ThroughputVsLatency0(egns, labels, "local-ssd-ebs-mag", "Avg write", "lat_w_avg", 6, y_max)
		_ThroughputVsLatency0(egns, labels, "local-ssd-ebs-mag", "Avg read" , "lat_r_avg", 9, y_max)

		egns = ["ebs-ssd", "local-ssd-ebs-ssd", "local-ssd"]
		labels = ["EBS\\nSSD", "LS+ES", "Local\\nSSD"]
		y_max = ExpData.LastExpAttr("ebs-ssd", "lat_r_avg") * y_alpha
		_ThroughputVsLatency0(egns, labels, "local-ssd-ebs-ssd", "Avg write", "lat_w_avg", 6, y_max)
		_ThroughputVsLatency0(egns, labels, "local-ssd-ebs-ssd", "Avg read" , "lat_r_avg", 9, y_max)


def _ThroughputVsLatency0(egns, labels, fn0, label_y_prefix, y_metric, col_idx_lat, y_max):
	env = os.environ.copy()

	for i in range(len(egns)):
		k = "FN_IN_%d" % i
		v = "plot-data/%s" % egns[i]
		env[k] = v

	fn_out = "plot-data/throughput-%s-%s.pdf" % (fn0, y_metric)

	env["FN_OUT"] = fn_out
	env["LABEL_Y"] = label_y_prefix + " latency (ms)"

	for i in range(len(egns)):
		egn = egns[i]
		k = "LAST_X_%d" % i
		v = ExpData.LastExpAttr(egn, "throughput")
		env[k] = str(v)

		k = "LAST_Y_%d" % i
		v = ExpData.LastExpAttr(egn, y_metric)
		env[k] = str(v)

	for i in range(len(labels)):
		egn = egns[i]
		k = "LABEL_%d" % i
		v = labels[i]
		env[k] = v

	env["COL_IDX_LAT"] = str(col_idx_lat)

	env["Y_MAX"] = str(y_max)
	env["X_TICS_INTERVAL"] = str(_TicsInterval(ExpData.LastExpAttr(egns[2], "throughput") / 1000.0))
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
	# 1 -> 0.5 : 2 tic marks
	# 2 -> 1   : 2 tic marks
	# 3 -> 1   : 3 tic marks
	# 4 -> 2   : 2 tic marks
	# 5 -> 2   : 2 tic marks
	# 6 -> 2   : 3 tic marks
	# 7 -> 2   : 3 tic marks
	# 8 -> 2   : 4 tic marks
	# 9 -> 2   : 4 tic marks
	a = [0.5, 1, 1, 2, 2, 2, 2, 4, 2]

	v_max = float(v_max)
	v = v_max
	if v >= 1.0:
		v_prev = v
		while v >= 1.0:
			v_prev = v
			v /= 10.0
		msd = int(v_prev)
	else:
		while v < 1.0:
			v *= 10.0
		msd = int(v)

	base = math.pow(10, math.floor(math.log10(v_max)))
	ti = a[msd - 1] * base
	return ti
