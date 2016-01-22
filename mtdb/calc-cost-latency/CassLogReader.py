import datetime
import os
import re
import sys
import zipfile

sys.path.insert(0, "../util/python")
import Cons
import Util

import Conf
import LoadgenLogReader
import SimTime
import StgCost

_raw_lines = []
_logs = []

_report_interval_ms = None

# TODO: may want to separate to a different file. This is data for storage-size-by-time plot
_fn_plot_data = None


def Read():
	with Cons.MeasureTime("Reading Cassandra system log ..."):
		if not _ReadStoredCassMtdbLog():
			_ReadCassMtdbLog()
		# Parse raw lines
		global _raw_lines, _logs
		for line in _raw_lines:
			_logs.append(LogEntry(line))


def _ReadStoredCassMtdbLog():
	# If there is a stored Cassandra MTDB log file, read the raw lines
	fn = _StoredCassMtdbLogFilename()
	if not os.path.isfile(fn):
		return False

	Cons.P("Reading the stored Cassandra MTDB log file %s" % fn)
	global _raw_lines
	with open(fn) as fo:
		for line in fo.readlines():
			_raw_lines.append(line.strip())
	return True


def _StoredCassMtdbLogFilename():
	dn = os.path.dirname(__file__) + "/../logs/cassandra"
	return dn + "/" + LoadgenLogReader.LogFilename()


def _ReadCassMtdbLog():
	lines = []
	found_clear_acc_stat = False
	lines1 = []
	fn = os.path.expanduser("~") + "/work/cassandra/logs/system.log"
	Cons.P("fn=%s" % fn)
	with open(fn) as fo:
		for line in fo.readlines():
			#print line
			if "MTDB: ClearAccStat" in line:
				#print line
				found_clear_acc_stat = True
				del lines[:]
			if "MTDB:" in line:
				lines.append(line.strip())

	# Look at system.log.1.zip when "MTDB: ClearAccStat" is not found
	if found_clear_acc_stat == False:
		fn = os.path.expanduser("~") + "/work/cassandra/logs/system.log.1.zip"
		Cons.P("MTDB: ClearAccStat not found. Reading more from file %s ..." % fn)
		with zipfile.ZipFile(fn, "r") as z:
			for fn1 in z.namelist():
				#Cons.P(fn1)
				for line in z.read(fn1).split("\n"):
					#Cons.P(line)
					if "MTDB: ClearAccStat" in line:
						#print line
						found_clear_acc_stat = True
						del lines1[:]
					if "MTDB:" in line:
						lines1.append(line.strip())

	if found_clear_acc_stat == False:
		raise RuntimeError("Incomplete Cassandra log. No MTDB: ClearAccStat in either of system.log or system.log.1.zip")

	if len(lines1) != 0:
		lines1.extend(lines)
		lines = lines1
	#for line in lines:
	#	print line
	global _raw_lines
	_raw_lines = lines

	_WriteToFile()


def _WriteToFile():
	fn = _StoredCassMtdbLogFilename()
	Cons.P("Writing Cassandra MTDB log to file %s" % fn)
	with open(fn, "w") as fo:
		for line in _raw_lines:
			fo.write(line)
			fo.write("\n")


class Event(object):
	def __init__(self):
		pass

	def __str__(self):
		return ", ".join("%s: %s" % item for item in vars(self).items())

class EventSstCreated(Event):
	def __init__(self, t):
		if "tmp-la-" not in t[8]:
			raise RuntimeError("A tmp table is expected: %s" % t[8])
		t1 = t[8].split("tmp-la-")
		#Cons.P(t1)
		self.sst_gen = int(t1[1].split("-")[0])

	def __str__(self):
		return "EventSstCreated: " + ", ".join("%s: %s" % item for item in vars(self).items())

class EventSstDeleted(Event):
	def __init__(self, t):
		t1 = t[8].split("/la-")
		#Cons.P(t1)
		self.sst_gen = int(t1[1].split("-")[0])

	def __str__(self):
		return "EventSstDeleted: " + ", ".join("%s: %s" % item for item in vars(self).items())

class EventAccessStat(Event):
	class AccStat(object):
		def __init__(self):
			pass
		def __str__(self):
			return ", ".join("%s: %s" % item for item in vars(self).items())

	class MemtAccStat(AccStat):
		def __init__(self, str0):
			# Memtable-table1@1481193123(271.975KiB serialized bytes, 798 ops, 1%/0% of on/off-heap limit)-1287,386
			if str0.startswith(" "):
				str0 = str0[1:]
			if str0.startswith("Memtable-table1@") == False:
				#                 0123456789012345
				raise RuntimeError("Unexpected: [%s]" % str0)
			str0 = str0[16:]
			t = str0.split("(")
			self.id_ = int(t[0])
			#Cons.P(self.id_)
			t1 = t[1].split()
			# In 110.426KiB
			self.size = t1[0]
			#Cons.P(self.size)
			#Cons.P(t[1])
			t2 = t[1].split("-")
			#Cons.P(t2)
			t3 = t2[2].split(",")
			self.num_accesses = int(t3[0])
			self.num_hits = int(t3[1])
			#Cons.P("%d %d" % (num_accesses, num_hits))

		def __str__(self):
			return "MemtAccStat: " + super(EventAccessStat.MemtAccStat, self).__str__()

	class SstAccStat(AccStat):
		def __init__(self, str0):
			#Cons.P(str0)
			# 09:55428930,258068,258068,0
			if str0.startswith(" "):
				str0 = str0[1:]
			t = str0.split(":")
			# We use sstable gen as id_
			self.id_ = int(t[0])
			t1 = t[1].split(",")
			#Cons.P(t1)
			self.size = int(t1[0])
			self.num_reads = int(t1[1])
			self.num_tp = int(t1[2])
			self.num_fp = int(t1[3])

		def __str__(self):
			return "SstAccStat: " + super(EventAccessStat.SstAccStat, self).__str__()

	# Memtable-table1@44994146(3.251MiB serialized bytes, 9768 ops, 15%/0% of on/off-heap limit)-17144,13881
	pattern0 = re.compile(r"( )?Memtable-table1@\d+\(\d*\.*\d*\w* serialized bytes, \d* ops, \d*%\/\d*% of on\/off-heap limit\)-\d+,\d+")
	# 09:55428930,251201,251201,0
	pattern1 = re.compile(r"( )?\d+:\d+,\d+,\d+,\d+")

	def __init__(self, t):
		str0 = " ".join(t[8:])
		#Cons.P(str0)
		self.entries = []
		i = 0
		while True:
			mo = re.match(EventAccessStat.pattern0, str0[i:])
			if mo != None:
				#Cons.P("%s %d %d" % (mo.group(0), mo.start(), mo.end()))
				self.entries.append(EventAccessStat.MemtAccStat(mo.group(0)))
				#Cons.P(acc_stat)
				i += mo.end()
				continue
			mo = re.match(EventAccessStat.pattern1, str0[i:])
			if mo != None:
				#Cons.P("%s %d %d" % (mo.group(0), mo.start(), mo.end()))
				self.entries.append(EventAccessStat.SstAccStat(mo.group(0)))
				i += mo.end()
				continue
			break

	def __str__(self):
		return "EventAccessStat: " + ", ".join("%s: %s" % item for item in vars(self).items())


class LogEntry(object):
	#    0       1          2            3                        4 5     6            7
	# WARN  [main] 2016-01-18 23:10:30,728 CassandraDaemon.java:490 - MTDB: CassActivate
	def __init__(self, line):
		#Cons.P(line)
		t = line.split()
		self.simulation_time = datetime.datetime.strptime("%s %s" % (t[2], t[3]), "%Y-%m-%d %H:%M:%S,%f")
		self.op = t[7]
		self.simulated_time = SimTime.SimulatedTime(self.simulation_time)
		#Cons.P("%s %s" % (self.simulated_time, self.op))

		if self.op == "SstCreated":
			self.event = EventSstCreated(t)
		elif self.op == "SstDeleted":
			self.event = EventSstDeleted(t)
		elif self.op == "report_interval_ms":
			global _report_interval_ms
			_report_interval_ms = int(t[8])
		elif self.op == "TabletAccessStat":
			self.event = EventAccessStat(t)
		else:
			#Cons.P(t[7:])
			pass

	def __str__(self):
		return ", ".join("%s: %s" % item for item in vars(self).items())


# Keeps the last cost calc time of SSTables. Memtable cost is already
# included in the EC2 instance cost.
class SstLastCostCalcTime(object):
	id_time = {}

	@staticmethod
	def Set(sst_gen, simulated_time):
		SstLastCostCalcTime.id_time[sst_gen] = simulated_time

	@staticmethod
	def Get(sst_gen):
		r = SstLastCostCalcTime.id_time.get(sst_gen)
		if r == None:
			raise RuntimeError("No last cost calc time for SSTable %d" % sst_gen)
		return r


def GenStorageSizePlotData():
	global _logs
	with Cons.MeasureTime("Generating storage size plot data ..."):
		global _fn_plot_data
		_fn_plot_data = os.path.dirname(__file__) + "/plot-data/" + LoadgenLogReader.LogFilename() + "-storage-size-by-time"
		with open(_fn_plot_data, "w") as fo:
			fmt = "%20s %20s %20s %20s %10d %8f"
			fo.write("%s\n" % Util.BuildHeader(fmt,
					"simulation_time_end simulated_time_begin simulated_time_end simulated_time_mid stg_size_bytes cost_in_the_simulated_time_segment"))
			total_cost = 0.0
			last_cost_print_time = SimTime._simulated_time_begin
			for l in _logs:
				if l.op == "TabletAccessStat":
					cost = 0.0
					stg_size = 0
					for e in l.event.entries:
						if type(e) is EventAccessStat.SstAccStat:
							stg_size += e.size
							# Find the last logging time of the same sstable and calculate cost.
							c = StgCost.InstStore(e.size, l.simulated_time - SstLastCostCalcTime.Get(e.id_))
							cost += c
							SstLastCostCalcTime.Set(e.id_, l.simulated_time)

					if l.simulated_time != last_cost_print_time:
						fo.write((fmt + "\n") %
								(l.simulation_time.strftime("%y%m%d-%H%M%S.%f")
									, last_cost_print_time.strftime("%y%m%d-%H%M%S.%f")
									, l.simulated_time.strftime("%y%m%d-%H%M%S.%f")
									, (last_cost_print_time + datetime.timedelta(seconds = (l.simulated_time - last_cost_print_time).total_seconds() * 0.5)).strftime("%y%m%d-%H%M%S.%f")
									, stg_size
									, cost))
					last_cost_print_time = l.simulated_time

					total_cost += cost
				elif l.op == "SstCreated":
					SstLastCostCalcTime.Set(l.event.sst_gen, l.simulated_time)
			msg = "total cost ($): %f" % total_cost
			fo.write("# %s\n" % msg)
			Cons.P(msg)
		Cons.P("Created file %s %d" % (_fn_plot_data, os.path.getsize(_fn_plot_data)))
