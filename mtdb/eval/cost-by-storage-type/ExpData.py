import os
import sys

sys.path.insert(0, "../../util/python")
import Cons
import Util

import Conf


def Load():
	with Cons.MeasureTime("Loading exp data ..."):
		for expg, v in Conf.Get().iteritems():
			_LoadExpGroup(expg)


_expg_exps = {}


def MaxTotalCost(expg):
	global _expg_exps
	max_total_cost = None
	for e in _expg_exps[expg]:
		if max_total_cost == None:
			max_total_cost = e.TotalCost()
		else:
			max_total_cost = max(max_total_cost, e.TotalCost())
	return max_total_cost


def MutantsTotalCost(expg):
	global _expg_exps
	return _expg_exps[expg][1].TotalCost()


def _LoadExpGroup(expg):
	exps = []
	for k, v in Conf.Get(expg).iteritems():
		for exp, exp_datetime in v.iteritems():
			fn = "%s/work/cassandra/mtdb/process-log/calc-cost-latency-plot-tablet-timeline/plot-data/%s-storage-size-by-time" \
					% (os.path.expanduser("~"), exp_datetime)
			with open(fn) as fo:
				lines = []
				for line in fo.readlines():
					#Cons.P(line)
					line = line.rstrip()
					lines.append(line)
				lines = lines[-5:]
				t = lines[0].split()
				if len(t) != 6:
					raise RuntimeError("Unexpected format [%s]" % lines[0])
				local_ssd_cost = float(t[3])
				ebs_ssd_cost = float(t[4])
				exps.append(ExpCost(exp, local_ssd_cost, ebs_ssd_cost))
	global _expg_exps
	_expg_exps[expg] = exps

	#Cons.P("%s" % expg)
	fn_out = "plot-data/cost.%s" % expg
	with open(fn_out, "w") as fo:
		fmt = "%5s %10.6f %10.6f %10.6f"
		fo.write("%s\n" % Util.BuildHeader(fmt, "exp_name hot_stg_cost cold_stg_cost total_stg_cost"))
		for e in exps:
			fo.write((fmt + "\n") % (e.exp_name, e.hot_stg_cost, e.cold_stg_cost, e.TotalCost()))
	Cons.P("Created file %s %d" % (fn_out, os.path.getsize(fn_out)))


class ExpCost():
	def __init__(self, exp_name, hot_stg_cost, cold_stg_cost):
		# NOTE: careful when you modify the other source. These are the numbers used.
		INST_STORE= 0.527583
		EBS_SSD   = 0.1

		ebs_mag   = 0.05

		# Total date size of the experiment 160307-024348
		data_size_during_exp = 5680490802
		# of i2.2xlarge, which has 2 800 GB SSDs
		inst_store_size = 2 * 800 * 1024 * 1024 * 1024
		size_alpha = float(inst_store_size) / data_size_during_exp

		self.exp_name = exp_name
		if exp_name == "EM":
			if cold_stg_cost != 0:
				raise RuntimeError("Unexpected %s %d %d" % (exp_name, hot_stg_cost, cold_stg_cost))
			self.hot_stg_cost = 0
			self.cold_stg_cost = hot_stg_cost / INST_STORE * ebs_mag
		elif exp_name == "ES":
			if cold_stg_cost != 0:
				raise RuntimeError("Unexpected %s %d %d" % (exp_name, hot_stg_cost, cold_stg_cost))
			self.hot_stg_cost = 0
			self.cold_stg_cost = hot_stg_cost / INST_STORE * EBS_SSD
		elif exp_name == "LS-EM":
			self.hot_stg_cost = hot_stg_cost
			self.cold_stg_cost = cold_stg_cost / EBS_SSD * ebs_mag
		elif exp_name == "LS-ES":
			self.hot_stg_cost = hot_stg_cost
			self.cold_stg_cost = cold_stg_cost
		elif exp_name == "LS":
			if cold_stg_cost != 0:
				raise RuntimeError("Unexpected %s %d %d" % (exp_name, hot_stg_cost, cold_stg_cost))
			self.hot_stg_cost = hot_stg_cost
			self.cold_stg_cost = 0
		else:
			raise RuntimeError("Unexpected %s" % exp_name)

		# Assume the data size that fully fits in the local storage
		self.hot_stg_cost *= size_alpha
		self.cold_stg_cost *= size_alpha

		# In K$
		self.hot_stg_cost /= 1000.0
		self.cold_stg_cost /= 1000.0
	
	def TotalCost(self):
		return self.hot_stg_cost + self.cold_stg_cost

	def __str__(self):
		return " ".join("%s=%s" % item for item in vars(self).items())
