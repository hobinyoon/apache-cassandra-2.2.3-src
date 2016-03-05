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
	with Cons.MeasureTime("Loading exp data ..."):
		global _exp_groups
		for egn in Conf.Get("exp_result"):
			fn_exp_group_result = "plot-data/%s" % egn
			if not os.path.isfile(fn_exp_group_result):
				_GenExpGroupReport(egn)
			_exp_groups[egn] = _LoadExpGroupReport(fn_exp_group_result)


def LastExpAttr(exp_group_name, attr_name):
	global _exp_groups
	return getattr(_exp_groups[exp_group_name].items[-1], attr_name)


def MaxExpAttr(attr_name, egns = None):
	global _exp_groups
	if egns == None:
		v = None
		for egn, eg in _exp_groups.iteritems():
			#Cons.P("egn=%s" % egn)
			#Cons.P("len(eg.items)=%d" % len(eg.items))
			for i in eg.items:
				#Cons.P(getattr(i, attr_name))
				if v == None:
					v = getattr(i, attr_name)
				else:
					v = max(v, getattr(i, attr_name))
	else:
		v = None
		for egn in egns:
			eg = _exp_groups[egn]
			for i in eg.items:
				if v == None:
					v = getattr(i, attr_name)
				else:
					v = max(v, getattr(i, attr_name))
	return v


class _GenExpGroupReport():
	def __init__(self, exp_group_name):
		self.fn_exp_list = "exp-results/%s" % Conf.Get("exp_result")[exp_group_name]
		self.exp_group_name = exp_group_name
		self.exps = []
		with Cons.MeasureTime("Generating exp group report for %s ..." % self.exp_group_name):
			self._Load()
			self._GenReport()

	def _Load(self):
		with open(self.fn_exp_list) as fo:
			for line in fo.readlines():
				#Cons.P(line)
				line = line.rstrip()
				if len(line) == 0:
					continue
				if line[0] == "#":
					continue
				self.exps.append(_GenExpGroupReport.Exp(line))
		#Cons.P(self)

	def _GenReport(self):
		fn_exp_group_result = "plot-data/%s" % self.exp_group_name
		fn = fn_exp_group_result
		with open(fn, "w") as fo:
			fo.write("# storage_type: %s\n" % self.exp_group_name)
			fo.write("#\n")
			fmt = "%13s" \
					" %7d %7d %8d" \
					" %5.0f" \
					" %7.3f %3.0f %4.0f" \
					" %7.3f %3.0f %4.0f" \
					" %2d" \
					" %2d %3d" \
					" %6.2f %6.2f %6.2f" \
					\
					" %8.2f %7.2f" \
					" %8.2f %6.2f" \
					" %5.2f %5.2f %6.2f %5.2f %5.2f" \
					\
					" %8.2f %7.2f" \
					" %8.2f %6.2f" \
					" %5.2f %5.2f %6.2f %5.2f %5.2f" \
					\
					" %8.2f %7.2f" \
					" %8.2f %6.2f" \
					" %5.2f %5.2f %6.2f %5.2f %5.2f" \
					\
					" %5.0f %5.0f"
			fo.write("%s\n" % Util.BuildHeader(fmt,
				"loadgen_datetime"
				" exe_time_ms num_writes num_reads"
				" throughput(ios/sec)"
				" lat_w.avg lat_w._50 lat_w._99"
				" lat_r.avg lat_r._50 lat_r._99"
				" saturated(overloaded)"
				" num_cass_threads.min num_cass_threads.max"
				" cpu.user cpu.sys cpu.wait"

				" disk.xvda.read_kb disk.xvda.read_io"
				" disk.xvda.write_kb disk.xvda.write_io"
				" disk.xvda.rw_size disk.xvda.q_len disk.xvda.wait disk.xvda.svc_time disk.xvda.util"

				" disk.xvdb.read_kb disk.xvdb.read_io"
				" disk.xvdb.write_kb disk.xvdb.write_io"
				" disk.xvdb.rw_size disk.xvdb.q_len disk.xvdb.wait disk.xvdb.svc_time disk.xvdb.util"

				" disk.xvdd.read_kb disk.xvdd.read_io"
				" disk.xvdd.write_kb disk.xvdd.write_io"
				" disk.xvdd.rw_size disk.xvdd.q_len disk.xvdd.wait disk.xvdd.svc_time disk.xvdd.util"

				" net.kb_in net.kb_out"
				))

			for i in range(len(self.exps)):
				e = self.exps[i]
				lat_w = e.loadgen_log.lat_w
				lat_r = e.loadgen_log.lat_r

				# saturated flag
				#   0: not saturated
				#   1: last non-saturated one
				#   2: saturated
				if e.saturated == 0:
					if i < len(self.exps) - 1:
						if self.exps[i + 1].saturated == 1:
							saturated = 1
						else:
							saturated = 0
				elif e.saturated == 1:
					saturated = 2

				fo.write("%s\n" % (fmt % (
					e.log_dt_loadgen
					, e.loadgen_log.exe_time_ms, e.loadgen_log.num_writes, e.loadgen_log.num_reads
					, e.loadgen_log.Throughput()
					, lat_w.avg, lat_w._50, lat_w._99
					, lat_r.avg, lat_r._50, lat_r._99
					, saturated
					, e.num_cass_threads.min, e.num_cass_threads.max
					, e.collectl.GetAttrAvg("cpu_user"), e.collectl.GetAttrAvg("cpu_sys"), e.collectl.GetAttrAvg("cpu_wait")

					, e.collectl.GetAttrAvg("disk_xvda_read_kb"), e.collectl.GetAttrAvg("disk_xvda_read_io")
					, e.collectl.GetAttrAvg("disk_xvda_write_kb"), e.collectl.GetAttrAvg("disk_xvda_write_io")
					, e.collectl.GetAttrAvg("disk_xvda_rw_size"), e.collectl.GetAttrAvg("disk_xvda_q_len"), e.collectl.GetAttrAvg("disk_xvda_wait"), e.collectl.GetAttrAvg("disk_xvda_svc_time"), e.collectl.GetAttrAvg("disk_xvda_util")

					, e.collectl.GetAttrAvg("disk_xvdb_read_kb"), e.collectl.GetAttrAvg("disk_xvdb_read_io")
					, e.collectl.GetAttrAvg("disk_xvdb_write_kb"), e.collectl.GetAttrAvg("disk_xvdb_write_io")
					, e.collectl.GetAttrAvg("disk_xvdb_rw_size"), e.collectl.GetAttrAvg("disk_xvdb_q_len"), e.collectl.GetAttrAvg("disk_xvdb_wait"), e.collectl.GetAttrAvg("disk_xvdb_svc_time"), e.collectl.GetAttrAvg("disk_xvdb_util")

					, e.collectl.GetAttrAvg("disk_xvdd_read_kb"), e.collectl.GetAttrAvg("disk_xvdd_read_io")
					, e.collectl.GetAttrAvg("disk_xvdd_write_kb"), e.collectl.GetAttrAvg("disk_xvdd_write_io")
					, e.collectl.GetAttrAvg("disk_xvdd_rw_size"), e.collectl.GetAttrAvg("disk_xvdd_q_len"), e.collectl.GetAttrAvg("disk_xvdd_wait"), e.collectl.GetAttrAvg("disk_xvdd_svc_time"), e.collectl.GetAttrAvg("disk_xvdd_util")

					, e.collectl.GetAttrAvg("net_kb_in"), e.collectl.GetAttrAvg("net_kb_out")
					)))
		Cons.P("Created file %s %d" % (fn, os.path.getsize(fn)))

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
			self.collectl = CollectlLogReader.Read(self.log_dt_collectl, self.loadgen_log)

			# TODO: Cassndra log. What do you get from it?
			# - Hot and cold storage size, which you use to calculate cost. This is
			#   worth plotting.
			# - When tablets migrate.
			# - Number of requests to each tablet.

		def __str__(self):
			return " ".join("%s=%s" % item for item in vars(self).items())


class _LoadExpGroupReport():
	def __init__(self, fn):
		self.items = []
		with open(fn) as fo:
			for line in fo.readlines():
				#Cons.P(line.rstrip())
				if len(line) == 0:
					continue
				if line[0] == "#":
					continue
				t = line.split()
				if len(t) != 46:
					raise RuntimeError("Unexpected format [%s]" % line)
				self.items.append(_LoadExpGroupReport._Item(t))

	class _Item():
		def __init__(self, tokens):
			self.loadgen_datetime     = tokens[0]
			self.exe_time_ms          = tokens[1]
			self.num_writes           = tokens[2]
			self.num_reads            = tokens[3]
			self.throughput           = float(tokens[4])
			self.lat_w_avg            = float(tokens[5])
			self.lat_w__50            = tokens[6]
			self.lat_w__99            = float(tokens[7])
			self.lat_r_avg            = float(tokens[8])
			self.lat_r__50            = tokens[9]
			self.lat_r__99            = float(tokens[10])
			self.saturated            = tokens[11]
			self.num_cass_threads_min = tokens[12]
			self.num_cass_threads_max = tokens[13]
			self.cpu_user             = float(tokens[14])
			self.cpu_sys              = float(tokens[15])
			self.cpu_wait             = float(tokens[16])
			self.disk_xvda_read_kb    = float(tokens[17])
			self.disk_xvda_read_io    = float(tokens[18])
			self.disk_xvda_write_kb   = float(tokens[19])
			self.disk_xvda_write_io   = float(tokens[20])
			self.disk_xvda_rw_size    = float(tokens[21])
			self.disk_xvda_q_len      = float(tokens[22])
			self.disk_xvda_wait       = float(tokens[23])
			self.disk_xvda_svc_time   = float(tokens[24])
			self.disk_xvda_util       = float(tokens[25])
			self.disk_xvdb_read_kb    = float(tokens[26])
			self.disk_xvdb_read_io    = float(tokens[27])
			self.disk_xvdb_write_kb   = float(tokens[28])
			self.disk_xvdb_write_io   = float(tokens[29])
			self.disk_xvdb_rw_size    = float(tokens[30])
			self.disk_xvdb_q_len      = float(tokens[31])
			self.disk_xvdb_wait       = float(tokens[32])
			self.disk_xvdb_svc_time   = float(tokens[33])
			self.disk_xvdb_util       = float(tokens[34])
			self.disk_xvdd_read_kb    = float(tokens[35])
			self.disk_xvdd_read_io    = float(tokens[36])
			self.disk_xvdd_write_kb   = float(tokens[37])
			self.disk_xvdd_write_io   = float(tokens[38])
			self.disk_xvdd_rw_size    = float(tokens[39])
			self.disk_xvdd_q_len      = float(tokens[40])
			self.disk_xvdd_wait       = float(tokens[41])
			self.disk_xvdd_svc_time   = float(tokens[42])
			self.disk_xvdd_util       = float(tokens[43])
			self.net_kb_in            = float(tokens[44])
			self.net_kb_out           = float(tokens[45])
