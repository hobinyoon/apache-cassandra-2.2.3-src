import datetime
import os
import sys

sys.path.insert(0, "../util/python")
import Cons
import Util

import CassLogReader
import LoadgenLogReader
import SimTime

_fn_plot_data = None

_id_events = {}


def Gen():
	with Cons.MeasureTime("Generating tablet min/max timestamp timeline plot data ..."):
		for l in CassLogReader._logs:
			_BuildIdEventsMap(l)
		_WriteToFile()


class Events:
	def __init__(self):
		self.created = None
		self.deleted = None
		self.min_timestamp = None
		self.max_timestamp = None

	def AddCreatedDeleted(self, e):
		if e.op == "SstCreated":
			self.created = e
		elif e.op == "SstDeleted":
			self.deleted = e

	def SetTimpstamps(self, tablet_acc_stat):
		# tablet_acc_stat is of type EventAccessStat.AccStat
		if self.min_timestamp == None:
			self.min_timestamp = tablet_acc_stat.min_timestamp
		else:
			if self.min_timestamp != tablet_acc_stat.min_timestamp:
				raise RuntimeError("Unexpected: self.min_timestamp (%d) != tablet_acc_stat.min_timestamp (%d)"
						% (self.min_timestamp, tablet_acc_stat.min_timestamp))
		if self.max_timestamp == None:
			self.max_timestamp = tablet_acc_stat.max_timestamp
		else:
			if self.max_timestamp != tablet_acc_stat.max_timestamp:
				raise RuntimeError("Unexpected: self.max_timestamp (%d) != tablet_acc_stat.max_timestamp (%d)"
						% (self.max_timestamp, tablet_acc_stat.max_timestamp))

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
				# Memtables don't have min/max timestamps
				pass
			elif type(e1) is CassLogReader.EventAccessStat.SstAccStat:
				sst_gen = e1.id_
				if sst_gen not in _id_events:
					raise RuntimeError("Unexpected: sst_gen %d not in _id_events" % sst_gen)
				_id_events[sst_gen].SetTimpstamps(e1)


def _WriteToFile():
	global _fn_plot_data
	_fn_plot_data = os.path.dirname(__file__) + "/plot-data/" + LoadgenLogReader.LogFilename() + "-tablet-min-max-timestamps-timeline"
	with open(_fn_plot_data, "w") as fo:
		fmt = "%2s %20s %20s %20s %20s %20s %20s %20s"
		fo.write("%s\n" % Util.BuildHeader(fmt, "id creation_time deletion_time deletion_time_for_plot "
			"box_plot_right_bound timestamp_min timestamp_max timestamp_mid"))
		for id_, v in sorted(_id_events.iteritems()):
			fo.write((fmt + "\n") % (id_
				, v.created.simulated_time.strftime("%y%m%d-%H%M%S.%f")
				, (v.deleted.simulated_time.strftime("%y%m%d-%H%M%S.%f") if v.deleted != None else "-")
				, (v.deleted.simulated_time.strftime("%y%m%d-%H%M%S.%f") if v.deleted != None else "090101-000000.000000")
				, (v.deleted.simulated_time.strftime("%y%m%d-%H%M%S.%f") if v.deleted != None else SimTime._simulated_time_end.strftime("%y%m%d-%H%M%S.%f"))
				, SimTime.SimulatedTime(v.min_timestamp).strftime("%y%m%d-%H%M%S.%f")
				, SimTime.SimulatedTime(v.max_timestamp).strftime("%y%m%d-%H%M%S.%f")
				, SimTime.SimulatedTime(v.min_timestamp + datetime.timedelta(seconds = (v.max_timestamp - v.min_timestamp).total_seconds()/2.0)).strftime("%y%m%d-%H%M%S.%f")
				))
	Cons.P("Created file %s %d" % (_fn_plot_data, os.path.getsize(_fn_plot_data)))
