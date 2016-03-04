import math
import os
import subprocess
import sys

sys.path.insert(0, "../../util/python")
import Cons

import Conf
import ExpData


def Plot():
	_Baseline()


def _Baseline():
	with Cons.MeasureTime("Baseline ..."):
		env = os.environ.copy()
		env["FN_IN_EBS_MAG"] =           "plot-data/ebs-mag"
		env["FN_IN_EBS_SSD"] =           "plot-data/ebs-ssd"
		env["FN_IN_LOCAL_SSD"] =         "plot-data/local-ssd"
		env["FN_IN_LOCAL_SSD_EBS_MAG"] = "plot-data/local-ssd-ebs-mag"
		env["FN_IN_LOCAL_SSD_EBS_SSD"] = "plot-data/local-ssd-ebs-ssd"
		fn_out = "throughput-w-avg-latency-ebs-mag-ebs-ssd-local-ssd.pdf"
		env["FN_OUT"] = fn_out
		env["LABEL_Y"] = "Avg write latency (ms)"

		env["EBS_MAG_LAST_X"] =   str(ExpData.LastExpAttr("ebs-mag",   "throughput"))
		env["EBS_MAG_LAST_Y"] =   str(ExpData.LastExpAttr("ebs-mag",   "lat_w_avg"))
		env["EBS_SSD_LAST_X"] =   str(ExpData.LastExpAttr("ebs-ssd",   "throughput"))
		env["EBS_SSD_LAST_Y"] =   str(ExpData.LastExpAttr("ebs-ssd",   "lat_w_avg"))
		env["LOCAL_SSD_LAST_X"] = str(ExpData.LastExpAttr("local-ssd", "throughput"))
		env["LOCAL_SSD_LAST_Y"] = str(ExpData.LastExpAttr("local-ssd", "lat_w_avg"))

		env["X_TICS_INTERVAL"] = str(_TicsInterval(ExpData.LastExpAttr("local-ssd", "throughput") / 1000.0))
		env["Y_TICS_INTERVAL"] = str(_TicsInterval(ExpData.LastExpAttr("ebs-mag", "lat_w_avg")))

		_RunSubp("gnuplot %s/throughput-latency.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))
		sys.exit(0)

		env["EBS_SSD_LABEL_X"] = str(PlotData.Throughput("EBS SSD GP2", "lat_w.avg"))
		env["EBS_SSD_LABEL_Y"] = str(PlotData.Latency("EBS SSD GP2", "lat_w.avg"))
		env["LOCAL_SSD_LABEL_X"] = str(PlotData.Throughput("Local SSD", "lat_w.avg"))
		env["LOCAL_SSD_LABEL_Y"] = str(PlotData.Latency("Local SSD", "lat_w.avg"))
		env["Y_MAX"] = str(PlotData.MaxLatency("avg"))
		env["COL_IDX_LATENCY"] = str(6)
		aal = PlotData.AvgAvgLat("EBS Mag", "lat_w.avg")
		env["AVG_AVG_LAT_EBS_MAG_X"] = str(aal[0])
		env["AVG_AVG_LAT_EBS_MAG_Y"] = str(aal[1])
		aal = PlotData.AvgAvgLat("EBS SSD GP2", "lat_w.avg")
		env["AVG_AVG_LAT_EBS_SSD_X"] = str(aal[0])
		env["AVG_AVG_LAT_EBS_SSD_Y"] = str(aal[1])
		aal = PlotData.AvgAvgLat("Local SSD", "lat_w.avg")
		env["AVG_AVG_LAT_LOCAL_SSD_X"] = str(aal[0])
		env["AVG_AVG_LAT_LOCAL_SSD_Y"] = str(aal[1])

		#fn_out = "data/throughput-w-99-latency-%s.pdf" % Conf.Get("exp_datetime")
		#env["FN_OUT"] = fn_out
		#env["LABEL_Y"] = "99% write"
		#env["EBS_MAG_LABEL_X"] = str(PlotData.Throughput("EBS Mag", "lat_w._99"))
		#env["EBS_MAG_LABEL_Y"] = str(PlotData.Latency("EBS Mag", "lat_w._99"))
		#env["EBS_SSD_LABEL_X"] = str(PlotData.Throughput("EBS SSD GP2", "lat_w._99"))
		#env["EBS_SSD_LABEL_Y"] = str(PlotData.Latency("EBS SSD GP2", "lat_w._99"))
		#env["LOCAL_SSD_LABEL_X"] = str(PlotData.Throughput("Local SSD", "lat_w._99"))
		#env["LOCAL_SSD_LABEL_Y"] = str(PlotData.Latency("Local SSD", "lat_w._99"))
		#env["Y_MAX"] = str(PlotData.MaxLatency("_99"))
		#env["COL_IDX_LATENCY"] = str(8)
		#_RunSubp("gnuplot %s/throughput-latency.gnuplot" % os.path.dirname(__file__), env)
		#Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))

		fn_out = "data/throughput-r-avg-latency-linear-regression-%s.pdf" % Conf.Get("exp_datetime")
		env["FN_OUT"] = fn_out
		env["LABEL_Y"] = "Avg read"
		env["EBS_MAG_LABEL_X"] = str(PlotData.Throughput("EBS Mag", "lat_r.avg"))
		env["EBS_MAG_LABEL_Y"] = str(PlotData.Latency("EBS Mag", "lat_r.avg"))
		env["EBS_SSD_LABEL_X"] = str(PlotData.Throughput("EBS SSD GP2", "lat_r.avg"))
		env["EBS_SSD_LABEL_Y"] = str(PlotData.Latency("EBS SSD GP2", "lat_r.avg"))
		env["LOCAL_SSD_LABEL_X"] = str(PlotData.Throughput("Local SSD", "lat_r.avg"))
		env["LOCAL_SSD_LABEL_Y"] = str(PlotData.Latency("Local SSD", "lat_r.avg"))
		env["Y_MAX"] = str(PlotData.MaxLatency("avg"))
		env["COL_IDX_LATENCY"] = str(9)
		aal = PlotData.AvgAvgLat("EBS Mag", "lat_r.avg")
		env["AVG_AVG_LAT_EBS_MAG_X"] = str(aal[0])
		env["AVG_AVG_LAT_EBS_MAG_Y"] = str(aal[1])
		aal = PlotData.AvgAvgLat("EBS SSD GP2", "lat_r.avg")
		env["AVG_AVG_LAT_EBS_SSD_X"] = str(aal[0])
		env["AVG_AVG_LAT_EBS_SSD_Y"] = str(aal[1])
		aal = PlotData.AvgAvgLat("Local SSD", "lat_r.avg")
		env["AVG_AVG_LAT_LOCAL_SSD_X"] = str(aal[0])
		env["AVG_AVG_LAT_LOCAL_SSD_Y"] = str(aal[1])
		_RunSubp("gnuplot %s/throughput-latency.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))

		#fn_out = "data/throughput-r-99-latency-%s.pdf" % Conf.Get("exp_datetime")
		#env["FN_OUT"] = fn_out
		#env["LABEL_Y"] = "99% read"
		#env["EBS_MAG_LABEL_X"] = str(PlotData.Throughput("EBS Mag", "lat_r._99"))
		#env["EBS_MAG_LABEL_Y"] = str(PlotData.Latency("EBS Mag", "lat_r._99"))
		#env["EBS_SSD_LABEL_X"] = str(PlotData.Throughput("EBS SSD GP2", "lat_r._99"))
		#env["EBS_SSD_LABEL_Y"] = str(PlotData.Latency("EBS SSD GP2", "lat_r._99"))
		#env["LOCAL_SSD_LABEL_X"] = str(PlotData.Throughput("Local SSD", "lat_r._99"))
		#env["LOCAL_SSD_LABEL_Y"] = str(PlotData.Latency("Local SSD", "lat_r._99"))
		#env["Y_MAX"] = str(PlotData.MaxLatency("_99"))
		#env["COL_IDX_LATENCY"] = str(11)
		#_RunSubp("gnuplot %s/throughput-latency.gnuplot" % os.path.dirname(__file__), env)
		#Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


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


def _TicsInterval(v_max):
	# Get most-significant digit
	# 1 -> 0.2 : 5 tic marks
	# 2 -> 0.5 : 4 tic marks
	# 3 -> 1   : 3 tic marks
	# 4 -> 1   : 4 tic marks
	# 5 -> 1   : 5 tic marks
	# 6 -> 2   : 3 tic marks
	# 7 -> 2   : 3 tic marks
	# 8 -> 2   : 4 tic marks
	# 9 -> 2   : 4 tic marks

	v_max = float(v_max)
	v = v_max
	v_prev = v
	while v > 1.0:
		v_prev = v
		v /= 10.0
	msd = int(v_prev)

	base = math.pow(10, int(math.log10(v_max)))
	if msd == 1:
		return 0.2 * base
	elif msd == 2:
		return 0.5 * base
	elif msd == 3:
		return 1.0 * base
	elif msd == 4:
		return 1.0 * base
	elif msd == 5:
		return 1.0 * base
	elif msd == 6:
		return 2.0 * base
	elif msd == 7:
		return 2.0 * base
	elif msd == 8:
		return 2.0 * base
	else:
		return 2.0 * base
