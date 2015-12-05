#!/usr/bin/env python

import os
import string
import sys
import datetime

sys.path.insert(0, "../..")
import Util

_fn_in = None
_fn_out = None
_simulated_time_in_year = None

class ReadCnt:
	def __init__(self, r, fp, tp):
		self.reads = r
		self.bf_fp = fp
		self.bf_tp = tp
		self.bf_n = r - fp - tp

	def __str__(self):
		return "%8d %4d %7d %8d" % (self.reads, self.bf_fp, self.bf_tp, self.bf_n)

	def __sub__(self, r):
		return ReadCnt(
				self.reads - r.reads,
				self.bf_fp - r.bf_fp,
				self.bf_tp - r.bf_tp)

# In string and in datetime
_simulation_time_begin_str = None
_simulation_time_end_str = None
_simulation_time_begin = None
_simulation_time_end = None
_simulation_time_dur = None

# In datetime
_simulated_time_begin = None
_simulated_time_dur = None

def InitSimTime():
	global _simulation_time_begin
	global _simulation_time_end
	global _simulation_time_dur
	_simulation_time_begin = datetime.datetime.strptime(_simulation_time_begin_str, "%Y-%m-%d-%H:%M:%S.%f")
	_simulation_time_end = datetime.datetime.strptime(_simulation_time_end_str, "%Y-%m-%d-%H:%M:%S.%f")
	# _simulation_time_dur.total_seconds() has microsecond resolution!
	_simulation_time_dur = _simulation_time_end - _simulation_time_begin

	print "simulation_time:"
	print "  begin: %s" % _simulation_time_begin
	print "  end  : %s" % _simulation_time_end
	print "  dur  : %f secs" % _simulation_time_dur.total_seconds()

	# _simulation_time_dur / _simulated_time_dur
	# = dur_since_simulation_time_begin / dur_since_simulated_time_begin
	#
	# target_simulated_time = _simulated_time_begin + dur_since_simulated_time_begin

	global _simulated_time_begin
	global _simulated_time_dur
	_simulated_time_begin = datetime.datetime.strptime("2007-01-01-00:00:00.000", "%Y-%m-%d-%H:%M:%S.%f")
	_simulated_time_dur = datetime.timedelta(seconds=(_simulated_time_in_year * 365.25 * 24 * 3600))

	print "simulated_time:"
	print "  begin: %s" % _simulated_time_begin
	print "  end  : %s" % (_simulated_time_begin + _simulated_time_dur)
	print "  dur  : %s" % _simulated_time_dur

	# target_simulated_time = _simulated_time_begin \
	# 		+ (_simulated_time_dur * dur_since_simulation_time_begin / _simulation_time_dur)


def SimulatedTime(simulation_time_str):
	global _simulation_time_dur
	global _simulated_time_begin
	global _simulated_time_dur

	simulation_time = datetime.datetime.strptime(simulation_time_str, "%Y-%m-%d-%H:%M:%S.%f")
	dur_since_simulation_time_begin = simulation_time - _simulation_time_begin

	target_simulated_time = _simulated_time_begin \
			+ datetime.timedelta(seconds=(_simulated_time_dur.total_seconds() \
			* dur_since_simulation_time_begin.total_seconds() \
			/ _simulation_time_dur.total_seconds()))

	return target_simulated_time


def ReadInputAndGenFormattedFile():
	global _simulation_time_begin_str
	global _simulation_time_end_str

	sstgen_time_cnt = {}

	global _fn_in
	with open(_fn_in) as fo:
		for line in fo.readlines():
			# print line
			if len(line) == 0:
				continue
			if line[0] == "#":
				continue

			time = None
			event_type = None
			t = line.split()
			#print len(t)
			for i in range(len(t)):
				if i == 0:
					time = t[i]
					continue
				elif i == 1:
					# replace decimal point , with .
					time += ("-" + string.replace(t[i], ",", "."))
					if _simulation_time_begin_str == None:
						_simulation_time_begin_str = time
					else:
						_simulation_time_begin_str = min(_simulation_time_begin_str, time)
					if _simulation_time_end_str == None:
						_simulation_time_end_str = time
					else:
						_simulation_time_end_str = max(_simulation_time_end_str, time)
					continue
				elif i == 2:
					event_type = t[i]
					continue

				if event_type != "SstAccess":
					break

				t2 = t[i].split(":")
				if len(t2) != 2:
					raise RuntimeError("Unexpected format: [%s] [%s]" % (line, t2))
				sstable_gen = int(t2[0][3:])
				t3 = t2[1].split(",")
				if len(t3) != 3:
					raise RuntimeError("Unexpected format: [%s] [%s]" % (line, t2))
				read_cnt = int(t3[0])
				bf_fp_cnt = int(t3[1])
				bf_tp_cnt = int(t3[2])

				if sstable_gen not in sstgen_time_cnt:
					sstgen_time_cnt[sstable_gen] = {}

				sstgen_time_cnt[sstable_gen][time] = ReadCnt(read_cnt, bf_fp_cnt, bf_tp_cnt)

	InitSimTime()

	with open(_fn_out, "w") as fo:
		fmt = "%2d %26s %8d %4d %7d %8d"
		fo.write(Util.BuildHeader(fmt, "sstable_gen time read_cnt bf_fp_cnt bf_tp_cnt bf_n_cnt"))

		for k, v in sorted(sstgen_time_cnt.iteritems()):
			v2_prev = None
			v2_inc = None
			for k2, v2 in sorted(v.iteritems()):
				if v2_prev == None:
					v2_inc = v2
				else:
					v2_inc = v2 - v2_prev
				v2_prev = v2
				#fo.write("%2d %s %s\n" % (k, k2, v2_inc))
				fo.write("%2d %s %s\n" % (k, SimulatedTime(k2).strftime("%Y-%m-%d-%H:%M:%S.%f"), v2_inc))
			fo.write("\n")
	print "Created file %s %d" % (_fn_out, os.path.getsize(_fn_out))


def main(argv):
	if len(argv) != 3:
		print "Usage: %s fn_in simulated_time_in_year" % (argv[0])
		sys.exit(1)

	global _fn_in
	global _fn_out
	global _simulated_time_in_year
	_fn_in = argv[1]
	_fn_out = _fn_in + "-by-sstables-by-time"
	_simulated_time_in_year = float(argv[2])

	ReadInputAndGenFormattedFile()


if __name__ == "__main__":
  sys.exit(main(sys.argv))
