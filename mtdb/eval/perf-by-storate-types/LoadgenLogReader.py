import operator
import os
import re
import sys

sys.path.insert(0, "../../../util/python")
import Cons
import Util

import Conf

def Read(log_datetime):
	fn = "../../../logs/loadgen/%s" % log_datetime
	lines = []
	with open(fn) as fo:
		for line in fo.readlines():
			line = line.rstrip()
			lines.append(line)
	return Log(lines[-12:])


class Log:
	def __init__(self, lines):
		self._Parse(lines)
	
	def _Parse(self, lines):
		#Cons.P(lines)
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
		line = lines[0]
		t = line.split()
		if len(t) != 14:
			raise RuntimeError("Unexpected format [%s]" % line)
		self.exe_time_ms = int(t[0])

		line = lines[2]
		t = line.split()
		if len(t) != 5:
			raise RuntimeError("Unexpected format [%s]" % line)
		self.num_writes = int(t[4])

		line = lines[3]
		t = line.split()
		if len(t) != 6:
			raise RuntimeError("Unexpected format [%s]" % line)
		self.num_reads = int(t[5])

		self.lat_w = _Latency(lines[8])
		self.lat_r = _Latency(lines[10])

		#Cons.P(self)
	
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
