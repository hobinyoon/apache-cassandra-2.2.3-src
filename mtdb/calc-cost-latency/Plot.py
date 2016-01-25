import os
import subprocess
import sys

sys.path.insert(0, "../util/python")
import Cons

import CassLogReader
import LoadgenLogReader
import StorageSizeByTimePlotDataGenerator
import TabletAccessesTimelinePlotDataGenerator
import TabletMinMaxTimestampsTimelinePlotDataGenerator


def Latency():
	with Cons.MeasureTime("Plotting latency by time ..."):
		fn_in = LoadgenLogReader._fn_plot_data
		fn_out = os.path.dirname(__file__) + "/" + LoadgenLogReader.LogFilename() + "-latency-by-time.pdf"
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out
		_RunSubp("gnuplot %s/latency-by-time.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def StorageSize():
	with Cons.MeasureTime("Plotting storage size by time ..."):
		fn_in = StorageSizeByTimePlotDataGenerator._fn_plot_data
		fn_out = os.path.dirname(__file__) + "/" + LoadgenLogReader.LogFilename() + "-storage-size-by-time.pdf"
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out
		_RunSubp("gnuplot %s/storage-size-by-time.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def TabletAccessesTimeline():
	with Cons.MeasureTime("Plotting tablet accesses timeline ..."):
		fn_in_cd = TabletAccessesTimelinePlotDataGenerator._fn_plot_data_tablet_timeline_created_deleted
		fn_in_ac = TabletAccessesTimelinePlotDataGenerator._fn_plot_data_tablet_access_counts_by_time
		fn_out = os.path.dirname(__file__) + "/" + LoadgenLogReader.LogFilename() + "-tablet-accesses-timeline.pdf"
		env = os.environ.copy()
		env["FN_IN_CD"] = fn_in_cd
		env["FN_IN_AC"] = fn_in_ac
		env["FN_OUT"] = fn_out
		_RunSubp("gnuplot %s/tablet-accesses-timeline.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def TabletMinMaxTimestampsTimeline():
	with Cons.MeasureTime("Plotting tablet min/max timestamps timeline ..."):
		fn_in = TabletMinMaxTimestampsTimelinePlotDataGenerator._fn_plot_data
		fn_out = os.path.dirname(__file__) + "/" + LoadgenLogReader.LogFilename() + "-tablet-min-max-timestamps-timeline.pdf"
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out
		_RunSubp("gnuplot %s/tablet-min-max-timestamps-timeline.gnuplot" % os.path.dirname(__file__), env)
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
