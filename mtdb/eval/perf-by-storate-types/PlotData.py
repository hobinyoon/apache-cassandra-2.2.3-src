import operator
import os
import re
import sys

sys.path.insert(0, "../../util/python")
import Cons
import Util

import Conf
import ExpData

_rows_by_storage = {}
_fn_plot_data = None


# TODO: I may not need this at all
#def Gen():
#	with Cons.MeasureTime("Generating plot data ..."):
#		exp_group_names = ["local-ssd", "ebs-ssd", "local-ssd-ebs-ssd"]
#		plot_data = {}
#		for egn in exp_group_names:
#			plot_data[egn] = ExpData.GetExpGroup(egn)
#
#		for k, eg in plot_data.iteritems():
#			Cons.P(k)
#			#Cons.P(eg)
#			for e in eg.items:
#				Cons.P(""
#						% (e.
#							))
#
#			self.loadgen_datetime     = tokens[0]
#			self.exe_time_ms          = tokens[1]
#			self.num_writes           = tokens[2]
#			self.num_reads            = tokens[3]
#			self.throughput           = tokens[4]
#			self.lat_w_avg            = tokens[5]
#			self.lat_w__50            = tokens[6]
#			self.lat_w__99            = tokens[7]
#			self.lat_r_avg            = tokens[8]
#			self.lat_r__50            = tokens[9]
#			self.lat_r__99            = tokens[10]
#			self.saturated            = tokens[11]
#			self.num_cass_threads_min = tokens[12]
#			self.num_cass_threads_max = tokens[13]
#			self.cpu_user             = tokens[14]
#			self.cpu_sys              = tokens[15]
#			self.cpu_wait             = tokens[16]
#			self.disk_xvdb_read_kb    = tokens[17]
#			self.disk_xvdb_read_io    = tokens[18]
#			self.disk_xvdb_write_kb   = tokens[19]
#			self.disk_xvdb_write_io   = tokens[20]
#			self.disk_xvdb_rw_size    = tokens[21]
#			self.disk_xvdb_q_len      = tokens[22]
#			self.disk_xvdb_wait       = tokens[23]
#			self.disk_xvdb_svc_time   = tokens[24]
#			self.disk_xvdb_util       = tokens[25]
#			self.net_kb_in            = tokens[26]
#			self.net_kb_out           = tokens[27]






# TODO: clean up
#		_fn_plot_data = "plot-data/throughput-latency-%s" % storage_type
#
#		with open(_fn_plot_data, "w") as fo:
#			fmt = "%13s %7d %8d %7d %8.2f" \
#					" %6.2f %4d %4d %6.2f %4d %4d" \
#					" %1d"
#			fo.write("%s\n" % Util.BuildHeader(fmt, \
#					"storage_type num_writes num_reads exe_time_ms throughput_ops_per_sec" \
#					" lat_w_avg_ms lat_w_50_ms lat_w_99_ms lat_r_avg_ms lat_r_50_ms lat_r_99_ms" \
#					" server_saturated" \
#					))
#			# Order by storage type, writes
#			for s, rows in _rows_by_storage.iteritems():
#				rows.sort(key=operator.attrgetter("writes"))
#				for r in rows:
#					fo.write((fmt + "\n") % (("\"%s\"" % s), r.writes, r.reads, r.exe_time
#						, float(r.writes + r.reads) * 1000.0 / r.exe_time
#						, r.lat_w.avg, r.lat_w._50, r.lat_w._99
#						, r.lat_r.avg, r.lat_r._50, r.lat_r._99
#						, r.saturated
#						))
#				fo.write("\n")
#		Cons.P("Created file %s %d" % (_fn_plot_data, os.path.getsize(_fn_plot_data)))
#
#
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
