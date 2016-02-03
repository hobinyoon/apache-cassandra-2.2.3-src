import os
import sys

sys.path.insert(0, "../util/python")
import Cons
import Util

import CassLogReader
import Desc
import TabletSizeTimelinePlotDataGenerator

_fn_plot_data = None
_id_events = {}
_max_num_needto_read_datafile_per_day = 0


def Gen():
	with Cons.MeasureTime("Generating tablet accesses timeline plot data ..."):
		for l in CassLogReader._logs:
			_BuildIdEventsMap(l)
		_WriteToFile()


def MaxNumNeedtoReadDatafilePerDay():
	return _max_num_needto_read_datafile_per_day


class Events:
	def __init__(self):
		self.time_cnts = {}

	def AddAccStat(self, simulated_time, tablet_acc_stat):
		# tablet_acc_stat is of type EventAccessStat.AccStat
		self.time_cnts[simulated_time] = tablet_acc_stat

	def __str__(self):
		return "Events: " + ", ".join("%s: %s" % item for item in vars(self).items())


def _BuildIdEventsMap(e):
	if e.op == "TabletAccessStat":
		for e1 in e.event.entries:
			if type(e1) is CassLogReader.EventAccessStat.MemtAccStat:
				# We don't plot memtables for now
				pass
			elif type(e1) is CassLogReader.EventAccessStat.SstAccStat:
				sst_gen = e1.id_
				if sst_gen not in _id_events:
					_id_events[sst_gen] = Events()
				_id_events[sst_gen].AddAccStat(e.simulated_time, e1)


def _WriteToFile():
	global _fn_plot_data
	_fn_plot_data = os.path.dirname(__file__) \
			+ "/plot-data/" + Desc.ExpDatetime() + "-tablet-accesses-for-tablet-size-plot-by-time"
	with open(_fn_plot_data, "w") as fo:
		fmt = "%2s %10d %20s %20s" \
				" %7.0f %7.0f %7.0f" \
				" %7.0f %7.0f"
		fo.write("%s\n" % Util.BuildHeader(fmt,
			"id(sst_gen_memt_id_may_be_added_later) y_cord_base_tablet_size_plot time_begin time_end"
			" num_reads_per_day num_needto_read_datafile_per_day num_bf_negatives_per_day"
			" num_true_positives_per_day(not_complete) num_false_positives_per_day(not_complete)"
			))
		for id_, v in sorted(_id_events.iteritems()):
			time_prev = None
			num_reads_prev = 0
			num_needto_read_datafile_prev = 0
			num_negatives_prev = 0
			# These are not complete numbers.
			num_tp_prev = 0
			num_fp_prev = 0
			for time_, cnts in sorted(v.time_cnts.iteritems()):
				num_negatives = cnts.num_reads - cnts.num_needto_read_datafile
				if time_prev == None:
					# We ignore the first time window, i.e., we don't print anything for
					# it. There is a very small time window between the first access and
					# it is logged.
					pass
				else:
					if time_ == time_prev:
						# It may happen.
						raise RuntimeError("Unexpected: time_(%s) == time_prev" % time_)
					time_dur_days = (time_ - time_prev).total_seconds() / (24.0 * 3600)
					num_needto_read_datafile_per_day = (cnts.num_needto_read_datafile - num_needto_read_datafile_prev) / time_dur_days
					global _max_num_needto_read_datafile_per_day
					_max_num_needto_read_datafile_per_day = max(_max_num_needto_read_datafile_per_day, num_needto_read_datafile_per_day)
					fo.write((fmt + "\n") % (id_
						, TabletSizeTimelinePlotDataGenerator.GetBaseYCord(id_)
						, time_prev.strftime("%y%m%d-%H%M%S.%f")
						, time_.strftime("%y%m%d-%H%M%S.%f")
						, (cnts.num_reads - num_reads_prev) / time_dur_days
						, num_needto_read_datafile_per_day
						, (num_negatives - num_negatives_prev) / time_dur_days
						, (cnts.num_tp - num_tp_prev) / time_dur_days
						, (cnts.num_fp - num_fp_prev) / time_dur_days
						))
				time_prev = time_
				num_reads_prev = cnts.num_reads
				num_needto_read_datafile_prev = cnts.num_needto_read_datafile
				num_negatives_prev = num_negatives
				num_tp_prev = cnts.num_tp
				num_fp_prev = cnts.num_fp
			fo.write("\n")
	Cons.P("Created file %s %d" % (_fn_plot_data, os.path.getsize(_fn_plot_data)))
