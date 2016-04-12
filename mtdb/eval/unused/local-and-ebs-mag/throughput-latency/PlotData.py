import operator
import os
import re
import sys

sys.path.insert(0, "../../../util/python")
import Cons
import Util

import Conf

def Gen():
	_LoadData()
	_SetSaturatedBorder()
	_GenPlotData()


def Throughput(storage_type, key_max_value):
	rows = _exps_by_storage[storage_type]
	rows.sort(key=operator.attrgetter(key_max_value))
	r = rows[-1]
	return float(r.writes + r.reads) * 1000.0 / r.exe_time


def Latency(storage_type, attr_name):
	rows = _exps_by_storage[storage_type]
	rows.sort(key=operator.attrgetter(attr_name))
	o = rows[-1]
	for a in attr_name.split("."):
		o = getattr(o, a)
	return o


def MaxLatency(attr_name):
	max_latency = 0

	for kmv in ["lat_r." + attr_name, "lat_w." + attr_name]:
		for st, rows in _exps_by_storage.iteritems():
			rows.sort(key=operator.attrgetter(kmv))
			o = rows[-1]
			for a in kmv.split("."):
				o = getattr(o, a)
			max_latency = max(max_latency, o)

	return max_latency


_exps_by_storage = {}
_fn_plot_data = None


class _Latency:
	def __init__(self, line):
		self._Parse(line)

	def _Parse(self, line):
		# avg= 0.995 min=0.536 max= 666 50=   0 90=   0 95=   1 99=   3 995=   6 999=  31
			mo = re.search(r"avg= *", line)
			if mo == None:
				raise RuntimeError("Unexpected format [%s]" % line)
			line = line[mo.end():]
			self.avg = float(line.split()[0])

			mo = re.search(r"min= *", line)
			if mo == None:
				raise RuntimeError("Unexpected format [%s]" % line)
			line = line[mo.end():]
			self.min = float(line.split()[0])

			mo = re.search(r"max= *", line)
			if mo == None:
				raise RuntimeError("Unexpected format [%s]" % line)
			line = line[mo.end():]
			self.max = float(line.split()[0])

			mo = re.search(r"50= *", line)
			if mo == None:
				raise RuntimeError("Unexpected format [%s]" % line)
			line = line[mo.end():]
			self._50 = int(line.split()[0])

			mo = re.search(r"90= *", line)
			if mo == None:
				raise RuntimeError("Unexpected format [%s]" % line)
			line = line[mo.end():]
			self._90 = int(line.split()[0])

			mo = re.search(r"95= *", line)
			if mo == None:
				raise RuntimeError("Unexpected format [%s]" % line)
			line = line[mo.end():]
			self._95 = int(line.split()[0])

			mo = re.search(r"99= *", line)
			if mo == None:
				raise RuntimeError("Unexpected format [%s]" % line)
			line = line[mo.end():]
			self._99 = int(line.split()[0])

			mo = re.search(r"995= *", line)
			if mo == None:
				raise RuntimeError("Unexpected format [%s]" % line)
			line = line[mo.end():]
			self._995 = int(line.split()[0])

			mo = re.search(r"999= *", line)
			if mo == None:
				raise RuntimeError("Unexpected format [%s]" % line)
			line = line[mo.end():]
			self._999 = int(line.split()[0])

	def __str__(self):
		return "[%s]" % (" ".join("%s=%s" % item for item in vars(self).items()))


class ExpItem:
	def __init__(self, raw_line):
		#Cons.P(raw_line)
		self.raw_line = raw_line
		self._ParseLine()
		self._ReadLogfile()
		#Cons.P(self)

	def _ParseLine(self):
		# EBS-Mag      160223-053528   10000         -
		t = self.raw_line.split()
		if len(t) != 4:
			raise RuntimeError("Unexpected format [%s]" % self.raw_line)
		self.storage = t[0]
		self.exp_datetime = t[1]
		self.num_Ws_per_simulation_time_min = t[2]
		self.saturated = 2 if t[3] == "saturated" else 0

	def _ReadLogfile(self):
		fn_log = "../../../logs/loadgen/%s" % self.exp_datetime
		with open(fn_log) as fo:
			# Get the last 12 lines
			lines = []
			for line in fo.readlines():
				lines.append(line)
			lines = lines[-12:]

			# # simulation_time_dur_ms     simulated_time         OpW_per_sec   running_behind_cnt    read_latency_ms  read_cnt
			# #         simulation_time         num_OpW_requested                  running_behind_avg_in_ms      write_cnt
			# #                                       percent_completed                         write_latency_ms
			# #                                                 running_on_time_cnt
			# #                                              running_on_time_sleep_avg_in_ms
			# #     1                 2                 3       4     5     6     7        8     9       10   11   12   13   14
			# 1646071 160226-161110.286 180326-022327.770 2666700 100.0    83     0        0    65   -45994   51   50   83  482
			self.exe_time = int(lines[0].split()[0])

			# # of writes: 2666700
			# # of reads : 13903645
			t1 = lines[2].split("# of writes: ")
			if len(t1) != 2:
				raise RuntimeError("Unexpected format [%s]" % lines[2])
			self.writes = int(t1[1])
			t1 = lines[3].split("# of reads : ")
			if len(t1) != 2:
				raise RuntimeError("Unexpected format [%s]" % lines[3])
			self.reads  = int(t1[1])

			self.lat_w = _Latency(lines[8])
			self.lat_r = _Latency(lines[10])

	def __str__(self):
		items = []
		for i in sorted(vars(self).items()):
			if i[0] == "raw_line":
				continue
			items.append("%s=%s" % (i[0], i[1]))
			#Cons.P("%s:%s" % (i[0], i[1]))
		return "[%s]" % (" ".join(items))


def _LoadData():
	global _exps_by_storage
	fn = "data/%s" % Conf.Get("exp_datetime")
	with Cons.MeasureTime("Reading data file %s ..." % fn):
		with open(fn) as fo:
			for line in fo.readlines():
				line = line.strip()
				if len(line) == 0:
					continue
				if line[0] == "#":
					continue
				ei = ExpItem(line)
				if ei.storage not in _exps_by_storage:
					_exps_by_storage[ei.storage] = []
				_exps_by_storage[ei.storage].append(ei)

		#for st, rows in _exps_by_storage.iteritems():
		#	Cons.P("%s %s" % (st, rows))


def _SetSaturatedBorder():
	for st, rows in _exps_by_storage.iteritems():
		rows.sort(key=operator.attrgetter("lat_w.avg"))
		r_prev = None
		for r in rows:
			if r.saturated == 2:
				if r_prev == None:
					raise RuntimeError("Unexpected row [%s]" % r)
				r_prev.saturated = 1
				break
			r_prev = r


def _GenPlotData():
	global _fn_plot_data
	with Cons.MeasureTime("Generating plot data ..."):
		_fn_plot_data = "data/throughput-latency-%s" % Conf.Get("exp_datetime")
		with open(_fn_plot_data, "w") as fo:
			fmt = "%13s %7d %8d %7d %8.2f" \
					" %6.2f %4d %4d %6.2f %4d %4d" \
					" %1d"
			fo.write("%s\n" % Util.BuildHeader(fmt, \
					"storage_type num_writes num_reads exe_time_ms throughput_ops_per_sec" \
					" lat_w_avg_ms lat_w_50_ms lat_w_99_ms lat_r_avg_ms lat_r_50_ms lat_r_99_ms" \
					" server_saturated" \
					))
			# Order by storage type, writes
			for s, rows in _exps_by_storage.iteritems():
				rows.sort(key=operator.attrgetter("writes"))
				for r in rows:
					fo.write((fmt + "\n") % (("\"%s\"" % s), r.writes, r.reads, r.exe_time
						, float(r.writes + r.reads) * 1000.0 / r.exe_time
						, r.lat_w.avg, r.lat_w._50, r.lat_w._99
						, r.lat_r.avg, r.lat_r._50, r.lat_r._99
						, r.saturated
						))
				fo.write("\n")
		Cons.P("Created file %s %d" % (_fn_plot_data, os.path.getsize(_fn_plot_data)))
