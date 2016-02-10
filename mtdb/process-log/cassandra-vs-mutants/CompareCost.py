import os
import sys

sys.path.insert(0, "../../util/python")
import Cons
import Util

import Conf

def Compare():
	_LoadLogs()
	_WritePlotData()


_cass = None
_mutants = None
_fn_plot_data = None


class CassLog(object):
	def __init__(self, c_or_m):
		self.exp_datetime = Conf.Get(c_or_m + "_experiment_datetime")
		# Use the already processed result
		self.fn_log = "../calc-cost-latency-plot-tablet-timeline/plot-data/%s-storage-size-by-time" % self.exp_datetime
		self._LoadFile()

	def _LoadFile(self):
		# total_cost_hot   ($): 4.792377 100.000%
		# total_cost_cold  ($): 0.000000  0.000%
		# total_cost_total ($): 4.792377
		with Cons.MeasureTime("Loading file %s ..." % self.fn_log):
			with open(self.fn_log) as fo:
				for line in fo.readlines():
					if "# total_cost_hot" in line:
						t = line.split()
						self.cost_hot = float(t[3])
					elif "# total_cost_cold" in line:
						t = line.split()
						self.cost_cold = float(t[3])
					elif "# total_cost_total" in line:
						t = line.split()
						self.cost_total = float(t[3])


def _LoadLogs():
	global _cass, _mutants
	_cass = CassLog("cassandra")
	_mutants = CassLog("mutants")


def _WritePlotData():
	global _cass, _mutants, _fn_plot_data
	_fn_plot_data = "plot-data/cost-comparison-%s-%s" % (_cass.exp_datetime, _mutants.exp_datetime)
	with Cons.MeasureTime("Writing file %s ..." % _fn_plot_data):
		with open(_fn_plot_data, "w") as fo:
			fmt = "%24s %10f %10f %10f"
			fo.write("%s\n" % Util.BuildHeader(fmt,
					"cass_or_mutants_exp_datetime cost_hot cost_cold cost_total"))
			fo.write((fmt + "\n") %
					("Cassandra\\n%s" % _cass.exp_datetime
						, _cass.cost_hot
						, _cass.cost_cold
						, _cass.cost_total))
			fo.write((fmt + "\n") %
					("Mutants\\n%s" % _mutants.exp_datetime
						, _mutants.cost_hot
						, _mutants.cost_cold
						, _mutants.cost_total))
		Cons.P("Created %s %d" % (_fn_plot_data, os.path.getsize(_fn_plot_data)))
