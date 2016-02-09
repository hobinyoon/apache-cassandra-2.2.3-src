import datetime
import os
import sys

sys.path.insert(0, "../../util/python")
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
	return _id_events[sst_gen].min_ts_simulated_time


class Events:
	def __init__(self):
		self.events = {}
		self.min_ts_simulated_time = None
		self.max_ts_simulated_time = None

	def Add(self, e):
		if type(e.event) not in self.events:
			self.events[type(e.event)] = []
		self.events[type(e.event)].append(e)

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

	def OpenedNormal(self):
		e = self.events.get(Event.SstOpen)
		if e == None:
			return None
		for e1 in e:
			if e1.event.open_reason == "NORMAL":
				return e1
		return None

	def OpenedEarly(self):
		e = self.events.get(Event.SstOpen)
		if e == None:
			return None
		for e1 in e:
			if e1.event.open_reason == "EARLY":
				return e1
		return None

	def TempMonStarted(self):
		e = self.events.get(Event.TempMon)
		if e == None:
			return None
		for e1 in e:
			if type(e1.event.event) is Event.TempMon.Started:
				return e1
		return None

	def TempMonStopped(self):
		if self.TempMonBecomeCold() != None:
			return None
		e = self.events.get(Event.TempMon)
		if e == None:
			return None
		for e1 in e:
			if type(e1.event.event) is Event.TempMon.Stopped:
				return e1
		return None

	def TempMonBecomeCold(self):
		e = self.events.get(Event.TempMon)
		if e == None:
			return None
		for e1 in e:
			if type(e1.event.event) is Event.TempMon.BecomeCold:
				return e1
		return None

	# Min/max timestamp can be None when a tablet is created at the end of the
	# experiment period, but hasn't opened-normal yet.
	def SetTimestamps(self):
		e = self.events.get(Event.SstOpen)
		if e == None:
			return False
		for e1 in e:
			if e1.event.open_reason == "NORMAL":
				self.min_ts_simulated_time = SimTime.SimulatedTime(datetime.datetime.strptime(e1.event.min_ts, "%y%m%d-%H%M%S.%f"))
				self.max_ts_simulated_time = SimTime.SimulatedTime(datetime.datetime.strptime(e1.event.max_ts, "%y%m%d-%H%M%S.%f"))
				return True
		return False

	def TimestampRange(self):
		return self.max_ts_simulated_time - self.min_ts_simulated_time

	def Temperature(self):
		e = self.events.get(Event.SstCreated)
		if e == None:
			raise RuntimeError("Unexpected:")
		if len(e) != 1:
			raise RuntimeError("Unexpected:")
		return e[0].event.storage_temperature

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
		elif type(l.event) is Event.SstOpen:
			_id_events[l.event.sst_gen].Add(l)
		elif type(l.event) is Event.TempMon:
			_id_events[l.event.sst_gen].Add(l)

	# Set min/max timestamps and filter out sstables without those
	for id_ in _id_events.keys():
		if _id_events[id_].SetTimestamps() == False:
			Cons.P("SSTable %d doesn't have min/max timestamp info. Safe to delete." % id_)
			del _id_events[id_]


def _WriteToFile():
	global _fn_plot_data
	_fn_plot_data = os.path.dirname(__file__) + "/plot-data/" + Desc.ExpDatetime() + "-tablet-min-max-timestamps-timeline"
	with open(_fn_plot_data, "w") as fo:
		fmt = "%2d %1d %20s %20s %20s %20s %20s %20s %20s %10.0f %10.0f %20s %20s %20s %20s %20s"
		fo.write("%s\n" % Util.BuildHeader(fmt, "id temperature_level creation_time deletion_time"
			" deletion_time_for_plot box_plot_right_bound"
			" timestamp_min timestamp_max timestamp_mid timestamp_dur_in_sec"
			" tablet_lifespan_in_sec"
			" opened_early opened_normal"
			" temp_mon_started temp_mon_stopped temp_mon_becomd_cold"
			))
		for id_, v in sorted(_id_events.iteritems()):
			if v.Created().simulated_time > SimTime.SimulatedTimeEnd():
				continue

			# If not defined, "-"
			deleted_time0 = (v.Deleted().simulated_time.strftime("%y%m%d-%H%M%S.%f") if v.Deleted() != None else "-")
			# If not defined, SimTime.SimulatedTimeEnd()
			deleted_time1_ = v.Deleted().simulated_time if v.Deleted() != None else SimTime.SimulatedTimeEnd()
			deleted_time1 = deleted_time1_.strftime("%y%m%d-%H%M%S.%f")
			deleted_time2 = SimTime.StrftimeWithOutofrange(v.Deleted())

			fo.write((fmt + "\n") % (id_
				, v.Temperature()
				, v.Created().simulated_time.strftime("%y%m%d-%H%M%S.%f")
				, deleted_time0
				, deleted_time2
				, deleted_time1
				, v.min_ts_simulated_time.strftime("%y%m%d-%H%M%S.%f")
				, v.max_ts_simulated_time.strftime("%y%m%d-%H%M%S.%f")
				, (v.min_ts_simulated_time + datetime.timedelta(seconds = (v.max_ts_simulated_time - v.min_ts_simulated_time).total_seconds()/2.0)).strftime("%y%m%d-%H%M%S.%f")
				, (v.max_ts_simulated_time - v.min_ts_simulated_time).total_seconds()
				, (deleted_time1_ - v.Created().simulated_time).total_seconds()
				, SimTime.StrftimeWithOutofrange(v.OpenedEarly())
				, SimTime.StrftimeWithOutofrange(v.OpenedNormal())
				, SimTime.StrftimeWithOutofrange(v.TempMonStarted())
				, SimTime.StrftimeWithOutofrange(v.TempMonStopped())
				, SimTime.StrftimeWithOutofrange(v.TempMonBecomeCold())
				))
	Cons.P("Created file %s %d" % (_fn_plot_data, os.path.getsize(_fn_plot_data)))
