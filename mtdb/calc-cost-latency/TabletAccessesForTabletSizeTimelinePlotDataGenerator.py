import os
import sys

sys.path.insert(0, "../util/python")
import Cons
import Util

import CassLogReader
import Desc
import SimTime

_fn_plot_data_tablet_timeline_created_deleted = None
_fn_plot_data_tablet_access_counts_by_time = None

_id_events = {}

def Gen():
	with Cons.MeasureTime("Generating tablet accesses timeline plot data ..."):
		for l in CassLogReader._logs:
			_BuildIdEventsMap(l)
		_CalcTabletsYCords()
		_WriteToFile()


class Events:
	def __init__(self):
		self.created = None
		self.deleted = None
		self.max_size = -1
		self.y_cord = -1
		self.time_cnts = {}

	def AddCreatedDeleted(self, e):
		if e.op == "SstCreated":
			self.created = e
		elif e.op == "SstDeleted":
			self.deleted = e

	def AddAccStat(self, simulated_time, tablet_acc_stat):
		# tablet_acc_stat is of type EventAccessStat.AccStat
		self.time_cnts[simulated_time] = tablet_acc_stat
		self.max_size = max(self.max_size, tablet_acc_stat.size)

	def __str__(self):
		return "Events: " + ", ".join("%s: %s" % item for item in vars(self).items())


def _BuildIdEventsMap(e):
	if e.op == "SstCreated" or e.op == "SstDeleted":
		if e.event.sst_gen not in _id_events:
			_id_events[e.event.sst_gen] = Events()
		_id_events[e.event.sst_gen].AddCreatedDeleted(e)
	elif e.op == "TabletAccessStat":
		for e1 in e.event.entries:
			if type(e1) is CassLogReader.EventAccessStat.MemtAccStat:
				# We don't plot memtables for now
				pass
			elif type(e1) is CassLogReader.EventAccessStat.SstAccStat:
				sst_gen = e1.id_
				if sst_gen not in _id_events:
					raise RuntimeError("Unexpected: sst_gen %d not in _id_events" % sst_gen)
				_id_events[sst_gen].AddAccStat(e.simulated_time, e1)


def _CalcTabletsYCords():
	# Space filling by sweeping through the x-axis. There will be only a
	# handful of blocks (sstables) going through the sweeping line.

	class Area:
		def __init__(self, x1, y0, y1):
			# x0, lower bound of x, is not used
			#self.x0 = x0.simulated_time
			# x1 can be None, if the tablet is still in use (not deleted yet)
			self.x1 = (SimTime._simulated_time_end if x1 == None else x1.simulated_time)
			self.y0 = y0
			self.y1 = y1

		def Overlaps(self, other):
			# We only check if the y-ranges overlap. X-ranges don't overlap.
			o_y0 = other.y0 - y_spacing
			o_y1 = other.y1 + y_spacing

			# If self.y0 straddles other's y-range, then overlap.
			if (self.y0 <= o_y0) != (self.y0 <= o_y1):
				return True
			# If self.y1 straddles other's y-range, then overlap.
			if (self.y1 <= o_y0) != (self.y1 <= o_y1):
				return True
			# The same goes with other
			if (o_y0 <= self.y0) != (o_y0 <= self.y1):
				return True
			if (o_y1 <= self.y0) != (o_y1 <= self.y1):
				return True
			return False

		def Moveup(self, y):
			height = self.y1 - self.y0
			self.y0 = y
			self.y1 = y + height

		def __lt__(self, other):
			# Since they don't overlap, we simply compare y0.
			return self.y0 < other.y0

	# Areas intersecting the current sweep line
	areas = []

	# Y spacing between blocks. 4 MB.
	y_spacing = 4 * 1024 * 1024

	for id, v in sorted(_id_events.iteritems()):
		# Delete areas that are past the sweeping line
		new_areas = []
		for a in areas:
			if v.created.simulated_time <= a.x1:
				new_areas.append(a)
		areas = new_areas

		# Sort areas by their y-coordinates
		areas.sort()

		# Fit the current area (block) while avoiding overlapping with existing areas.
		#a0 = Area(v.created, v.deleted, 0, v.size)
		a0 = Area(v.deleted, 0, v.max_size)
		for a in areas:
			if a.Overlaps(a0):
				a0.Moveup(a.y1 + y_spacing)
		areas.append(a0)
		v.y_cord = a0.y0


def _WriteToFile():
	global _fn_plot_data_tablet_timeline_created_deleted
	_fn_plot_data_tablet_timeline_created_deleted = os.path.dirname(__file__) + "/plot-data/" + Desc.ExpDatetime() + "-tablet-timeline"
	with open(_fn_plot_data_tablet_timeline_created_deleted, "w") as fo:
		fmt = "%2s %20s %20s %20s %20s %10d %10d"
		fo.write("%s\n" % Util.BuildHeader(fmt, "id creation_time deletion_time deletion_time_for_plot "
			"box_plot_right_bound max_size y_cord_base"))
		# Note: id can be m(number) or (number) for memtables and sstables
		for id_, v in sorted(_id_events.iteritems()):
			fo.write((fmt + "\n") % (id_
				, v.created.simulated_time.strftime("%y%m%d-%H%M%S.%f")
				, (v.deleted.simulated_time.strftime("%y%m%d-%H%M%S.%f") if v.deleted != None else "-")
				, (v.deleted.simulated_time.strftime("%y%m%d-%H%M%S.%f") if v.deleted != None else "090101-000000.000000")
				, (v.deleted.simulated_time.strftime("%y%m%d-%H%M%S.%f") if v.deleted != None else SimTime._simulated_time_end.strftime("%y%m%d-%H%M%S.%f"))
				, v.max_size
				, v.y_cord
				))
	Cons.P("Created file %s %d" % (_fn_plot_data_tablet_timeline_created_deleted, os.path.getsize(_fn_plot_data_tablet_timeline_created_deleted)))

	global _fn_plot_data_tablet_access_counts_by_time
	_fn_plot_data_tablet_access_counts_by_time = os.path.dirname(__file__) \
			+ "/plot-data/" + Desc.ExpDatetime() + "-tablet-access-counts-by-time"
	with open(_fn_plot_data_tablet_access_counts_by_time, "w") as fo:
		fmt = "%2s %10d %20s %20s %7.0f %7.0f %7.0f %7.0f"
		fo.write("%s\n" % Util.BuildHeader(fmt,
			"id(sst_gen_memt_id_may_be_added_later) y_cord_base_tablet_size_plot time_begin time_end"
			" num_reads_per_day num_true_positives_per_day num_false_positives_per_day"
			" num_negatives_per_day"))
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
					fo.write((fmt + "\n") % (id_
						, v.y_cord
						, time_prev.strftime("%y%m%d-%H%M%S.%f")
						, time_.strftime("%y%m%d-%H%M%S.%f")
						, (cnts.num_reads - num_reads_prev) / time_dur_days
						, (cnts.num_tp - num_tp_prev) / time_dur_days
						, (cnts.num_fp - num_fp_prev) / time_dur_days
						, (num_negatives - num_negatives_prev) / time_dur_days
						))
				time_prev = time_
				num_reads_prev = cnts.num_reads
				num_tp_prev = cnts.num_tp
				num_fp_prev = cnts.num_fp
				num_negatives_prev = num_negatives
			fo.write("\n")
	Cons.P("Created file %s %d" % (_fn_plot_data_tablet_access_counts_by_time, os.path.getsize(_fn_plot_data_tablet_access_counts_by_time)))
