import operator
import os
import re
import sys

sys.path.insert(0, "../../util/python")
import Cons
import Util

import Conf

def Read(log_datetime):
	fn = "../../logs/loadgen/%s" % log_datetime
	return Log(fn)


class Log:
	def __init__(self, fn):
		self.fn = fn
		self._Parse(fn)
	
	def _Parse(self, fn):
		raw_lines = []
		with open(fn) as fo:
			for line in fo.readlines():
				line = line.rstrip()
				raw_lines.append(line)

		self._ParseStartTime(raw_lines)

		# TODO: _ParseTail()




		lines_tail = raw_lines[-12:]
		#Cons.P(lines_tail)
		#  0 1600025 160302-200229.382 180101-001411.305  266670 100.0     1     0        0     0        0    0    3    1    8
		#  1 #
		#  2 # # of writes: 266670
		#  3 # # of reads : 1390809
		#  4 # # reads / write:
		#  5 #   avg= 5.215 min=    0 max= 783 50=   2 90=  11 95=  19 99=  57 995=  86 999= 184
		#  6 #
		#  7 # Write latency:
		#  8 #   avg= 2.560 min=0.470 max=1328 50=   0 90=   0 95=   0 99=   8 995=  87 999= 494
		#  9 # Read latency:
		# 10 #   avg= 1.696 min=0.582 max=1285 50=   0 90=   0 95=   1 99=   3 995=  21 999= 227
		# 11 1602454 ms
		# 12 24 ms
		line = lines_tail[0]
		t = line.split()
		if len(t) != 14:
			raise RuntimeError("Unexpected format [%s]" % line)
		self.exe_time_ms = int(t[0])

		line = lines_tail[2]
		t = line.split()
		if len(t) != 5:
			raise RuntimeError("Unexpected format [%s]" % line)
		self.num_writes = int(t[4])

		line = lines_tail[3]
		t = line.split()
		if len(t) != 6:
			raise RuntimeError("Unexpected format [%s]" % line)
		self.num_reads = int(t[5])

		self.lat_w = _Latency(lines_tail[8])
		self.lat_r = _Latency(lines_tail[10])

		#Cons.P(self)

	def _ParseStartTime(self, raw_lines):
		lines = raw_lines
		first_body_line = None
		for i in range(200):
			line = lines[i]
			#Cons.P(line)
			t = line.split()
			if len(t) <= 9:
				continue
			detected_header = True
			for j in range(1, 9):
				#Cons.P("%d %s" % (j, t[j]))
				if int(t[j]) != j:
					detected_header = False
					break
			if detected_header == True:
				first_body_line = lines[i + 1]
				break
		if first_body_line == None:
			raise RuntimeError("Cannot find the first body line. fn=[%s]", self.fn)
		#Cons.P(first_body_line)
		t = first_body_line.split()
		lap_time_ms = t[0]
		cur_dt = t[1]

		sys.exit(0)

	
	# IOs / sec
	def Throughput(self):
		return (self.num_writes + self.num_reads) * 1000.0 / self.exe_time_ms
	
	def __str__(self):
		return " ".join("%s=%s" % item for item in vars(self).items())


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
