import os
import re
import sys

sys.path.insert(0, "../../util/python")
import Cons
import Util

import Conf


def Read(log_datetime, loadgen_log):
	# If the digested file doesn't exist, read the raw one and create one
	fn_digested = "plot-data/collectl-digested-%s" % log_datetime
	if not os.path.isfile(fn_digested):
		rlp = _ParseRawLog(log_datetime, loadgen_log)
	return _LogDigested(fn_digested)


class _ParseRawLog:
	def __init__(self, log_datetime, loadgen_log):
		self.time_res_usage = {}
		self.log_datetime = log_datetime
		self._ParseFile(loadgen_log)


	def _ParseFile(self, loadgen_log):
		self.loadgen_exp_dt_begin = loadgen_log.ExpBegin().strftime("%H:%M:%S.%f")[:-3]
		self.loadgen_exp_dt_end = loadgen_log.ExpEnd().strftime("%H:%M:%S.%f")[:-3]
		if self.loadgen_exp_dt_begin >= self.loadgen_exp_dt_end:
			raise RuntimeError("Exp begin time(%s) is smaller than end time(%s)."
					"Collectl log time doesn't have a date part :("
					% (self.loadgen_exp_dt_begin, self.loadgen_exp_dt_end))

		# TODO: what I want
		# - CPU
		#     (user, kernel, iowait) * (avg, min, max, _50, _99)
		# - Disk usage: (per device) * (what?)
		# - Network usage: eth0 in/out. Check if it is saturated or what.
		# - Mem is always full, since it is pressured. Linux buffer cache is assumed to be always full.

		raw_lines = []
		fn_raw = "../../logs/collectl/collectl-%s" % self.log_datetime
		with open(fn_raw) as fo:
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

		#self._ReportByTime()
		#self._ReportAvg()
		# May want 99th percentile? Think about it later.

		self._CreateDigestFile()


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
		if time <= self.loadgen_exp_dt_begin:
			return
		if self.loadgen_exp_dt_end <= time:
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
		if time <= self.loadgen_exp_dt_begin:
			return
		if self.loadgen_exp_dt_end <= time:
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
		# ### RECORD    7 >>> s0-c3-2xlarge-02 <<< (1456931323.001) (Wed Mar  2.001 15:08:43) ###
		#
		# #Time         Num    Name   KBIn  PktIn SizeIn  MultI   CmpI  ErrsI  KBOut PktOut  SizeO   CmpO  ErrsO
		# 15:08:43.001    0    eth0      0      3     66      0      0      0      2      3    686      0      0
		# 15:08:43.001    1      lo      0      0      0      0      0      0      0      0      0      0      0
		if len(line) == 0:
			return
		if line[0] == "#":
			return
		t = line.split()
		if len(t) != 14:
			return

		time = t[0]
		# Scope time range by the loadgen time range
		if time <= self.loadgen_exp_dt_begin:
			return
		if self.loadgen_exp_dt_end <= time:
			self.parse_time_passed_exp_time_end = True
			return

		intf = t[2]
		if intf != "eth0":
			return

		kb_in   = t[3]
		pkt_in  = t[4]
		size_in = t[5]
		mult_i  = t[6]
		cmp_i   = t[7]
		errs_i  = t[8]
		kb_out  = t[9]
		pkt_out = t[10]
		size_o  = t[11]
		cmp_o   = t[12]
		errs_o  = t[13]

		if time not in self.time_res_usage:
			self.time_res_usage[time] = _ResUsage()
		self.time_res_usage[time].AddNetwork(kb_in, pkt_in, size_in, mult_i, cmp_i, errs_i, kb_out, pkt_out, size_o, cmp_o, errs_o)

	def _ReportByTime(self):
		fmt = "%12s %3d %3d %3d" \
				" %5d %4d" \
				" %5d %4d" \
				" %4d %4d" \
				" %3d %2d %2d" \
				" %4d %4d %4d %1d %1d %1d" \
				" %4d %4d %4d %1d %1d"

		# TODO: could be something else, or multiple if you use multiple storages
		disk_dev_name = "xvdb"

		Cons.P(Util.BuildHeader(fmt,
			"time cpu.user cpu.sys cpu.wait"
			" disk.%s.read_kb disk.%s.read_io"
			" disk.%s.write_kb disk.%s.write_io"
			" disk.%s.rw_size disk.%s.q_len"
			" disk.%s.wait disk.%s.svc_time disk.%s.util"
			" net.kb_in net.pkt_in net.size_in net.mult_i net.cmp_i net.errs_i"
			" net.kb_out net.pkt_out net.size_o net.cmp_o net.errs_o"
			% (disk_dev_name, disk_dev_name
				, disk_dev_name, disk_dev_name
				, disk_dev_name, disk_dev_name
				, disk_dev_name, disk_dev_name, disk_dev_name)
			))

		for time, ru in sorted(self.time_res_usage.iteritems()):
			Cons.P(fmt % (
				time
				, ru.CpuAttr("user"), ru.CpuAttr("sys"), ru.CpuAttr("wait")
				, ru.DiskAttr(disk_dev_name, "read_kb"), ru.DiskAttr(disk_dev_name, "read_io")
				, ru.DiskAttr(disk_dev_name, "write_kb"), ru.DiskAttr(disk_dev_name, "write_io")
				, ru.DiskAttr(disk_dev_name, "rw_size"), ru.DiskAttr(disk_dev_name, "q_len")
				, ru.DiskAttr(disk_dev_name, "wait"), ru.DiskAttr(disk_dev_name, "svc_time"), ru.DiskAttr(disk_dev_name, "util")
				, ru.NetAttr("kb_in"), ru.NetAttr("pkt_in") , ru.NetAttr("size_in") , ru.NetAttr("mult_i") , ru.NetAttr("cmp_i") , ru.NetAttr("errs_i")
				, ru.NetAttr("kb_out") , ru.NetAttr("pkt_out") , ru.NetAttr("size_o") , ru.NetAttr("cmp_o") , ru.NetAttr("errs_o")
				))

	def _ReportAvg(self):
		# TODO: need to be presented with other metrics

		fmt = "%5.2f %5.2f %5.2f" \
				" %7.2f %6.2f" \
				" %7.2f %6.2f" \
				" %6.2f %6.2f" \
				" %5.2f %4.2f %4.2f" \
				" %4d %4d %4d %1d %1d %1d" \
				" %4d %4d %4d %1d %1d"

		# TODO: could be something else, or multiple if you use multiple storages
		#   xvda: EBS SSD
		#   xvdb: First local SSD
		#   xvdc: (Never used). A Second local SSD
		#   xvdd: EBS Magnetic
		disk_dev_name = "xvdb"

		Cons.P(Util.BuildHeader(fmt,
			"cpu.user cpu.sys cpu.wait"
			" disk.%s.read_kb disk.%s.read_io"
			" disk.%s.write_kb disk.%s.write_io"
			" disk.%s.rw_size disk.%s.q_len"
			" disk.%s.wait disk.%s.svc_time disk.%s.util"
			" net.kb_in net.pkt_in net.size_in net.mult_i net.cmp_i net.errs_i"
			" net.kb_out net.pkt_out net.size_o net.cmp_o net.errs_o"
			% (disk_dev_name, disk_dev_name
				, disk_dev_name, disk_dev_name
				, disk_dev_name, disk_dev_name
				, disk_dev_name, disk_dev_name, disk_dev_name)
			))

		cpu_user = 0
		cpu_sys  = 0
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
		net_kb_in   = 0
		net_pkt_in  = 0
		net_size_in = 0
		net_mult_i  = 0
		net_cmp_i   = 0
		net_errs_i  = 0
		net_kb_out  = 0
		net_pkt_out = 0
		net_size_o  = 0
		net_cmp_o   = 0
		net_errs_o  = 0

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
			net_kb_in   += ru.NetAttr("kb_in")
			net_pkt_in  += ru.NetAttr("pkt_in")
			net_size_in += ru.NetAttr("size_in")
			net_mult_i  += ru.NetAttr("mult_i")
			net_cmp_i   += ru.NetAttr("cmp_i")
			net_errs_i  += ru.NetAttr("errs_i")
			net_kb_out  += ru.NetAttr("kb_out")
			net_pkt_out += ru.NetAttr("pkt_out")
			net_size_o  += ru.NetAttr("size_o")
			net_cmp_o   += ru.NetAttr("cmp_o")
			net_errs_o  += ru.NetAttr("errs_o")

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
		net_kb_in   /= len_
		net_pkt_in  /= len_
		net_size_in /= len_
		net_mult_i  /= len_
		net_cmp_i   /= len_
		net_errs_i  /= len_
		net_kb_out  /= len_
		net_pkt_out /= len_
		net_size_o  /= len_
		net_cmp_o   /= len_
		net_errs_o  /= len_

		Cons.P(fmt % (
			cpu_user, cpu_sys, cpu_wait
			, disk_read_kb, disk_read_io
			, disk_write_kb, disk_write_io
			, disk_rw_size, disk_q_len, disk_wait, disk_svc_time, disk_util
			, net_kb_in, net_pkt_in, net_size_in, net_mult_i, net_cmp_i, net_errs_i
			, net_kb_out, net_pkt_out, net_size_o, net_cmp_o, net_errs_o
			))

	# Collectl stat by time
	def _CreateDigestFile(self):
		fn = "plot-data/collectl-digested-%s" % self.log_datetime
		with open(fn, "w") as fo:
			fmt = "%12s %3d %3d %3d" \
					" %5d %4d" \
					" %5d %4d" \
					" %4d %4d" \
					" %3d %2d %2d" \
					" %4d %4d %4d %1d %1d %1d" \
					" %4d %4d %4d %1d %1d"

			# TODO: could be something else, or multiple if you use multiple storages
			disk_dev_name = "xvdb"

			fo.write("%s\n" % Util.BuildHeader(fmt,
				"time cpu.user cpu.sys cpu.wait"
				" disk.%s.read_kb disk.%s.read_io"
				" disk.%s.write_kb disk.%s.write_io"
				" disk.%s.rw_size disk.%s.q_len"
				" disk.%s.wait disk.%s.svc_time disk.%s.util"
				" net.kb_in net.pkt_in net.size_in net.mult_i net.cmp_i net.errs_i"
				" net.kb_out net.pkt_out net.size_o net.cmp_o net.errs_o"
				% (disk_dev_name, disk_dev_name
					, disk_dev_name, disk_dev_name
					, disk_dev_name, disk_dev_name
					, disk_dev_name, disk_dev_name, disk_dev_name)
				))

			for time, ru in sorted(self.time_res_usage.iteritems()):
				fo.write("%s\n" % (fmt % (
					time
					, ru.CpuAttr("user"), ru.CpuAttr("sys"), ru.CpuAttr("wait")
					, ru.DiskAttr(disk_dev_name, "read_kb"), ru.DiskAttr(disk_dev_name, "read_io")
					, ru.DiskAttr(disk_dev_name, "write_kb"), ru.DiskAttr(disk_dev_name, "write_io")
					, ru.DiskAttr(disk_dev_name, "rw_size"), ru.DiskAttr(disk_dev_name, "q_len")
					, ru.DiskAttr(disk_dev_name, "wait"), ru.DiskAttr(disk_dev_name, "svc_time"), ru.DiskAttr(disk_dev_name, "util")
					, ru.NetAttr("kb_in"), ru.NetAttr("pkt_in") , ru.NetAttr("size_in") , ru.NetAttr("mult_i") , ru.NetAttr("cmp_i") , ru.NetAttr("errs_i")
					, ru.NetAttr("kb_out") , ru.NetAttr("pkt_out") , ru.NetAttr("size_o") , ru.NetAttr("cmp_o") , ru.NetAttr("errs_o")
					)))
		Cons.P("Created a digest file %s %d" % (fn, os.path.getsize(fn)))


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

	class Network:
		def __init__(self, kb_in, pkt_in, size_in, mult_i, cmp_i, errs_i, kb_out, pkt_out, size_o, cmp_o, errs_o):
			self.kb_in   = int(kb_in)
			self.pkt_in  = int(pkt_in)
			self.size_in = int(size_in)
			self.mult_i  = int(mult_i)
			self.cmp_i   = int(cmp_i)
			self.errs_i  = int(errs_i)
			self.kb_out  = int(kb_out)
			self.pkt_out = int(pkt_out)
			self.size_o  = int(size_o)
			self.cmp_o   = int(cmp_o)
			self.errs_o  = int(errs_o)

		def __repr__(self):
			return "[%s]" % (" ".join("%s=%s" % item for item in vars(self).items()))

	def __init__(self):
		self.cpu = {}
		self.disk = {}
		self.network = None

	def AddCpu(self, cpu_id, user, sys, wait):
		if cpu_id not in self.cpu:
			self.cpu[cpu_id] = _ResUsage.Cpu(user, sys, wait)

	def AddDisk(self, dev_name, read_kb, read_io, write_kb, write_io, rw_size, q_len, wait, svc_time, util):
		if dev_name not in self.disk:
			self.disk[dev_name] = _ResUsage.Disk(read_kb, read_io, write_kb, write_io, rw_size, q_len, wait, svc_time, util)

	def AddNetwork(self, kb_in, pkt_in, size_in, mult_i, cmp_i, errs_i, kb_out, pkt_out, size_o, cmp_o, errs_o):
			self.network = _ResUsage.Network(kb_in, pkt_in, size_in, mult_i, cmp_i, errs_i, kb_out, pkt_out, size_o, cmp_o, errs_o)

	def __str__(self):
		return " ".join("%s=%s" % item for item in vars(self).items())

	def CpuAttr(self, name):
		r = 0
		for k, v in self.cpu.iteritems():
			r += getattr(v, name)
		return r

	def DiskAttr(self, dev_name, attr_name):
		return getattr(self.disk[dev_name], attr_name)

	def NetAttr(self, attr_name):
		return getattr(self.network, attr_name)


class _LogDigested:
	def __init__(self, fn):
		self.time_res_usage = {}
		self.fn = fn
		self._LoadFile()

	def GetAttrAvg(self, attr_name):
		sum = 0
		for k, rum in self.time_res_usage.iteritems():
			sum += getattr(rum, attr_name)
		return float(sum) / len(self.time_res_usage)

	def _LoadFile(self):
		fn = self.fn
		with open(fn) as fo:
			for line in fo.readlines():
				if len(line) == 0:
					continue
				if line[0] == "#":
					continue
				t = line.split()
				if len(t) != 24:
					raise RuntimeError("Unexpected format: [%s]" % line)

				# TODO: implement xvda, xvdd too
				time = t[0]
				self.time_res_usage[time] = _LogDigested.ResUsageMetrics(t)

	class ResUsageMetrics:
		def __init__(self, tokens):
			self.cpu_user           = int(tokens[1])
			self.cpu_sys            = int(tokens[2])
			self.cpu_wait           = int(tokens[3])
			self.disk_xvdb_read_kb  = int(tokens[4])
			self.disk_xvdb_read_io  = int(tokens[5])
			self.disk_xvdb_write_kb = int(tokens[6])
			self.disk_xvdb_write_io = int(tokens[7])
			self.disk_xvdb_rw_size  = int(tokens[8])
			self.disk_xvdb_q_len    = int(tokens[9])
			self.disk_xvdb_wait     = int(tokens[10])
			self.disk_xvdb_svc_time = int(tokens[11])
			self.disk_xvdb_util     = int(tokens[12])
			self.net_kb_in          = int(tokens[13])
			self.net_pkt_in         = int(tokens[14])
			self.net_size_in        = int(tokens[15])
			self.net_mult_i         = int(tokens[16])
			self.net_cmp_i          = int(tokens[17])
			self.net_errs_i         = int(tokens[18])
			self.net_kb_out         = int(tokens[19])
			self.net_pkt_out        = int(tokens[20])
			self.net_size_o         = int(tokens[21])
			self.net_cmp_o          = int(tokens[22])
			self.net_errs_o         = int(tokens[23])
