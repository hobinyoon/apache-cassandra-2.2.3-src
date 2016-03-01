import os
import subprocess
import sys
import threading
import time

sys.path.insert(0, "../../util/python")
import Cons
import Util

import Conf


# Note: Redirecting output to memory file system may have a lower overhead. Not
# a big deal though.

class Mon:
	mon_interval = 0.1

	def __init__(self, test_name):
		self.test_name = test_name
		self.stop_requested = False
		self.stdout = []

	def __enter__(self):
		# Start monitoring CPU, Disk, Network
		cmd = "collectl -i %f -sCDN -oTm 2>/dev/null" % Mon.mon_interval
		self.subp = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		self.t = threading.Thread(target=self._CollectMonitorOutput)
		self.t.start()

		# collectl has an initial of the monitoring interval. Wait for a bit.
		time.sleep(Mon.mon_interval * 2)

		return self

	def _CollectMonitorOutput(self):
		while not self.stop_requested:
			line = self.subp.stdout.readline()
			self.stdout.append(line)
			#Cons.P(line.rstrip())
		self.subp.kill()
		self.subp.wait()

	def _Stop(self):
		if not self.stop_requested:
			self.stop_requested = True
			self.t.join()

	def __exit__(self, type, value, traceback):
		self._Stop()
		self._WriteToFile()
		_GenConciseReport(self.stdout)

	def _WriteToFile(self):
		fn = "data/%s-%s-collectl" % (Conf.ExpDatetime(), self.test_name)
		with open(fn, "w") as fo:
			for line in self.stdout:
				fo.write(line)
		Cons.P("Saved collectl log to %s %d" % (fn, os.path.getsize(fn)))


def PrintReport(exp_datetime, test_name):
	fn = "data/%s-%s-collectl" % (exp_datetime, test_name)
	#Cons.P("fn=[%s]" % fn)
	with open(fn) as fo:
		_GenConciseReport(fo.readlines())


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


_time_res_usage = {}

def ResAddCpu(time, cpu_id, user, sys, wait):
	global _time_res_usage
	if time not in _time_res_usage:
		_time_res_usage[time] = _ResUsage()
	_time_res_usage[time].AddCpu(cpu_id, user, sys, wait)


def ResAddDisk(time, dev_name, read_kb, read_io, write_kb, write_io, rw_size, q_len, wait, svc_time, util):
	global _time_res_usage
	if time not in _time_res_usage:
		_time_res_usage[time] = _ResUsage()
	_time_res_usage[time].AddDisk(dev_name, read_kb, read_io, write_kb, write_io, rw_size, q_len, wait, svc_time, util)


def _ResUsageReportByTime():
	fmt = "%12s %3d %3d %3d %7d %6d %7d %6d %7d %7d %7d %7d %7d"
	disk_dev_name = "xvdb"
	Cons.P(Util.BuildHeader(fmt,
		"time cpu_user cpu_sys cpu_wait"
		" disk_%s_read_kb"
		" disk_%s_read_io"
		" disk_%s_write_kb"
		" disk_%s_write_io"
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
		))

	global _time_res_usage
	for time, ru in sorted(_time_res_usage.iteritems()):
		Cons.P(fmt % (
			time
			, ru.CpuAttr("user"), ru.CpuAttr("sys"), ru.CpuAttr("wait")
			, ru.DiskAttr(disk_dev_name, "read_kb")
			, ru.DiskAttr(disk_dev_name, "read_io")
			, ru.DiskAttr(disk_dev_name, "write_kb")
			, ru.DiskAttr(disk_dev_name, "write_io")
			, ru.DiskAttr(disk_dev_name, "rw_size")
			, ru.DiskAttr(disk_dev_name, "q_len")
			, ru.DiskAttr(disk_dev_name, "wait")
			, ru.DiskAttr(disk_dev_name, "svc_time")
			, ru.DiskAttr(disk_dev_name, "util")
			))


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

	global _time_res_usage
	for time, ru in _time_res_usage.iteritems():
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

	len_ = float(len(_time_res_usage))
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


def _GenConciseReport(lines):
	# TODO: what I need is probably aggregate stat, like avg, _99th percentile, min, max, not by time

	phase = None
	for line in lines:
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
			# # SINGLE CPU[HYPER] STATISTICS
			# #Time            Cpu  User Nice  Sys Wait IRQ  Soft Steal Idle
			# 14:52:49.732       0     0    0    0    0    0    0     0    0
			# 14:52:49.732       1     0    0    0    0    0    0     0    0
			if line.startswith("#Time"):
				continue
			t = line.split()
			if len(t) != 10:
				# There is a blank line. Ignore.
				continue
			time = t[0]
			cpu_id = t[1]
			user = t[2]
			sys = t[4]
			wait = t[5]
			ResAddCpu(time, cpu_id, user, sys, wait)
		elif phase == "DISK":
			## DISK STATISTICS (/sec)
			##                       <---------reads---------><---------writes---------><--------averages--------> Pct
			##Time         Name       KBytes Merged  IOs Size  KBytes Merged  IOs Size  RWSize  QLen  Wait SvcTim Util
			#14:52:49.732 xvda             0      0    0    0       0      0    0    0       0     0     0      0    0
			#14:52:49.732 xvdb         23996      0 5999    4       0      0    0    0       4     0     0      0    0
			#14:52:49.732 xvdc             0      0    0    0       0      0    0    0       0     0     0      0    0
			#           0    1             2      3    4    5       6      7    8    9      10    11    12     13   14
			if line.startswith("#"):
				continue
			t = line.split()
			if len(t) != 15:
				continue
			time = t[0]
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
			ResAddDisk(time, dev_name, read_kb, read_io, write_kb, write_io, \
					rw_size, q_len, wait, svc_time, util)

	# Trim the first two and last two, which may not overlap with the experiment
	global _time_res_usage
	tru0 = {}
	cnt = 0
	len_tru = len(_time_res_usage)
	for time, ru in sorted(_time_res_usage.iteritems()):
		if cnt < 2:
			pass
		elif cnt >= len_tru - 2:
			pass
		else:
			tru0[time] = ru
			pass
		cnt += 1
	_time_res_usage = tru0

	# TODO: network report too, eth0 probably
	#_ResUsageReportByTime()
	_ResUsageReportAggr()


#14:52:49.732 xvdd             0      0    0    0       0      0    0    0       0     0     0      0    0
#
## NETWORK STATISTICS (/sec)


def _TestParse():
	fn = "data/160229-170819-4k-rand-read-Local-SSD-collectl"
	with open(fn) as fo:
		_GenConciseReport(fo.readlines())
