import operator
import os
import re
import sys

sys.path.insert(0, "../../util/python")
import Cons
import Util

import CollectlLogReader
import Conf
import LoadgenLogReader
import NumCassThreadsReader

_exp_groups = {}

def Load():
	global _exp_groups
	with Cons.MeasureTime("Loading exp sets ..."):
		exp_group_names = []
		for k in Conf.Get("exp_result"):
			exp_group_names.append(k)

		for egn in exp_group_names:
			fn_exp_set = "exp-results/%s" % Conf.Get("exp_result")[egn]
			#Cons.P("%s %s" % (egn, fn_exp_set))
			egst = ExpGroupStorageType(fn_exp_set)
			Cons.P("%s: loaded %d exps" % (egn, len(egst.exps)))
			_exp_groups[egn] = ExpGroupStorageType(fn_exp_set)


def ExpGroups():
	return _exp_groups


class ExpGroupStorageType():
	def __init__(self, fn):
		self.exps = []
		self._Load(fn)

	def _Load(self, fn):
		with open(fn) as fo:
			for line in fo.readlines():
				#Cons.P(line)
				line = line.rstrip()
				if len(line) == 0:
					continue
				if line[0] == "#":
					continue
				self.exps.append(Exp(line))
		#Cons.P(self)

	def __str__(self):
		return " ".join("%s=%s" % item for item in vars(self).items())


class Exp():
	def __init__(self, line):
		self._Parse(line)

	def _Parse(self, line):
		t = line.split()
		if len(t) != 8:
			raise RuntimeError("Unexpected format [%s]" % line)
		self.server_name = t[0]
		self.server_ip = t[1]
		self.log_dt_loadgen = t[2]
		self.log_dt_num_cass_threads = t[3]
		self.log_dt_collectl = t[4]
		self.hot_data_size = t[5]
		self.cold_data_size = t[6]
		self.saturated = int(t[7])
		self.loadgen_log = LoadgenLogReader.Read(self.log_dt_loadgen)
		self.num_cass_threads = NumCassThreadsReader.Read(self.log_dt_num_cass_threads)
		self.collectl = CollectlLogReader.Read(self.log_dt_collectl)

		# TODO: Cassndra log. What do you get from it?
		# - Hot and cold storage size, which you use to calculate cost. This is
		#   worth plotting.
		# - When tablets migrate.
		# - Number of requests to each tablet.

	def __str__(self):
		return " ".join("%s=%s" % item for item in vars(self).items())












# TODO: clean up
#def Throughput(storage_type, key_max_value):
#	rows = _rows_by_storage[storage_type]
#	rows.sort(key=operator.attrgetter(key_max_value))
#	r = rows[-1]
#	return float(r.writes + r.reads) * 1000.0 / r.exe_time
#
#
#def Latency(storage_type, attr_name):
#	rows = _rows_by_storage[storage_type]
#	rows.sort(key=operator.attrgetter(attr_name))
#	o = rows[-1]
#	for a in attr_name.split("."):
#		o = getattr(o, a)
#	return o
#
#
#def MaxLatency(attr_name):
#	max_latency = 0
#
#	for kmv in ["lat_r." + attr_name, "lat_w." + attr_name]:
#		for st, rows in _rows_by_storage.iteritems():
#			rows.sort(key=operator.attrgetter(kmv))
#			o = rows[-1]
#			for a in kmv.split("."):
#				o = getattr(o, a)
#			max_latency = max(max_latency, o)
#
#	return max_latency
#
#
#def AvgAvgLat(storage_type, attr_name):
#	rows = _rows_by_storage[storage_type]
#	sum_lat = 0.0
#	sum_throughput = 0.0
#	max_throughput = 0.0
#	for r in rows:
#		o = r
#		for a in attr_name.split("."):
#			o = getattr(o, a)
#		sum_lat += o
#		thr = float(r.writes + r.reads) * 1000.0 / r.exe_time
#		sum_throughput += thr
#		max_throughput = max(max_throughput, thr)
#	avg_avg_lat = sum_lat / sum_throughput
#	Cons.P("%s %s avg_avg_lat=%f" % (storage_type, attr_name, avg_avg_lat))
#	return [max_throughput, max_throughput * avg_avg_lat]
#
#
#_rows_by_storage = {}
#_fn_plot_data = None
#

# TODO: clean up
#class ExpItem:
#	def __init__(self, raw_lines):
#		#Cons.P(raw_lines)
#		self.raw_lines = raw_lines
#		self.saturated = 0
#		self._ParseLines()
#
#	def _ParseLines(self):
#		i = 0
#		while i < len(self.raw_lines):
#			line = self.raw_lines[i]
#			#Cons.P("line=[%s]" % line)
#			if i == 0:
#				# Local SSD	160223-052200	10,000	"  # # of writes: 266670
#				t = line.split("\t")
#				if len(t) != 4:
#					raise RuntimeError("Unexpected format [%s]" % line)
#				self.storage = t[0]
#				self.exp_datetime = t[1]
#				# Not very relevant. This is from the loadgen client
#				self.num_Ws_per_simulation_time_min = t[2]
#				t1 = t[3].split("# of writes: ")
#				if len(t1) != 2:
#					raise RuntimeError("Unexpected format [%s]" % t[3])
#				self.writes = int(t1[1])
#			elif "# saturated" in line:
#				self.saturated = 2
#			elif "# of reads : " in line:
#				t = line.split("# of reads : ")
#				if len(t) != 2:
#					raise RuntimeError("Unexpected format [%s]" % line)
#				self.reads = int(t[1])
#			elif "# Write latency:" in line:
#				i += 1
#				line = self.raw_lines[i]
#				self.lat_w = _Latency(line)
#			elif "# Read latency:" in line:
#				i += 1
#				line = self.raw_lines[i]
#				self.lat_r = _Latency(line)
#			elif i == len(self.raw_lines) - 1:
#				t = line.split()
#				if (len(t) != 2) or (t[1] != "ms\""):
#					raise RuntimeError("Unexpected format [%s]" % line)
#				self.exe_time = int(t[0])
#			i += 1
#
#	def __str__(self):
#		items = []
#		for i in sorted(vars(self).items()):
#			if i[0] == "raw_lines":
#				continue
#			items.append("%s=%s" % (i[0], i[1]))
#			#Cons.P("%s:%s" % (i[0], i[1]))
#		return "[%s]" % (" ".join(items))
