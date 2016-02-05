import datetime
import re
import sys

sys.path.insert(0, "../util/python")
import Cons

import SimTime


class Event(object):
	def __init__(self):
		pass

	def __str__(self):
		return ("%s: " % type(self).__name__) + (", ".join("%s: %s" % item for item in vars(self).items()))


# A tmp table is created
class SstCreated(Event):
	def __init__(self, t):
		if "tmp-la-" not in t[8]:
			raise RuntimeError("A tmp table is expected: %s" % t[8])
		t1 = t[8].split("tmp-la-")
		#Cons.P(t1)
		self.sst_gen = int(t1[1].split("-")[0])


class SstDeleted(Event):
	def __init__(self, t):
		t1 = t[8].split("/la-")
		#Cons.P(t1)
		self.sst_gen = int(t1[1].split("-")[0])


class SstOpen(Event):
	# SSTableReader desc=/mnt/s5-cass-cold-storage/mtdb-cold/mtdb1/table1-89dd85a0cbba11e59f551d822de6a4f1/la-6-big openReason=NORMAL bytesOnDisk()=19547422 minTimestamp=160204-224305.652 maxTimestamp=160204-224324.694

	pattern_size = re.compile(r"bytesOnDisk\(\)=\d+")
	pattern_min_ts = re.compile(r"minTimestamp=\d\d\d\d\d\d-\d\d\d\d\d\d\.\d\d\d")
	pattern_max_ts = re.compile(r"maxTimestamp=\d\d\d\d\d\d-\d\d\d\d\d\d\.\d\d\d")

	def __init__(self, line):
		#Cons.P(line)
		t1 = line.split("/la-")
		self.sst_gen = int(t1[1].split("-")[0])
		#Cons.P(self.sst_gen)
		t2 = line.split(" openReason=")
		if len(t2) != 2:
			raise RuntimeError("Unexpected format: [%s]" % line)
		self.open_reason = t2[1].split(" ")[0]
		#Cons.P(self.open_reason)
		if self.open_reason == "NORMAL":
			mo = re.search(SstOpen.pattern_size, line)
			if mo != None:
				self.bytesOnDisk = int(line[mo.start():mo.end()].split("=")[1])
				#Cons.P(self.bytesOnDisk)
			mo = re.search(SstOpen.pattern_min_ts, line)
			if mo != None:
				self.min_ts = line[mo.start():mo.end()].split("=")[1]
				#Cons.P(self.min_ts)
			mo = re.search(SstOpen.pattern_max_ts, line)
			if mo != None:
				self.max_ts = line[mo.start():mo.end()].split("=")[1]
				#Cons.P(self.max_ts)


class TempMon(Event):
	class Started(object):
		def __init__(self):
			pass

	class Stopped(object):
		def __init__(self):
			pass

	class NumAccessesPerDay(object):
		def __init__(self):
			pass

	class BecomeCold(object):
		def __init__(self):
			pass

	pattern_start = re.compile(r" Start ")
	pattern_stop = re.compile(r" Stop ")
	pattern_num_accesses = re.compile(r" numAccessesPerDay=")
	pattern_num_accesses_sstgen = re.compile(r"SstTempMon-\d+-Thread-\d+")
	pattern_become_cold = re.compile(r" TabletBecomeCold ")
	pattern_become_cold_sstgen = re.compile(r"\d+")

	def __init__(self, line):
		mo = re.search(TempMon.pattern_start, line)
		if mo != None:
			self.sst_gen = int(line[mo.end():])
			self.event = TempMon.Started()
			return

		mo = re.search(TempMon.pattern_stop, line)
		if mo != None:
			self.sst_gen = int(line[mo.end():])
			self.event = TempMon.Stopped()
			return

		mo = re.search(TempMon.pattern_num_accesses, line)
		if mo != None:
			self.num_accesses_per_day = float(line[mo.end():])
			mo = re.search(TempMon.pattern_num_accesses_sstgen, line)
			if mo == None:
				raise RuntimeError("Unexpected [%s]" % line)
			#Cons.P(line[mo.start():])
			t = line[mo.start():].split("-")
			self.sst_gen = int(t[1])
			self.event = TempMon.NumAccessesPerDay()
			return

		mo = re.search(TempMon.pattern_become_cold, line)
		if mo != None:
			mo1 = re.search(TempMon.pattern_become_cold_sstgen, line[mo.end():])
			if mo1 == None:
				raise RuntimeError("Unexpected [%s]" % line)
			#Cons.P(line[mo.end():][mo1.start():mo1.end()])
			self.sst_gen = int(line[mo.end():][mo1.start():mo1.end()])
			self.event = TempMon.BecomeCold()
			return

		raise RuntimeError("Unexpected [%s]" % line)


class AccessStat(Event):
	class AccStat(object):
		def __init__(self):
			pass
		def __str__(self):
			return ("%s: " % type(self).__name__) + (", ".join("%s: %s" % item for item in vars(self).items()))

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
			self.num_reads = int(t1[0])
			self.num_needto_read_datafile = int(t1[1])
			# These numbers are not complete. They are not tracked when key cache is
			# present or the tracking is not enabled, which is a per-request option.
			self.num_tp = int(t1[2])
			self.num_fp = int(t1[3])

	# Memtable-table1@44994146(3.251MiB serialized bytes, 9768 ops, 15%/0% of on/off-heap limit)-17144,13881
	pattern0 = re.compile(r"( )?Memtable-table1@\d+\(\d*\.*\d*\w* serialized bytes, \d* ops, \d*%\/\d*% of on\/off-heap limit\)-\d+,\d+")

	#                           04:94839,8542,77,0
	#                           04: sst_gen:
	#                               94839 num_reads
	#                                  ,8542 num_need_to_read_dfiles
	#                                      ,77 num_bf_tp
	#                                          ,0 num_bf_fp
	pattern1 = re.compile(r"( )?\d+:\d+,\d+,\d+,\d+")

	def __init__(self, t):
		str0 = " ".join(t[8:])
		#Cons.P(str0)
		self.entries = []
		i = 0
		while True:
			mo = re.match(AccessStat.pattern0, str0[i:])
			if mo != None:
				#Cons.P("%s %d %d" % (mo.group(0), mo.start(), mo.end()))
				self.entries.append(AccessStat.MemtAccStat(mo.group(0)))
				#Cons.P(acc_stat)
				i += mo.end()
				continue
			mo = re.match(AccessStat.pattern1, str0[i:])
			if mo != None:
				#Cons.P("%s %d %d" % (mo.group(0), mo.start(), mo.end()))
				self.entries.append(AccessStat.SstAccStat(mo.group(0)))
				i += mo.end()
				continue
			break
