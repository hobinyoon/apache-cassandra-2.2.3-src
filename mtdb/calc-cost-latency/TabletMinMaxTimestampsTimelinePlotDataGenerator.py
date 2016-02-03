import datetime
import os
import sys

sys.path.insert(0, "../util/python")
import Cons
import Util

import CassLogReader
import Desc
import Event
import SimTime

_fn_plot_data = None

_id_events = {}


def Gen():
	with Cons.MeasureTime("Generating tablet min/max timestamp timeline plot data ..."):
		_BuildIdEventsMap()
		_WriteToFile()


def GetTabletMinTimestamp(sst_gen):
	if sst_gen not in _id_events:
		raise RuntimeError("Unexpected: sst_gen %d not in _id_events" % sst_gen)
	return _id_events[sst_gen].min_timestamp


class Events:
	def __init__(self):
		self.events = {}
		self.min_timestamp = None
		self.max_timestamp = None

	def Add(self, e):
		if type(e.event) not in self.events:
			self.events[type(e.event)] = []
		self.events[type(e.event)].append(e)

	def SetTimpstamps(self, tablet_acc_stat):
		# tablet_acc_stat is of type AccessStat.AccStat
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

	def Created(self):
		e = self.events.get(Event.SstCreated)
		if e == None:
			return None
		if len(e) != 1:
			raise RuntimeError("Unexpected:")
		return e[0]

	def Deleted(self):
		e = self.events.get(Event.SstDeleted)
		if e == None:
			return None
		if len(e) != 1:
			raise RuntimeError("Unexpected:")
		return e[0]

	def __str__(self):
		return "Events: " + ", ".join("%s: %s" % item for item in vars(self).items())


def _BuildIdEventsMap():
	for l in CassLogReader._logs:
		if type(l.event) is Event.SstCreated:
			if l.event.sst_gen not in _id_events:
				_id_events[l.event.sst_gen] = Events()
			_id_events[l.event.sst_gen].Add(l)
		elif type(l.event) is Event.SstDeleted:
			_id_events[l.event.sst_gen].Add(l)
		elif type(l.event) is Event.AccessStat:
			for e1 in l.event.entries:
				if type(e1) is Event.AccessStat.MemtAccStat:
					# Memtables don't have min/max timestamps
					pass
				elif type(e1) is Event.AccessStat.SstAccStat:
					sst_gen = e1.id_
					if sst_gen not in _id_events:
						raise RuntimeError("Unexpected: sst_gen %d not in _id_events" % sst_gen)
					_id_events[sst_gen].SetTimpstamps(e1)

	# Filter out sstables without min/max timestamps. It can happen when the
	# tablets are created at the end of the experiment period without any
	# accesses to them followed.
	for id_ in _id_events.keys():
		if _id_events[id_].min_timestamp == None:
			Cons.P("SSTable %d doesn't have min/max timestamp info. Safe to delete." % id_)
			del _id_events[id_]


def _WriteToFile():
	global _fn_plot_data
	_fn_plot_data = os.path.dirname(__file__) + "/plot-data/" + Desc.ExpDatetime() + "-tablet-min-max-timestamps-timeline"
	with open(_fn_plot_data, "w") as fo:
		fmt = "%2s %20s %20s %20s %20s %20s %20s %20s %10.0f %10.0f"
		fo.write("%s\n" % Util.BuildHeader(fmt, "id creation_time deletion_time"
			" deletion_time_for_plot box_plot_right_bound"
			" timestamp_min timestamp_max timestamp_mid timestamp_dur_in_sec"
			" tablet_lifespan_in_sec"
			))
		for id_, v in sorted(_id_events.iteritems()):
			# If not defined, "-"
			deleted_time0 = (v.Deleted().simulated_time.strftime("%y%m%d-%H%M%S.%f") if v.Deleted() != None else "-")
			# If not defined, SimTime._simulated_time_end
			deleted_time1_ = v.Deleted().simulated_time if v.Deleted() != None else SimTime._simulated_time_end
			deleted_time1 = deleted_time1_.strftime("%y%m%d-%H%M%S.%f")
			deleted_time2 = SimTime.StrftimeWithOutofrange(v.Deleted())

			fo.write((fmt + "\n") % (id_
				, v.Created().simulated_time.strftime("%y%m%d-%H%M%S.%f")
				, deleted_time0
				, deleted_time2
				, deleted_time1
				, v.min_timestamp.strftime("%y%m%d-%H%M%S.%f")
				, v.max_timestamp.strftime("%y%m%d-%H%M%S.%f")
				, (v.min_timestamp + datetime.timedelta(seconds = (v.max_timestamp - v.min_timestamp).total_seconds()/2.0)).strftime("%y%m%d-%H%M%S.%f")
				, (v.max_timestamp - v.min_timestamp).total_seconds()
				, (deleted_time1_ - v.Created().simulated_time).total_seconds()
				))
	Cons.P("Created file %s %d" % (_fn_plot_data, os.path.getsize(_fn_plot_data)))
