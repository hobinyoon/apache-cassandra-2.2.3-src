import datetime
import os
import re
import sys

sys.path.insert(0, "../util/python")
import Cons

import SimTime

# _raw_lines0, 1, 2: lines before, in, after progress monitor
_raw_lines0 = []
_raw_lines1 = []
_raw_lines2 = []

_progresses = []

# If not specified, read the latest one
def Read():
	global _raw_lines0, _raw_lines1, _raw_lines2
	with Cons.MeasureTime("Reading Loadgen log ..."):
		dn = os.path.dirname(__file__) + "/../loadgen/logs"
		fn = _GetYoungestFn(dn)
		Cons.P("fn=%s" % fn)
		with open(fn) as fo:
			parse_log_status = "before_monitor"
			for line in fo.readlines():
				line = line.strip()
				if parse_log_status == "before_monitor":
					_raw_lines0.append(line)
					t = line.split()
					if len(t) < 6:
						continue
					detect_header = 0
					if t[0] == "#":
						for i in range(1, 6):
							if t[i] == str(i):
								detect_header += 1
					if detect_header == 5:
						parse_log_status = "in_monitor"
				elif parse_log_status == "in_monitor":
					t = line.split()
					if len(t) < 1:
						continue
					if t[0] == "#":
						parse_log_status = "after_monitor"
						continue
					_raw_lines1.append(line)
				else:
					_raw_lines2.append(line)
					#print parse_log_status
					pass
		#for line in _raw_lines1:
		#	print line

		_ParseProgMonLines()

	SimTime.Init(_progresses[0].simulation_time_dur_ms
			, _progresses[0].simulation_time , _progresses[0].simulated_time
			, _progresses[-1].simulation_time , _progresses[-1].simulated_time)


class ProgressEntry(object):
	# simulation_time_dur_ms     simulated_time         OpW_per_sec   running_behind_cnt    read_latency_ms  read_cnt
	#         simulation_time         num_OpW_requested                  running_behind_avg_in_ms      write_cnt
	#                                       percent_completed                         write_latency_ms
	#                                                 running_on_time_cnt
	#                                              running_on_time_sleep_avg_in_ms
	#     1                 2                 3       4     5     6     7        8     9       10   11   12   13   14
	# 57386 160119-135559.241 150207-032415.942   31428  62.9   756     0        0  4410     -679   90  107  756 3654
	def __init__(self, line):
		#Cons.P(line)
		t = line.split()
		if len(t) != 14:
			raise RuntimeError("Unexpected format [%s]" % line)
		self.simulation_time_dur_ms          = long(t[0])
		self.simulation_time                 = datetime.datetime.strptime(t[1], "%y%m%d-%H%M%S.%f")
		self.simulated_time                  = datetime.datetime.strptime(t[2], "%y%m%d-%H%M%S.%f")
		self.num_OpW_requested               = long(t[3])
		self.percent_completed               = float(t[4])
		self.OpW_per_sec                     = int(t[5])
		self.running_on_time_cnt             = int(t[6])
		self.running_on_time_sleep_avg_in_ms = int(t[7])
		self.running_behind_cnt              = int(t[8])
		self.running_behind_avg_in_ms        = int(t[9])
		self.write_latency_ms                = int(t[10])
		self.read_latency_ms                 = int(t[11])
		self.write_cnt                       = int(t[12])
		self.read_cnt                        = int(t[13])



def _ParseProgMonLines():
	global _raw_lines1
	for line in _raw_lines1:
		_progresses.append(ProgressEntry(line))


def _GetYoungestFn(dn):
	pattern = re.compile(r"\d\d\d\d\d\d-\d\d\d\d\d\d.*")
	fns = []
	for fn in os.listdir(dn):
		#print "[%s] [%s]" % (fn, pattern.match(fn))
		if pattern.match(fn) != None:
			fns.append(fn)
	if len(fns) == 0:
		raise RuntimeError("No log file in %s" % dn)
	fns.sort()
	return dn + "/" + fns[-1]
