import os
import subprocess
import sys

sys.path.insert(0, "../../util/python")
import Cons

import Conf
import PlotData


def Plot():
	with Cons.MeasureTime("Plotting ..."):
		fn_in = PlotData._fn_plot_data

		fn_out = "data/throughput-avg-w-latency-%s.pdf" % Conf.Get("exp_datetime")
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out
		env["LABEL_Y"] = "Avg write"
		env["EBS_MAG_LABEL_X"] = str(PlotData.Throughput("EBS Mag", "lat_w.avg"))
		env["EBS_MAG_LABEL_Y"] = str(PlotData.Latency("EBS Mag", "lat_w.avg", "lat_w.avg"))
		env["EBS_SSD_LABEL_X"] = str(PlotData.Throughput("EBS SSD GP2", "lat_w.avg"))
		env["EBS_SSD_LABEL_Y"] = str(PlotData.Latency("EBS SSD GP2", "lat_w.avg", "lat_w.avg"))
		env["LOCAL_SSD_LABEL_X"] = str(PlotData.Throughput("Local SSD", "lat_w.avg"))
		env["LOCAL_SSD_LABEL_Y"] = str(PlotData.Latency("Local SSD", "lat_w.avg", "lat_w.avg"))
		env["COL_IDX_LATENCY"] = str(6)
		_RunSubp("gnuplot %s/throughput-latency.gnuplot" % os.path.dirname(__file__), env)

		fn_out = "data/throughput-avg-r-latency-%s.pdf" % Conf.Get("exp_datetime")
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out
		env["LABEL_Y"] = "Avg read"
		env["EBS_MAG_LABEL_X"] = str(PlotData.Throughput("EBS Mag", "lat_r.avg"))
		env["EBS_MAG_LABEL_Y"] = str(PlotData.Latency("EBS Mag", "lat_r.avg", "lat_r.avg"))
		env["EBS_SSD_LABEL_X"] = str(PlotData.Throughput("EBS SSD GP2", "lat_r.avg"))
		env["EBS_SSD_LABEL_Y"] = str(PlotData.Latency("EBS SSD GP2", "lat_r.avg", "lat_r.avg"))
		env["LOCAL_SSD_LABEL_X"] = str(PlotData.Throughput("Local SSD", "lat_r.avg"))
		env["LOCAL_SSD_LABEL_Y"] = str(PlotData.Latency("Local SSD", "lat_r.avg", "lat_r.avg"))
		env["COL_IDX_LATENCY"] = str(9)
		_RunSubp("gnuplot %s/throughput-latency.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))

		# TODO: 99th percentile?


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
