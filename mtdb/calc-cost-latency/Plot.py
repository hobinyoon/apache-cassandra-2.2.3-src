import os
import subprocess
import sys

sys.path.insert(0, "../util/python")
import Cons

import CassLogReader
import Desc
import LoadgenLogReader
import StorageSizeByTimePlotDataGenerator
import TabletAccessesForTabletMinMaxTimestampsTimelinePlotDataGenerator
import TabletAccessesForTabletSizeTimelinePlotDataGenerator
import TabletMinMaxTimestampsTimelinePlotDataGenerator
import TabletSizeTimelinePlotDataGenerator


def Latency():
	with Cons.MeasureTime("Plotting latency by time ..."):
		fn_in = LoadgenLogReader._fn_plot_data
		fn_out = os.path.dirname(__file__) + "/" + Desc.ExpDatetime() + "-latency-by-time.pdf"
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out
		_RunSubp("gnuplot %s/latency-by-time.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def StorageSize():
	with Cons.MeasureTime("Plotting storage size by time ..."):
		fn_in = StorageSizeByTimePlotDataGenerator._fn_plot_data
		fn_out = os.path.dirname(__file__) + "/" + Desc.ExpDatetime() + "-storage-size-by-time.pdf"
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out
		_RunSubp("gnuplot %s/storage-size-by-time.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def TabletSizesTimeline():
	with Cons.MeasureTime("Plotting tablet sizes timeline ..."):
		fn_in_cd = TabletSizeTimelinePlotDataGenerator._fn_plot_data
		fn_in_ac = TabletAccessesForTabletSizeTimelinePlotDataGenerator._fn_plot_data
		fn_out = os.path.dirname(__file__) + "/" + Desc.ExpDatetime() + "-tablet-sizes-timeline.pdf"
		env = os.environ.copy()
		env["FN_IN_CD"] = fn_in_cd
		env["FN_IN_AC"] = fn_in_ac
		env["FN_OUT"] = fn_out
		env["DESC"] = Desc.GnuplotDesc()
		env["MIN_TABLET_SIZE"] = str(TabletSizeTimelinePlotDataGenerator.MinTabletSize())
		env["MAX_NEEDTO_READ_DATAFILE_PER_DAY"] = str(int(round(TabletAccessesForTabletSizeTimelinePlotDataGenerator.MaxNumNeedtoReadDatafilePerDay(), 0)))
		_RunSubp("gnuplot %s/tablet-sizes-timeline.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def TabletMinMaxTimestampsTimeline():
	with Cons.MeasureTime("Plotting tablet min/max timestamps timeline ..."):
		fn_in_ts = TabletMinMaxTimestampsTimelinePlotDataGenerator._fn_plot_data
		fn_in_ac = TabletAccessesForTabletMinMaxTimestampsTimelinePlotDataGenerator._fn_plot_data
		fn_out = os.path.dirname(__file__) + "/" + Desc.ExpDatetime() + "-tablet-min-max-timestamps-timeline.pdf"
		env = os.environ.copy()
		env["FN_IN_TS"] = fn_in_ts
		env["FN_IN_AC"] = fn_in_ac
		env["FN_OUT"] = fn_out
		env["DESC"] = Desc.GnuplotDesc()
		env["MAX_NUM_ACCESSES"] = str(int(round(TabletAccessesForTabletMinMaxTimestampsTimelinePlotDataGenerator.NumToTime.max_num_bf_positives_per_day, 0)))
		env["MIN_TIMESTAMP_RANGE"] = str(int(TabletAccessesForTabletMinMaxTimestampsTimelinePlotDataGenerator.NumToTime.min_timestamp_range.total_seconds()))
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
