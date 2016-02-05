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
import StgCost

_fn_plot_data = None
_sstgen_csd = {}


# SSTable Created, Size, and Deleted info. It is constructed from these log entries:
#   Sst start: Event.SstCreated
#   Sst size : Will know at Event.SstOpen-NORMAL.
#   Sst end  : Event.SstDeleted. If not exist, simulation end time
class CSD(object):
	# Constructor sets the creation time
	def __init__(self, time):
		self.created = time

	def SetSize(self, size):
		self.size = size

	def SetDeleted(self, time):
		self.deleted = time

	def __str__(self):
		return "created=%s size=%d deleted=%s" \
				% (self.created, self.size , self.deleted if hasattr(self, "deleted") else "(NA)")


def _BuildData():
	for l in CassLogReader._logs:
		if type(l.event) is Event.SstCreated:
			_sstgen_csd[l.event.sst_gen] = CSD(l.simulated_time)
		elif type(l.event) is Event.SstOpen:
			if l.event.open_reason == "NORMAL":
				_sstgen_csd[l.event.sst_gen].SetSize(l.event.bytesOnDisk)
		elif type(l.event) is Event.SstDeleted:
			_sstgen_csd[l.event.sst_gen].SetDeleted(l.simulated_time)

	#for k, v in sorted(_sstgen_csd.iteritems()):
	#	Cons.P("%d %s" % (k, v))


def FileOrCons(fo, msg):
	if fo is not None:
		fo.write(msg + "\n")
	else:
		Cons.P(msg)


def _Write():
	cur_size = 0
	last_cost_calc_time = SimTime.SimulatedTimeBegin()
	total_cost = 0.0
	fmt = "%20s %10d %10f %12s"

	#	TODO: Calculate instance cost (Everything other than the storage, i.e., CPU, memory, ...)
	# Memtable cost is already included in the EC2 instance cost.

	global _fn_plot_data
	_fn_plot_data = os.path.dirname(__file__) + "/plot-data/" + Desc.ExpDatetime() + "-storage-size-by-time"
	with open(_fn_plot_data, "w") as fo:
		FileOrCons(fo, Util.BuildHeader(fmt, "simulation_time cur_size stg_cost_so_far event_desc"))
		FileOrCons(fo, fmt % (SimTime.SimulatedTimeBegin().strftime("%y%m%d-%H%M%S.%f"), cur_size, total_cost, "sim_begin"))

		for l in CassLogReader._logs:
			if type(l.event) is Event.SstCreated:
				subcost = StgCost.InstStore(cur_size, l.simulated_time - last_cost_calc_time)
				last_cost_calc_time = l.simulated_time
				total_cost += subcost

				cur_size += _sstgen_csd[l.event.sst_gen].size
				desc = "%d-created" % l.event.sst_gen
				FileOrCons(fo, fmt % (l.simulated_time.strftime("%y%m%d-%H%M%S.%f"), cur_size, total_cost, desc))
				#	TODO: Calculate EBS storage cost too based on the location of the SSTable

			elif type(l.event) is Event.SstDeleted:
				subcost = StgCost.InstStore(cur_size, l.simulated_time - last_cost_calc_time)
				last_cost_calc_time = l.simulated_time
				total_cost += subcost

				cur_size -= _sstgen_csd[l.event.sst_gen].size
				desc = "%d-deleted" % l.event.sst_gen
				FileOrCons(fo, fmt % (l.simulated_time.strftime("%y%m%d-%H%M%S.%f"), cur_size, total_cost, desc))

		subcost = StgCost.InstStore(cur_size, SimTime.SimulatedTimeEnd() - last_cost_calc_time)
		last_cost_calc_time = SimTime.SimulatedTimeEnd()
		total_cost += subcost
		FileOrCons(fo, fmt % (SimTime.SimulatedTimeEnd().strftime("%y%m%d-%H%M%S.%f"), cur_size, total_cost, "sim_end"))

		FileOrCons(fo, "#")
		FileOrCons(fo, "# total_cost($): %f" % total_cost)
	Cons.P("Created file %s %d" % (_fn_plot_data, os.path.getsize(_fn_plot_data)))


def Gen():
	with Cons.MeasureTime("Generating storage size by time plot data ..."):
		_BuildData();
		_Write()
