import datetime
import math
import os
import sys

sys.path.insert(0, "../util/python")
import Cons
import Util

import CassLogReader
import Desc
import TabletMinMaxTimestampsTimelinePlotDataGenerator

_fn_plot_data = None

_id_events = {}

def Gen():
	with Cons.MeasureTime("Generating tablet accesses plot data for min/max timestamps plot ..."):
		for l in CassLogReader._logs:
			_BuildIdEventsMap(l)
		NumToTime.SetNumAccessesTimeRatio()
		_WriteToFile()


class Events:
	def __init__(self):
		self.time_cnts = {}
		self.min_timestamp = None

	def AddAccStat(self, simulated_time, tablet_acc_stat):
		# tablet_acc_stat is of type EventAccessStat.AccStat
		self.time_cnts[simulated_time] = tablet_acc_stat
		if self.min_timestamp == None:
			self.min_timestamp = tablet_acc_stat.min_timestamp
		elif self.min_timestamp != tablet_acc_stat.min_timestamp:
			raise RuntimeError("Unexpected: self.min_timestamp (%s) != tablet_acc_stat.min_timestamp (%s)"
					% (self.min_timestamp, tablet_acc_stat.min_timestamp))

	def __str__(self):
		return "Events: " + ", ".join("%s: %s" % item for item in vars(self).items())


def _BuildIdEventsMap(e):
	if e.op != "TabletAccessStat":
		return
	for e1 in e.event.entries:
		if type(e1) is CassLogReader.EventAccessStat.MemtAccStat:
			# We don't plot memtables for now.
			pass
		elif type(e1) is CassLogReader.EventAccessStat.SstAccStat:
			sst_gen = e1.id_
			global _id_events
			if sst_gen not in _id_events:
				_id_events[sst_gen] = Events()
			_id_events[sst_gen].AddAccStat(e.simulated_time, e1)


class NumToTime:
	max_num_tpfp_per_day = 0
	min_timestamp_range = None
	# in seconds, in float
	timedur_per_access = None

	# To skip plotting
	datetime_out_of_rage = "090101-000000.000000"


	# Number of accesses is the sum of true and false positives, both of which
	# access the SSTable.
	@staticmethod
	def _SetMaxNumAccesses():
		global _id_events
		for sstgen, events in sorted(_id_events.iteritems()):
			time_prev = None
			num_tp_prev = 0
			num_fp_prev = 0
			for time_, cnts in sorted(events.time_cnts.iteritems()):
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
					num_tp_per_day = (cnts.num_tp - num_tp_prev) / time_dur_days
					num_fp_per_day = (cnts.num_fp - num_fp_prev) / time_dur_days
					num_tpfp_per_day = num_tp_per_day + num_fp_per_day
					NumToTime.max_num_tpfp_per_day = max(NumToTime.max_num_tpfp_per_day, num_tpfp_per_day)
				time_prev = time_
				num_tp_prev = cnts.num_tp
				num_fp_prev = cnts.num_fp
		Cons.P("NumToTime.max_num_tpfp_per_day: %d" % NumToTime.max_num_tpfp_per_day)

	@staticmethod
	def _SetMinTabletTimestampRange():
		for sstgen, v in sorted(TabletMinMaxTimestampsTimelinePlotDataGenerator._id_events.iteritems()):
			if NumToTime.min_timestamp_range == None:
				NumToTime.min_timestamp_range = v.max_timestamp - v.min_timestamp
			else:
				NumToTime.min_timestamp_range = min(NumToTime.min_timestamp_range, v.max_timestamp - v.min_timestamp)
			#Cons.P("%d %s %s %s" % (sstgen
			#	, v.min_timestamp
			#	, v.max_timestamp
			#	, v.max_timestamp - v.min_timestamp
			#	))
		Cons.P("NumToTime.min_timestamp_range: %s" % NumToTime.min_timestamp_range)

	@staticmethod
	def SetNumAccessesTimeRatio():
		NumToTime._SetMaxNumAccesses()
		NumToTime._SetMinTabletTimestampRange()
		NumToTime.timedur_per_access = NumToTime.min_timestamp_range.total_seconds() / NumToTime.max_num_tpfp_per_day

	@staticmethod
	def Conv(base_time, cnt):
		return base_time + datetime.timedelta(seconds = (NumToTime.timedur_per_access * cnt))

	@staticmethod
	def ConvLogscale(base_time, cnt):
		if cnt == 0:
			return NumToTime.datetime_out_of_rage
		else:
			return (base_time + datetime.timedelta(seconds = (NumToTime.min_timestamp_range.total_seconds()
				* math.log(cnt + 1) / math.log(NumToTime.max_num_tpfp_per_day + 1)))).strftime("%y%m%d-%H%M%S.%f")


def _WriteToFile():
	global _fn_plot_data
	_fn_plot_data = os.path.dirname(__file__) \
			+ "/plot-data/" + Desc.ExpDatetime() + "-tablet-accesses-for-min-max-timestamp-plot-by-time"
	with open(_fn_plot_data, "w") as fo:
		fmt = "%2s %20s %20s" \
				" %10d %10d %10d %10d" \
				" %20s"
		fo.write("%s\n" % Util.BuildHeader(fmt,
			"id(sst_gen) simulated_time y_cord_base(min_timestamp)"
			" num_reads_per_day num_true_positives_per_day num_false_positives_per_day num_negatives_per_day"
			" num_true_false_positivies_per_day_converted_to_time"))
		for id_, v in sorted(_id_events.iteritems()):
			time_prev = None
			num_reads_prev = 0
			num_tp_prev = 0
			num_fp_prev = 0
			num_negatives_prev = 0
			for time_, cnts in sorted(v.time_cnts.iteritems()):
				num_negatives = cnts.num_reads - cnts.num_tp - cnts.num_fp
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
					num_tp_per_day = (cnts.num_tp - num_tp_prev) / time_dur_days
					num_fp_per_day = (cnts.num_fp - num_fp_prev) / time_dur_days
					fo.write((fmt + "\n") % (id_
						, time_.strftime("%y%m%d-%H%M%S.%f")
						, v.min_timestamp.strftime("%y%m%d-%H%M%S.%f")
						, (cnts.num_reads - num_reads_prev) / time_dur_days
						, num_tp_per_day
						, num_fp_per_day
						, (num_negatives - num_negatives_prev) / time_dur_days
						, NumToTime.ConvLogscale(v.min_timestamp, num_tp_per_day + num_fp_per_day)
						))
				time_prev = time_
				num_reads_prev = cnts.num_reads
				num_tp_prev = cnts.num_tp
				num_fp_prev = cnts.num_fp
				num_negatives_prev = num_negatives
			fo.write("\n")
	Cons.P("Created file %s %d" % (_fn_plot_data, os.path.getsize(_fn_plot_data)))
