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
	with Cons.MeasureTime("Generating tablet accesses timeline plot data ..."):
		_BuildIdEventsMap()
		_CalcTabletsYCords()
		_WriteToFile()


def GetBaseYCord(sst_gen):
	if sst_gen not in _id_events:
		raise RuntimeError("Unexpected: sst_gen %d not in _id_events" % sst_gen)
	return _id_events[sst_gen].y_cord


def MinTabletSize():
	s = None
	for k, v in _id_events.iteritems():
		if s == None:
			s = v.TabletSize()
		else:
			s = min(s, v.TabletSize())
	return s


class Events:
	def __init__(self):
		self.events = {}
		self.y_cord = -1

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

	# Tablet size can be None when a tablet is created at the end of the
	# experiment period, but hasn't opened-normal yet.
	def TabletSize(self):
		e = self.events.get(Event.SstOpen)
		if e == None:
			return None
		for e1 in e:
			if e1.event.open_reason == "NORMAL":
				return e1.event.bytesOnDisk
		return None

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

	# Filter out sstables without tablet size
	for id_ in _id_events.keys():
		if _id_events[id_].TabletSize() == None:
			Cons.P("SSTable %d doesn't have tablet size info. Safe to delete." % id_)
			del _id_events[id_]


def _CalcTabletsYCords():
	# Y spacing between blocks
	y_spacing = 0
	_CalcTabletsYCords0(y_spacing)

	max_y_cord = 0
	for id, v in _id_events.iteritems():
		max_y_cord = max(max_y_cord, v.y_cord + v.TabletSize())
	Cons.P("max_y_cord: %d" % max_y_cord)
	y_spacing = max_y_cord * 0.01
	_CalcTabletsYCords0(y_spacing)


def _CalcTabletsYCords0(y_spacing):
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

	for id, v in sorted(_id_events.iteritems()):
		# Delete areas that are past the sweeping line
		new_areas = []
		for a in areas:
			if v.Created().simulated_time <= a.x1:
				new_areas.append(a)
		areas = new_areas

		# Sort areas by their y-coordinates
		areas.sort()

		# Fit the current area (block) while avoiding overlapping with existing areas.
		#a0 = Area(v.Created(), v.Deleted(), 0, v.size)
		a0 = Area(v.Deleted(), 0, v.TabletSize())
		for a in areas:
			if a.Overlaps(a0):
				a0.Moveup(a.y1 + y_spacing)
		areas.append(a0)
		v.y_cord = a0.y0


def _WriteToFile():
	global _fn_plot_data
	_fn_plot_data = os.path.dirname(__file__) + "/plot-data/" + Desc.ExpDatetime() + "-tablet-sizes-timeline"
	with open(_fn_plot_data, "w") as fo:
		fmt = "%2d %1d %20s %20s %20s %20s %10d %10d %20s %20s %20s %20s %20s"
		fo.write("%s\n" % Util.BuildHeader(fmt,
			"id temperature_level creation_time deletion_time deletion_time_for_plot"
			" box_plot_right_bound tablet_size y_cord_base"
			" opened_early opened_normal"
			" temp_mon_started temp_mon_stopped temp_mon_becomd_cold"
			))
		# Note: id can be m(number) or (number) for memtables and sstables
		for id_, v in sorted(_id_events.iteritems()):
			fo.write((fmt + "\n") % (id_
				, v.Temperature()
				, v.Created().simulated_time.strftime("%y%m%d-%H%M%S.%f")
				, (v.Deleted().simulated_time.strftime("%y%m%d-%H%M%S.%f") if v.Deleted() != None else "-")
				, SimTime.StrftimeWithOutofrange(v.Deleted())
				, (v.Deleted().simulated_time.strftime("%y%m%d-%H%M%S.%f") if v.Deleted() != None else SimTime._simulated_time_end.strftime("%y%m%d-%H%M%S.%f"))
				, v.TabletSize()
				, v.y_cord
				, SimTime.StrftimeWithOutofrange(v.OpenedEarly())
				, SimTime.StrftimeWithOutofrange(v.OpenedNormal())
				, SimTime.StrftimeWithOutofrange(v.TempMonStarted())
				, SimTime.StrftimeWithOutofrange(v.TempMonStopped())
				, SimTime.StrftimeWithOutofrange(v.TempMonBecomeCold())
				))
	Cons.P("Created file %s %d" % (_fn_plot_data, os.path.getsize(_fn_plot_data)))
