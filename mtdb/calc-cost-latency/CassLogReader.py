import datetime
import os
import re
import sys
import zipfile

sys.path.insert(0, "../util/python")
import Cons

import Desc
import Event
import SimTime

_raw_lines = []
_logs = []


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
	return dn + "/" + Desc.ExpDatetime()


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

	# Keep reading zipped files like system.log.1.zip, until "MTDB: ClearAccStat"
	# is found
	i = 1
	while found_clear_acc_stat == False:
		fn = os.path.expanduser("~") + ("/work/cassandra/logs/system.log.%d.zip" % i)
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
		if len(lines1) != 0:
			lines1.extend(lines)
			lines = list(lines1)
			del lines1[:]
		i += 1

	#for line in lines:
	#	print line
	global _raw_lines
	_raw_lines = lines

	_WriteToFile()


def _WriteToFile():
	fn = _StoredCassMtdbLogFilename()
	with open(fn, "w") as fo:
		for line in _raw_lines:
			fo.write(line)
			fo.write("\n")
	Cons.P("Created a Cassandra MTDB log file %s %d" % (fn, os.path.getsize(fn)))


class LogEntry(object):
	pattern0 = re.compile(r"SSTableReader desc=.+/la-\d+-big openReason=.+")

	#    0       1          2            3                        4 5     6            7
	# WARN  [main] 2016-01-18 23:10:30,728 CassandraDaemon.java:490 - MTDB: CassActivate
	def __init__(self, line):
		#Cons.P(line)
		t = line.split()
		self.simulation_time = datetime.datetime.strptime("%s %s" % (t[2], t[3]), "%Y-%m-%d %H:%M:%S,%f")
		self.simulated_time = SimTime.SimulatedTime(self.simulation_time)
		#Cons.P("%s %s" % (self.simulated_time, self.op))
		self.op = t[7]
		line_from_op = " ".join(t[7:])

		# TODO: add more events, like temperature monitor started, ...

		self.event = None
		if self.op == "SstCreated":
			self.event = Event.SstCreated(t)
		elif self.op == "SstDeleted":
			self.event = Event.SstDeleted(t)
		elif self.op == "TabletAccessStat":
			self.event = Event.AccessStat(t)
		elif line_from_op.startswith("Node configuration:"):
			Desc.SetNodeConfiguration(line_from_op)
		elif self.op.startswith("metadata="):
			Desc.SetCassMetadata(line)
		elif self.op == "SSTableReader":
			mo = re.match(LogEntry.pattern0, line_from_op)
			if mo == None:
				raise RuntimeError("Unexpected: [%s]" % line_from_op)
			#Cons.P(mo.group(0))
			self.event = Event.SstOpen(line_from_op)
		else:
			#Cons.P(t[7:])
			pass

	def __str__(self):
		return ", ".join("%s: %s" % item for item in vars(self).items())
