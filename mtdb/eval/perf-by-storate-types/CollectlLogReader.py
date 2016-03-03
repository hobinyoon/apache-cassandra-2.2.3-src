import os
import re
import sys

sys.path.insert(0, "../../util/python")
import Cons
import Util

import Conf


def Read(log_datetime, loadgen_log):
	fn = "../../logs/collectl/collectl-%s" % log_datetime
	#Cons.P(fn)
	return Log(fn, loadgen_log)


class Log:
	def __init__(self, fn, loadgen_log):
		self.fn = fn
		self.exp_dt_begin = loadgen_log.ExpBegin().strftime("%H:%M:%S.%f")[:-3]
		self.exp_dt_end = loadgen_log.ExpEnd().strftime("%H:%M:%S.%f")[:-3]
		#Cons.P(self.exp_dt_begin)
		#Cons.P(self.exp_dt_end)
		if self.exp_dt_begin >= self.exp_dt_end:
			raise RuntimeError("Exp begin time(%s) is smaller than end time(%s)."
					"Collectl log time doesn't have a date part :("
					% (self.exp_dt_begin, self.exp_dt_end))
		self.time_res_usage = {}
		self._ParseFile()

	def _ParseFile(self):
		# TODO: will want to make a concise, intermediate data file

		# TODO: what I want
		# - CPU
		#     (user, kernel, iowait) * (avg, min, max, _50, _99)
		# - Disk usage: (per device) * (what?)
		# - Network usage: eth0 in/out. Check if it is saturated or what.
		# - Mem is always full, since it is pressured. Linux buffer cache is assumed to be always full.

		raw_lines = []
		with open(self.fn) as fo:
			for line in fo.readlines():
				raw_lines.append(line.rstrip())
	
		phase = None
		self.parse_time_passed_exp_time_end = False
		for line in raw_lines:
			if self.parse_time_passed_exp_time_end:
				break
			if line.startswith("# SINGLE CPU[HYPER] STATISTICS"):
				phase = "CPU"
				continue
			elif line.startswith("# DISK STATISTICS"):
				phase = "DISK"
				continue
			elif line.startswith("# NETWORK STATISTICS"):
				phase = "NET"
				continue

			if phase == "CPU":
				self._ParseCpu(line)
			elif phase == "DISK":
				self._ParseDisk(line)
			elif phase == "NET":
				self._ParseNetwork(line)

		self._ReportByTime()
		sys.exit(0)
		_ResUsageReportAggr()





	def _ParseCpu(self, line):
		# # SINGLE CPU[HYPER] STATISTICS
		# #Time            Cpu  User Nice  Sys Wait IRQ  Soft Steal Idle
		# 14:52:49.732       0     0    0    0    0    0    0     0    0
		# 14:52:49.732       1     0    0    0    0    0    0     0    0
		if line.startswith("#Time"):
			return
		t = line.split()
		if len(t) != 10:
			# There are blank lines. Ignore.
			return

		time = t[0]
		# Scope time range by the loadgen time range
		if time <= self.exp_dt_begin:
			return
		if self.exp_dt_end <= time:
			self.parse_time_passed_exp_time_end = True
			return

		cpu_id = t[1]
		user = t[2]
		sys_ = t[4]
		wait = t[5]

		if time not in self.time_res_usage:
			self.time_res_usage[time] = _ResUsage()
		self.time_res_usage[time].AddCpu(cpu_id, user, sys_, wait)

	def _ParseDisk(self, line):
		# # DISK STATISTICS (/sec)
		# #                       <---------reads---------><---------writes---------><--------averages--------> Pct
		# #Time         Name       KBytes Merged  IOs Size  KBytes Merged  IOs Size  RWSize  QLen  Wait SvcTim Util
		# 14:52:49.732 xvda             0      0    0    0       0      0    0    0       0     0     0      0    0
		# 14:52:49.732 xvdb         23996      0 5999    4       0      0    0    0       4     0     0      0    0
		# 14:52:49.732 xvdc             0      0    0    0       0      0    0    0       0     0     0      0    0
		#            0    1             2      3    4    5       6      7    8    9      10    11    12     13   14
		if line.startswith("#"):
			return
		t = line.split()
		if len(t) != 15:
			return

		time = t[0]
		# Scope time range by the loadgen time range
		if time <= self.exp_dt_begin:
			return
		if self.exp_dt_end <= time:
			self.parse_time_passed_exp_time_end = True
			return

		dev_name = t[1]
		read_kb = t[2]
		read_io = t[4]
		write_kb = t[6]
		write_io = t[8]

		rw_size = t[10]
		# TODO: can q_len be a hint?
		q_len = t[11]
		wait = t[12]
		svc_time = t[13]
		util = t[14]

		if time not in self.time_res_usage:
			self.time_res_usage[time] = _ResUsage()
		self.time_res_usage[time].AddDisk(dev_name, read_kb, read_io, write_kb, write_io, rw_size, q_len, wait, svc_time, util)

	def _ParseNetwork(self, line):
		# TODO: network too. eth0 probably

		# 14:52:49.732 xvdd             0      0    0    0       0      0    0    0       0     0     0      0    0
		#
		# # NETWORK STATISTICS (/sec)
		pass

	def _ReportByTime(self):
		fmt = "%12s %3d %3d %3d" \
				" %5d %4d" \
				" %5d %4d" \
				" %4d %4d" \
				" %3d %2d %2d"
		disk_dev_name = "xvdb"
		Cons.P(Util.BuildHeader(fmt,
			"time cpu.user cpu.sys cpu.wait"
			" disk.%s.read_kb disk.%s.read_io"
			" disk.%s.write_kb disk.%s.write_io"
			" disk.%s.rw_size disk.%s.q_len"
			" disk.%s.wait"
			" disk.%s.svc_time"
			" disk.%s.util"
			% (disk_dev_name, disk_dev_name
				, disk_dev_name, disk_dev_name
				, disk_dev_name, disk_dev_name
				, disk_dev_name
				, disk_dev_name
				, disk_dev_name)
			))

		for time, ru in sorted(self.time_res_usage.iteritems()):
			Cons.P(fmt % (
				time
				, ru.CpuAttr("user"), ru.CpuAttr("sys"), ru.CpuAttr("wait")
				, ru.DiskAttr(disk_dev_name, "read_kb"), ru.DiskAttr(disk_dev_name, "read_io")
				, ru.DiskAttr(disk_dev_name, "write_kb"), ru.DiskAttr(disk_dev_name, "write_io")
				, ru.DiskAttr(disk_dev_name, "rw_size"), ru.DiskAttr(disk_dev_name, "q_len")
				, ru.DiskAttr(disk_dev_name, "wait")
				, ru.DiskAttr(disk_dev_name, "svc_time")
				, ru.DiskAttr(disk_dev_name, "util")
				))


# TODO: clean up
#		_GenConciseReport(self.stdout)
#
#	def _WriteToFile(self):
#		fn = "data/%s-%s-collectl" % (Conf.ExpDatetime(), self.test_name)
#		with open(fn, "w") as fo:
#			for line in self.stdout:
#				fo.write(line)
#		Cons.P("Saved collectl log to %s %d" % (fn, os.path.getsize(fn)))


def Test():
	#_TestMon()
	_TestParse()


def _TestMon():
	with Mon() as srm:
		for i in range(2):
			time.sleep(1)


class _ResUsage:
	class Cpu:
		def __init__(self, user, sys, wait):
			self.user = int(user)
			self.sys = int(sys)
			self.wait = int(wait)

		# Interesting. This is called instead of __str__
		def __repr__(self):
			return "[%s]" % (" ".join("%s=%s" % item for item in vars(self).items()))

	class Disk:
		def __init__(self, read_kb, read_io, write_kb, write_io, rw_size, q_len, wait, svc_time, util):
			self.read_kb = int(read_kb)
			self.read_io = int(read_io)
			self.write_kb = int(write_kb)

			# For example, 10K
			if write_io.endswith("K"):
				self.write_io = int(write_io[:len(write_io)-1]) * 1000
			else:
				self.write_io = int(write_io)

			self.rw_size = int(rw_size)
			self.q_len = int(q_len)
			self.wait = int(wait)
			self.svc_time = int(svc_time)
			self.util = int(util)

		def __repr__(self):
			return "[%s]" % (" ".join("%s=%s" % item for item in vars(self).items()))

	def __init__(self):
		self.cpu = {}
		self.disk = {}

	def AddCpu(self, cpu_id, user, sys, wait):
		if cpu_id not in self.cpu:
			self.cpu[cpu_id] = _ResUsage.Cpu(user, sys, wait)

	def AddDisk(self, dev_name, read_kb, read_io, write_kb, write_io, rw_size, q_len, wait, svc_time, util):
		if dev_name not in self.disk:
			self.disk[dev_name] = _ResUsage.Disk(read_kb, read_io, write_kb, write_io, rw_size, q_len, wait, svc_time, util)

	def __str__(self):
		return " ".join("%s=%s" % item for item in vars(self).items())

	def CpuAttr(self, name):
		r = 0
		for k, v in self.cpu.iteritems():
			r += getattr(v, name)
		return r

	def DiskAttr(self, dev_name, attr_name):
		return getattr(self.disk[dev_name], attr_name)


def _ResUsageReportAggr():
	Cons.P("Resource usage stat:")
	fmt = "%6.2f %6.2f %6.2f %10.2f %9.2f %10.2f %9.2f %10.2f %10.2f %10.2f %10.2f %10.2f"
	disk_dev_name = "xvdb"
	Cons.P(Util.Indent(Util.BuildHeader(fmt,
		"cpu_user cpu_sys cpu_wait"
		" disk_%s_read_kb disk_%s_read_io"
		" disk_%s_write_kb disk_%s_write_io"
		" disk_%s_rw_size"
		" disk_%s_q_len"
		" disk_%s_wait"
		" disk_%s_svc_time"
		" disk_%s_util"
		% (disk_dev_name
			, disk_dev_name
			, disk_dev_name
			, disk_dev_name
			, disk_dev_name
			, disk_dev_name
			, disk_dev_name
			, disk_dev_name
			, disk_dev_name)
		), 2))

	cpu_user = 0
	cpu_sys = 0
	cpu_wait = 0
	disk_read_kb  = 0
	disk_read_io  = 0
	disk_write_kb = 0
	disk_write_io = 0
	disk_rw_size  = 0
	disk_q_len    = 0
	disk_wait     = 0
	disk_svc_time = 0
	disk_util     = 0

	for time, ru in self.time_res_usage.iteritems():
		cpu_user += ru.CpuAttr("user")
		cpu_sys  += ru.CpuAttr("sys")
		cpu_wait += ru.CpuAttr("wait")
		disk_read_kb  += ru.DiskAttr(disk_dev_name, "read_kb")
		disk_read_io  += ru.DiskAttr(disk_dev_name, "read_io")
		disk_write_kb += ru.DiskAttr(disk_dev_name, "write_kb")
		disk_write_io += ru.DiskAttr(disk_dev_name, "write_io")
		disk_rw_size  += ru.DiskAttr(disk_dev_name, "rw_size")
		disk_q_len    += ru.DiskAttr(disk_dev_name, "q_len")
		disk_wait     += ru.DiskAttr(disk_dev_name, "wait")
		disk_svc_time += ru.DiskAttr(disk_dev_name, "svc_time")
		disk_util     += ru.DiskAttr(disk_dev_name, "util")

	len_ = float(len(self.time_res_usage))
	cpu_user /= len_
	cpu_sys  /= len_
	cpu_wait /= len_
	disk_read_kb  /= len_
	disk_read_io  /= len_
	disk_write_kb /= len_
	disk_write_io /= len_
	disk_rw_size  /= len_
	disk_q_len    /= len_
	disk_wait     /= len_
	disk_svc_time /= len_
	disk_util     /= len_

	Cons.P(Util.Indent(fmt % (
		cpu_user , cpu_sys , cpu_wait
		, disk_read_kb , disk_read_io
		, disk_write_kb , disk_write_io
		, disk_rw_size , disk_q_len , disk_wait , disk_svc_time , disk_util
		), 2))




def _TestParse():
	fn = "data/160229-170819-4k-rand-read-Local-SSD-collectl"
	with open(fn) as fo:
		_GenConciseReport(fo.readlines())





























