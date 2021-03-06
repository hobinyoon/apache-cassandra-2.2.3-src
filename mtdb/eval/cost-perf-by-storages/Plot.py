import math
import os
import subprocess
import sys

sys.path.insert(0, "../../util/python")
import Cons

import Conf
import ExpData


def Plot():
	_ThroughputVsLatency()

	# Request rates vs all metrics. Cold-only vs. hot-only vs. Mutants.
	_ES_LS_LSES()


# TODO: def _EM_LS_LSEM():

def _ES_LS_LSES():
	_ES_LS_LSES0_metric("throughput",  5)
	_ES_LS_LSES0_metric("lat_w_avg" ,  6)
	_ES_LS_LSES0_metric("lat_w__99" ,  8)
	_ES_LS_LSES0_metric("lat_r_avg" ,  9)
	_ES_LS_LSES0_metric("lat_r__99" , 11)

	_ES_LS_LSES0_cpu()
	_ES_LS_LSES0_network()
	_ES_LS_LSES0_disk("read_kb" , 0)
	_ES_LS_LSES0_disk("read_io" , 1)
	_ES_LS_LSES0_disk("write_kb", 2)
	_ES_LS_LSES0_disk("write_io", 3)
	_ES_LS_LSES0_disk("rw_size" , 4)
	_ES_LS_LSES0_disk("q_len"   , 5)
	_ES_LS_LSES0_disk("wait"    , 6)
	_ES_LS_LSES0_disk("svc_time", 7)
	_ES_LS_LSES0_disk("util"    , 8, 100)

	_ES_LS_LSES0_storage_cost()
	# TODO: storage size. Not sure if this gives you much insight
	#_ES_LS_LSES0_storage_size()


def _ES_LS_LSES0_metric(y_metric, col_idx):
	egns = ["ebs-ssd", "local-ssd", "local-ssd-ebs-ssd"]
	what_to_compare = "-vs-".join(egns)

	fn_out = "plot-data/%s--num-reqs-vs-%s.pdf" % (what_to_compare, y_metric)

	env = os.environ.copy()

	fn_ins = []
	for egn in egns:
		fn_ins.append("plot-data/%s" % Conf.Get("exp-result")[egn]["fn"])
	env["FN_INS"] = " ".join(fn_ins)

	env["LEGEND_LABELS"] = "ES LS LSES"
	env["FN_OUT"] = fn_out
	env["LABEL"] = y_metric.replace("_", "\\_")
	env["COL_IDX"] = str(col_idx)

	y_max = ExpData.MaxExpAttr(y_metric, egns = egns)
	env["Y_MAX"] = str(y_max)
	env["Y_TICS_INTERVAL"] = str(_TicsInterval(y_max))

	_RunSubp("gnuplot %s/3way.num-reqs-vs-metric.gnuplot" % os.path.dirname(__file__), env)
	Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def _ES_LS_LSES0_cpu():
	col_idx = [15, 16, 17]
	egns = ["ebs-ssd", "local-ssd", "local-ssd-ebs-ssd"]
	what_to_compare = "-vs-".join(egns)

	y_metric = "cpu"
	fn_out = "plot-data/%s--num-reqs-vs-%s.pdf" % (what_to_compare, y_metric)

	env = os.environ.copy()

	fn_ins = []
	for egn in egns:
		fn_ins.append("plot-data/%s" % Conf.Get("exp-result")[egn]["fn"])
	env["FN_INS"] = " ".join(fn_ins)

	env["LEGEND_LABELS"] = "ES LS LSES"
	env["FN_OUT"] = fn_out
	env["LABELS"] = "cpu_user cpy_sys cpu_wait".replace("_", "\\_")
	env["COL_IDX"] = " ".join(str(i) for i in col_idx)

	y_max = 350
	env["Y_MAX"] = str(y_max)
	env["Y_TICS_INTERVAL"] = str(_TicsInterval(y_max))

	_RunSubp("gnuplot %s/3way.num-reqs-vs-cpu.gnuplot" % os.path.dirname(__file__), env)
	Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def _ES_LS_LSES0_network():
	col_idx = [45, 46]
	egns = ["ebs-ssd", "local-ssd", "local-ssd-ebs-ssd"]
	what_to_compare = "-vs-".join(egns)

	y_metric = "network"
	fn_out = "plot-data/%s--num-reqs-vs-%s.pdf" % (what_to_compare, y_metric)

	env = os.environ.copy()

	fn_ins = []
	for egn in egns:
		fn_ins.append("plot-data/%s" % Conf.Get("exp-result")[egn]["fn"])
	env["FN_INS"] = " ".join(fn_ins)

	env["LEGEND_LABELS"] = "ES LS LSES"
	env["FN_OUT"] = fn_out
	env["LABELS"] = "kB_in kB_out".replace("_", "\\_")
	env["COL_IDX"] = " ".join(str(i) for i in col_idx)

	y_max = max(ExpData.MaxExpAttr("net_kb_in"), ExpData.MaxExpAttr("net_kb_out"))
	env["Y_MAX"] = str(y_max)
	env["Y_TICS_INTERVAL"] = str(_TicsInterval(y_max))

	_RunSubp("gnuplot %s/3way.num-reqs-vs-network.gnuplot" % os.path.dirname(__file__), env)
	Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


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

	fn_out = "plot-data/%s--num-reqs-vs-disk-%s.pdf" % (what_to_compare, y_metric)

	env = os.environ.copy()

	fn_ins = []
	for egn in egns:
		fn_ins.append("plot-data/%s" % Conf.Get("exp-result")[egn]["fn"])
	env["FN_INS"] = " ".join(fn_ins)

	env["TITLE"] = "disk " + y_metric.replace("_", "\\_")
	env["LEGEND_LABELS"] = "ES LS LSES"
	env["FN_OUT"] = fn_out
	env["LABEL_Y_0"] = "EBS SSD"
	env["LABEL_Y_1"] = "Local SSD"
	env["COL_IDX_0"] = str(col_idx0)
	env["COL_IDX_1"] = str(col_idx1)

	if y_max == None:
		y_max = max(ExpData.MaxExpAttr(y_metric0), ExpData.MaxExpAttr(y_metric1))
	env["Y_MAX"] = str(y_max)
	env["Y_TICS_INTERVAL"] = str(_TicsInterval(y_max))

	_RunSubp("gnuplot %s/3way.num-reqs-vs-disk.gnuplot" % os.path.dirname(__file__), env)
	Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def _ES_LS_LSES0_storage_cost():
	col_idx = [49, 50]
	egns = ["ebs-ssd", "local-ssd", "local-ssd-ebs-ssd"]
	what_to_compare = "-vs-".join(egns)

	y_metric = "storage-cost"
	fn_out = "plot-data/%s--num-reqs-vs-%s.pdf" % (what_to_compare, y_metric)

	env = os.environ.copy()

	fn_ins = []
	for egn in egns:
		fn_ins.append("plot-data/%s" % Conf.Get("exp-result")[egn]["fn"])
	env["FN_INS"] = " ".join(fn_ins)

	env["LEGEND_LABELS"] = "ES LS LSES"
	env["FN_OUT"] = fn_out
	env["COL_IDX"] = " ".join(str(i) for i in col_idx)

	y_max = ExpData.MaxExpAttr("hot_stg_cost") + ExpData.MaxExpAttr("cold_stg_cost")
	env["Y_MAX"] = str(y_max)
	env["Y_TICS_INTERVAL"] = str(_TicsInterval(y_max))

	_RunSubp("gnuplot %s/3way.num-reqs-vs-storage-cost.gnuplot" % os.path.dirname(__file__), env)
	Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def _ThroughputVsLatency():
	with Cons.MeasureTime("Baseline throughput vs latency ..."):
		_ThroughputVsLatency0(["ebs-mag", "ebs-ssd", "local-ssd"])
		_ThroughputVsLatency0(["ebs-mag", "local-ssd-ebs-mag", "local-ssd"])
		_ThroughputVsLatency0(["ebs-ssd", "local-ssd-ebs-ssd", "local-ssd"])
		_ThroughputVsLatency0(["local-ssd", "local-ssd-local-ssd"])


def _WhatToCompareShortName(egns):
	short_names = []
	for egn in egns:
		short_names.append(Conf.Get("exp-result")[egn]["short-name"])
	return "-".join(short_names)


def _ThroughputVsLatency0(egns):
	_ThroughputVsLatency1(egns, "Avg write" , "lat_w_avg",  6, y_max = ExpData.MaxExpAttr("lat_r_avg", egns))
	_ThroughputVsLatency1(egns, "Avg read"  , "lat_r_avg",  9)
	_ThroughputVsLatency1(egns, "99th write", "lat_w__99",  8, y_max = ExpData.MaxExpAttr("lat_r__99", egns))
	_ThroughputVsLatency1(egns, "99th read" , "lat_r__99", 11)


def _ThroughputVsLatency1(egns, label_y_prefix, y_metric, col_idx_lat, y_max = None):
	env = os.environ.copy()

	fn_ins = []
	for egn in egns:
		fn_ins.append("plot-data/%s" % Conf.Get("exp-result")[egn]["fn"])
	env["FN_INS"] = " ".join(fn_ins)

	# latex doesn't work with dot other than before the file extension
	fn_out = "plot-data/%s--throughput-vs-%s.pdf" % (_WhatToCompareShortName(egns), y_metric)

	env["FN_OUT"] = fn_out
	#env["LABEL_Y"] = label_y_prefix + " latency (ms)"
	env["LABEL_Y"] = label_y_prefix + " (ms)"

	#last_x = []
	#last_y = []
	#for egn in egns:
	#	last_x.append(ExpData.LastExpAttr(egn, "throughput"))
	#	last_y.append(ExpData.LastExpAttr(egn, y_metric))
	#env["LAST_X"] = " ".join(str(i) for i in last_x)
	#env["LAST_Y"] = " ".join(str(i) for i in last_y)

	# Experiment group names
	env["EGNS"] = " ".join(egns)

	env["COL_METRIC"] = str(col_idx_lat)

	if y_max == None:
		y_max = ExpData.MaxExpAttr(y_metric, egns)

	env["Y_MAX"] = str(y_max)
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
