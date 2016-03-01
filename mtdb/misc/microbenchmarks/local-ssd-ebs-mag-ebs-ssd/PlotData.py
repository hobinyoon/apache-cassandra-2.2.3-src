import os
import sys

sys.path.insert(0, "../../../util/python")
import Cons
import Util

import Conf

def Gen():
	_LoadData()
	_GenPlotData()


_fn_plot_data = None
_latencies = []

def _LoadData():
	#storage_types = ["local-ssd", "ebs-ssd-iop", "ebs-ssd-gp2", "ebs-mag"]
	storage_types = ["local-ssd", "ebs-ssd-gp2", "ebs-mag"]
	c_or_d = ["cached", "direct"]

	with Cons.MeasureTime("Reading data files ..."):
		for st in storage_types:
			for cd in c_or_d:
				#Cons.P("%s %s" % (cd, s))
				_latencies.append(ReadLat(cd, st))


def _GenPlotData():
	global _fn_plot_data
	with Cons.MeasureTime("Generating plot data ..."):
		_fn_plot_data = "data/stg-cost-latency-%s.%s" % (Conf.Get("exp_hostname"), Conf.Get("exp_datetime"))
		with open(_fn_plot_data, "w") as fo:
			fmt = "%13s %9.3f %7.1f %7.1f %8.6f"
			#Cons.P(Util.BuildHeader(fmt, "storage_type avg_read_us read_1p_us read_99p_us cost($/GB/Month)"))
			fo.write("%s\n" % Util.BuildHeader(fmt, "storage_type avg_read_us read_1p_us read_99p_us cost($/GB/Month)"))
			for l in _latencies:
				if l.c_or_d == "cached":
					continue
				#Cons.P(fmt % (l.storage_type, l.read_avg, l.read_1, l.read_99, _StgCost(l.storage_type)))
				fo.write((fmt + "\n") % ("\"%s\"" % l.plot_label, l.read_avg, l.read_1, l.read_99, _StgCost(l.storage_type)))
		Cons.P("Created file %s %d" % (_fn_plot_data, os.path.getsize(_fn_plot_data)))


def _StgCost(storage_type):
	#Cons.P(Conf.Get("stg_cost"))
	return Conf.Get("stg_cost")[storage_type]


class ReadLat(object):
	def __init__(self, c_or_d, storage_type):
		self.c_or_d = c_or_d
		self.storage_type = storage_type
		self.fn = "data/%s.%s.%s-%s" % (Conf.Get("exp_hostname"), Conf.Get("exp_datetime"), storage_type, c_or_d)
		self.read_times_us = []
		self.plot_label = None
		if storage_type == "local-ssd":
			self.plot_label = "Ins SSD"
		elif storage_type == "ebs-ssd-iop":
			self.plot_label = "EBS SSD PIO"
		elif storage_type == "ebs-ssd-gp2":
			self.plot_label = "EBS SSD"
		elif storage_type == "ebs-mag":
			self.plot_label = "EBS Mag"

		self.ReadFile()
	
	def ReadFile(self):
		#with Cons.MeasureTime("Reading file %s ..." % self.fn):
		#Cons.P("%s %d" % (self.fn, os.path.getsize(self.fn)))
		with open(self.fn) as fo:
			for line in fo.readlines():
				# 4.0 KiB from /mnt/ebs-mag/ioping-test (ext4 /dev/xvdc): request=14 time=1 us
				tokens = line.split("time=")
				if len(tokens) != 2:
					continue
				t1 = tokens[1].split()
				if len(t1) != 2:
					raise RuntimeError("Unexpected format [%s]" % line)
				read_time_us = float(t1[0])
				if t1[1] == "us":
					pass
				elif t1[1] == "ms":
					read_time_us *= 1000.0
				elif t1[1] == "s":
					read_time_us *= 1000000.0
				else:
					raise RuntimeError("Unexpected format [%s]" % line)
				#sys.stdout.write("%f " % read_time_us)
				self.read_times_us.append(read_time_us)
		self.CalcStat()
	
	def CalcStat(self):
		#Cons.P("%d" % len(self.read_times_us))
		self.read_avg = sum(self.read_times_us) / float(len(self.read_times_us))
		self.read_times_us.sort()
		idx = int(0.01 * len(self.read_times_us))
		self.read_1 = self.read_times_us[idx]
		idx = int(0.99 * len(self.read_times_us))
		self.read_99 = self.read_times_us[idx]
		#Cons.P("avg=%9.3f 1%%=%9.3f 99%%=%9.3f" % (self.read_avg, self.read_1, self.read_99))
