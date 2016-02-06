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
	def __init__(self, log_entry):
		self.created = log_entry.simulated_time
		self.temperature_level = log_entry.event.storage_temperature

	def SetSize(self, size):
		self.size = size

	def SetDeleted(self, time):
		self.deleted = time

	def __str__(self):
		return " ".join("%s=%s" % item for item in vars(self).items())


def _BuildData():
	for l in CassLogReader._logs:
		if type(l.event) is Event.SstCreated:
			_sstgen_csd[l.event.sst_gen] = CSD(l)
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
	cur_hot_stg_size = 0
	cur_cold_stg_size = 0
	total_cost_hot = 0.0
	total_cost_cold = 0.0
	last_cost_calc_time = SimTime.SimulatedTimeBegin()
	fmt = "%20s %10d %10d %10f %10f %-14s"

	#	TODO: Calculate instance cost (Everything other than the storage, i.e., CPU, memory, ...)
	# Memtable cost is already included in the EC2 instance cost.

	global _fn_plot_data
	_fn_plot_data = os.path.dirname(__file__) + "/plot-data/" + Desc.ExpDatetime() + "-storage-size-by-time"
	with open(_fn_plot_data, "w") as fo:
		FileOrCons(fo, Util.BuildHeader(fmt, "simulation_time" \
				" cur_hot_stg_size cur_cold_stg_size" \
				" hot_stg_cost_so_far cold_stg_cost_so_far event_desc"))
		FileOrCons(fo, fmt % (SimTime.SimulatedTimeBegin().strftime("%y%m%d-%H%M%S.%f")
			, cur_hot_stg_size, cur_cold_stg_size
			, total_cost_hot, total_cost_cold, "sim_begin"))

		for l in CassLogReader._logs:
			if (type(l.event) is not Event.SstCreated) and (type(l.event) is not Event.SstDeleted):
				continue

			cur_time_dur = l.simulated_time - last_cost_calc_time
			size = _sstgen_csd[l.event.sst_gen].size

			total_cost_hot += StgCost.InstStore(cur_hot_stg_size, cur_time_dur)
			total_cost_cold += StgCost.EbsSsd(cur_cold_stg_size, cur_time_dur)

			temperature_level = _sstgen_csd[l.event.sst_gen].temperature_level

			if type(l.event) is Event.SstCreated:
				if temperature_level == 0:
					cur_hot_stg_size += size
				else:
					cur_cold_stg_size += size
				desc = "%d-created-%s" % (l.event.sst_gen, ("hot" if temperature_level == 0 else "cold"))
			elif type(l.event) is Event.SstDeleted:
				if temperature_level == 0:
					cur_hot_stg_size -= size
				else:
					cur_cold_stg_size -= size
				desc = "%d-deleted" % l.event.sst_gen

			last_cost_calc_time = l.simulated_time
			FileOrCons(fo, fmt % (l.simulated_time.strftime("%y%m%d-%H%M%S.%f")
				, cur_hot_stg_size, cur_cold_stg_size, total_cost_hot, total_cost_cold, desc))

		cur_time_dur = l.simulated_time - last_cost_calc_time
		total_cost_hot += StgCost.InstStore(cur_hot_stg_size, cur_time_dur)
		total_cost_cold += StgCost.EbsSsd(cur_cold_stg_size, cur_time_dur)
		FileOrCons(fo, fmt % (l.simulated_time.strftime("%y%m%d-%H%M%S.%f")
			, cur_hot_stg_size, cur_cold_stg_size, total_cost_hot, total_cost_cold, "sim_end"))

		total_cost_total = total_cost_hot + total_cost_cold
		FileOrCons(fo, "#")
		FileOrCons(fo, "# total_cost_hot   ($): %f %6.3f%%" % (total_cost_hot, 100.0 * total_cost_hot / total_cost_total))
		FileOrCons(fo, "# total_cost_cold  ($): %f %6.3f%%" % (total_cost_cold, 100.0 * total_cost_cold/ total_cost_total))
		FileOrCons(fo, "# total_cost_total ($): %f" % total_cost_total)
	Cons.P("Created file %s %d" % (_fn_plot_data, os.path.getsize(_fn_plot_data)))


def Gen():
	with Cons.MeasureTime("Generating storage size by time plot data ..."):
		_BuildData();
		_Write()
