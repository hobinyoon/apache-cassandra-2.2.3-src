import operator
import os
import re
import sys

sys.path.insert(0, "../../util/python")
import Cons
import Util

import Conf

def Gen():
	_LoadData()
	_GenPlotData()


def Throughput(storage_type, key_max_value):
	rows = _rows_by_storage[storage_type]
	rows.sort(key=operator.attrgetter(key_max_value))
	r = rows[-1]
	return float(r.writes + r.reads) * 1000.0 / r.exe_time


def Latency(storage_type, key_max_value, attr_name):
	rows = _rows_by_storage[storage_type]
	rows.sort(key=operator.attrgetter(key_max_value))
	o = rows[-1]
	for a in attr_name.split("."):
		o = getattr(o, a)
	return o


_rows_by_storage = {}
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
	def __init__(self, raw_lines):
		#Cons.P(raw_lines)
		self.raw_lines = raw_lines
		self._ParseLines()

	def _ParseLines(self):
		i = 0
		while i < len(self.raw_lines):
			line = self.raw_lines[i]
			#Cons.P("line=[%s]" % line)
			if i == 0:
				# Local SSD	160223-052200	10,000	"  # # of writes: 266670
				t = line.split("\t")
				if len(t) != 4:
					raise RuntimeError("Unexpected format [%s]" % line)
				self.storage = t[0]
				self.exp_datetime = t[1]
				# Not very relevant. This is from the loadgen client
				self.num_Ws_per_simulation_time_min = t[2]
				t1 = t[3].split("# of writes: ")
				if len(t1) != 2:
					raise RuntimeError("Unexpected format [%s]" % t[3])
				self.writes = int(t1[1])
			elif "# of reads : " in line:
				t = line.split("# of reads : ")
				if len(t) != 2:
					raise RuntimeError("Unexpected format [%s]" % line)
				self.reads = int(t[1])
			elif "# Write latency:" in line:
				i += 1
				line = self.raw_lines[i]
				self.lat_w = _Latency(line)
			elif "# Read latency:" in line:
				i += 1
				line = self.raw_lines[i]
				self.lat_r = _Latency(line)
			elif i == len(self.raw_lines) - 1:
				t = line.split()
				if (len(t) != 2) or (t[1] != "ms\""):
					raise RuntimeError("Unexpected format [%s]" % line)
				self.exe_time = int(t[0])
			i += 1

	def __str__(self):
		items = []
		for i in sorted(vars(self).items()):
			if i[0] == "raw_lines":
				continue
			items.append("%s=%s" % (i[0], i[1]))
			#Cons.P("%s:%s" % (i[0], i[1]))
		return "[%s]" % (" ".join(items))


def _LoadData():
	global _rows_by_storage
	fn = "data/%s" % Conf.Get("exp_datetime")
	with Cons.MeasureTime("Reading data file %s ..." % fn):
		with open(fn) as fo:
			row_raw_lines = []
			for line in fo.readlines():
				line = line.strip()
				if line.endswith("ms\""):
					#Cons.P(line)
					row_raw_lines.append(line)
					row = ExpItem(row_raw_lines)
					if row.storage not in _rows_by_storage:
						_rows_by_storage[row.storage] = []
					_rows_by_storage[row.storage].append(row)
					row_raw_lines = []
				else:
					row_raw_lines.append(line)
		#for s, rows in _rows_by_storage.iteritems():
		#	Cons.P("%s %s" % (s, rows))


def _GenPlotData():
	global _fn_plot_data
	with Cons.MeasureTime("Generating plot data ..."):
		_fn_plot_data = "data/baseline-throughput-latency-%s" % Conf.Get("exp_datetime")
		with open(_fn_plot_data, "w") as fo:
			fmt = "%13s %7d %8d %7d %8.2f" \
					" %6.2f %4d %4d %6.2f %4d %4d"
			fo.write("%s\n" % Util.BuildHeader(fmt, \
					"storage_type num_writes num_reads exe_time_ms throughput_ops_per_sec" \
					" lat_w_avg_ms lat_w_50_ms lat_w_99_ms lat_r_avg_ms lat_r_50_ms lat_r_99_ms" \
					))
			# Order by storage type, writes
			for s, rows in _rows_by_storage.iteritems():
				rows.sort(key=operator.attrgetter("writes"))
				for r in rows:
					fo.write((fmt + "\n") % (("\"%s\"" % s), r.writes, r.reads, r.exe_time
						, float(r.writes + r.reads) * 1000.0 / r.exe_time
						, r.lat_w.avg, r.lat_w._50, r.lat_w._99
						, r.lat_r.avg, r.lat_r._50, r.lat_r._99
						))
				fo.write("\n")
		Cons.P("Created file %s %d" % (_fn_plot_data, os.path.getsize(_fn_plot_data)))
