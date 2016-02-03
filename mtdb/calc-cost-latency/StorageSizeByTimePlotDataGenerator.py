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

def Gen():
	with Cons.MeasureTime("Generating storage size plot data ..."):
		global _fn_plot_data
		_fn_plot_data = os.path.dirname(__file__) + "/plot-data/" + Desc.ExpDatetime() + "-storage-size-by-time"
		with open(_fn_plot_data, "w") as fo:
			fmt = "%20s %20s %20s %20s %10d %8f"
			fo.write("%s\n" % Util.BuildHeader(fmt,
					"simulation_time_end simulated_time_begin simulated_time_end simulated_time_mid stg_size_bytes cost_in_the_simulated_time_segment"))
			total_cost = 0.0
			last_cost_print_time = SimTime._simulated_time_begin
			for l in CassLogReader._logs:
				if type(l.event) is Event.AccessStat:
					cost = 0.0
					stg_size = 0
					for e in l.event.entries:
						if type(e) is Event.AccessStat.SstAccStat:
							stg_size += e.size
							# Find the last logging time of the same sstable and calculate cost.
							c = StgCost.InstStore(e.size, l.simulated_time - SstLastCostCalcTime.Get(e.id_))
							cost += c
							SstLastCostCalcTime.Set(e.id_, l.simulated_time)

					if l.simulated_time != last_cost_print_time:
						fo.write((fmt + "\n") %
								(l.simulation_time.strftime("%y%m%d-%H%M%S.%f")
									, last_cost_print_time.strftime("%y%m%d-%H%M%S.%f")
									, l.simulated_time.strftime("%y%m%d-%H%M%S.%f")
									, (last_cost_print_time + datetime.timedelta(seconds = (l.simulated_time - last_cost_print_time).total_seconds() * 0.5)).strftime("%y%m%d-%H%M%S.%f")
									, stg_size
									, cost))
					last_cost_print_time = l.simulated_time

					total_cost += cost
				elif type(l.event) is Event.SstCreated:
					SstLastCostCalcTime.Set(l.event.sst_gen, l.simulated_time)
			msg = "total cost ($): %f" % total_cost
			fo.write("# %s\n" % msg)
			Cons.P(msg)
		Cons.P("Created file %s %d" % (_fn_plot_data, os.path.getsize(_fn_plot_data)))


# Keeps the last cost calc time of SSTables. Memtable cost is already
# included in the EC2 instance cost.
class SstLastCostCalcTime(object):
	id_time = {}

	@staticmethod
	def Set(sst_gen, simulated_time):
		SstLastCostCalcTime.id_time[sst_gen] = simulated_time

	@staticmethod
	def Get(sst_gen):
		r = SstLastCostCalcTime.id_time.get(sst_gen)
		if r == None:
			raise RuntimeError("No last cost calc time for SSTable %d" % sst_gen)
		return r
