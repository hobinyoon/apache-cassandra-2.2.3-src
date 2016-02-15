import os
import sys

sys.path.insert(0, "../../util/python")
import Cons

import Conf

def Load():
	_LoadLogs()
	sys.exit(0)
	_WritePlotData()


_cass = None
_mutants = None


class LogEntry(object):
# simulation_time_dur_ms     simulated_time         OpW_per_sec   running_behind_cnt    read_latency_ms  read_cnt
#         simulation_time         num_OpW_requested                  running_behind_avg_in_ms      write_cnt
#                                       percent_completed                         write_latency_ms
#                                                 running_on_time_cnt
#                                              running_on_time_sleep_avg_in_ms
#     1                 2                 3       4     5     6     7        8     9       10   11   12   13   14
#  1013 160209-165822.613 100117-105129.802     215   0.4   215     0        0   724     -130  131  168  215  293
#                         12345678901234567
	def __init__(self, tokens):
		self.simulation_time_dur_ms = int(tokens[0])
		self.simulation_time = tokens[1]
		self.simulated_time = tokens[2]
		self.write_latency_ms = int(tokens[10])
		self.read_latency_ms = int(tokens[11])

	def __str__(self):
		return " ".join("%s=%s" % item for item in vars(self).items())


class LoadgenLog(object):
	def __init__(self, exp_datetime):
		self.exp_datetime = exp_datetime
		self.fn_log = "../../logs/loadgen/%s" % self.exp_datetime
		self._LoadFile()

	def WritePlotData(self):
		fn = "plot-data/%s-latency-by-time" % self.exp_datetime
		with Cons.MeasureTime("Writing file %s ..." % fn):
			with open(fn, "w") as fo:
				fmt = "%17s %4d %4d"
				for e in _cass.entries:
					#Cons.P(fmt % (e.simulated_time, e.write_latency_ms, e.read_latency_ms))
					fo.write((fmt + "\n") % (e.simulated_time, e.write_latency_ms, e.read_latency_ms))
			Cons.P("Created %s %d" % (fn, os.path.getsize(fn)))

	# TODO: Keep all the latencies and generate a CDF
	def _LoadFile(self):
		self.entries = []
		#with Cons.MeasureTime("Loading file %s ..." % self.fn_log):
		with open(self.fn_log) as fo:
			parse_status = "header"
			for line in fo.readlines():
				if parse_status == "header":
					if len(line) == 0:
						continue
					t = line.split("simulated_time_years: ")
					if len(t) == 2:
						self.simulated_time_years = float(t[1])
					t = line.split("simulation_time_in_min: ")
					if len(t) == 2:
						self.simulattion_time_mins = float(t[1])

					t = line.split()
					detect_body_start = 0
					if len(t) > 5 and t[0] == "#":
						for i in range(1, 6):
							if t[i] == str(i):
								detect_body_start += 1
						if detect_body_start == 5:
							#Cons.P(line)
							parse_status = "body"
				elif parse_status == "body":
					t = line.split()
					if (len(t) > 0) and (t[0] == "#"):
						parse_status = "footer"
						continue
					#Cons.P(line)
					le = LogEntry(t)
					if le.simulation_time_dur_ms > (int(Conf.Get("simulation_time_exclude_first_secs")) * 1000):
						self.entries.append(le)
			#Cons.P("%s: Loaded %d log entries" % (self.exp_datetime, len(self.entries)))
			self._GenStat()

	def _GenStat(self):
		w_sum = 0
		r_sum = 0
		time_intervals = []
		time_prev = None
		first = True
		for e in self.entries:
			if first:
				w_min = e.write_latency_ms
				w_max = e.write_latency_ms
				r_min = e.read_latency_ms
				r_max = e.read_latency_ms
				first = False
			else:
				w_min = min(w_min, e.write_latency_ms)
				w_max = max(w_max, e.write_latency_ms)
				r_min = min(r_min, e.read_latency_ms)
				r_max = max(r_max, e.read_latency_ms)
				time_intervals.append(e.simulation_time_dur_ms - time_prev)
			w_sum += e.write_latency_ms
			r_sum += e.read_latency_ms
			time_prev = e.simulation_time_dur_ms
		self.w_avg = float(w_sum) / len(self.entries)
		self.r_avg = float(r_sum) / len(self.entries)
		self.w_min = w_min
		self.w_max = w_max
		self.r_min = r_min
		self.r_max = r_max
		#Cons.P("  w_avg=%f w_min=%d w_max=%d" % (self.w_avg, self.w_min, self.w_max))
		#Cons.P("  r_avg=%f r_min=%d r_max=%d" % (self.r_avg, self.r_min, self.r_max))
		self.time_intervals_avg_ms = sum(time_intervals) / float(len(time_intervals))
		#Cons.P("  avg time interval simulated time days=%f" % (self._ToSimulatedTimeSecs(self.time_intervals_avg_ms) / (24.0 * 3600)))

	def _ToSimulatedTimeSecs(self, simulation_time_ms):
		return simulation_time_ms / 1000.0 \
			* (self.simulated_time_years * 365.25 * 24 * 60) \
			/ self.simulattion_time_mins


def _GenStat(logs):
	read_lat_ms = []
	write_lat_ms = []
	for l in logs:
		for e in l.entries:
			write_lat_ms.append(e.write_latency_ms)
			read_lat_ms.append(e.read_latency_ms)
	w_avg = sum(write_lat_ms) / float(len(write_lat_ms))
	r_avg = sum(read_lat_ms) / float(len(read_lat_ms))
	Cons.P("w_avg=%f r_avg=%f" % (w_avg, r_avg))


def _FilterOutSlowestN(logs, ratio):
	num_exp_to_filter_out = int(len(logs) * ratio)
	Cons.P("Filtering out the slowest %d experiments" % num_exp_to_filter_out)
	#Cons.P("Before")
	#for l in logs:
	#	Cons.P("  %s r_max=%d" % (l.exp_datetime, l.r_max))
	logs.sort(key=lambda x: x.r_max)
	#Cons.P("After sorting")
	#for l in logs:
	#	Cons.P("  %s r_max=%d" % (l.exp_datetime, l.r_max))

	logs = logs[:-num_exp_to_filter_out]
	#Cons.P("After filtering out")
	#for l in logs:
	#	Cons.P("  %s r_max=%d" % (l.exp_datetime, l.r_max))
	return logs


def _LoadLogs():
	# TODO
	#global _cass, _mutants

	# Play around with this. On mt-s7, Mutants beats Cassandra with 0, 0.1, 0.2
	filter_out_slowest_n_ratio = 0.3

	_cass_logs = []
	with Cons.MeasureTime("Loading Cassandra loadgen log files ..."):
		for dt in Conf.Get("cassandra_experiment_datetime"):
			#Cons.P(dt)
			_cass_logs.append(LoadgenLog(dt))
		Cons.P("Loaded %d experiments" % len(_cass_logs))
		_cass_logs = _FilterOutSlowestN(_cass_logs, filter_out_slowest_n_ratio)
		#Cons.P(len(_cass_logs))
		_GenStat(_cass_logs)

	_mutants_logs = []
	with Cons.MeasureTime("Loading Mutants loadgen log files ..."):
		for dt in Conf.Get("mutants_experiment_datetime"):
			#Cons.P(dt)
			_mutants_logs.append(LoadgenLog(dt))
		Cons.P("Loaded %d experiments" % len(_mutants_logs))
		_FilterOutSlowestN(_mutants_logs, filter_out_slowest_n_ratio)
		#Cons.P(len(_cass_logs))
		_GenStat(_mutants_logs)


def _WritePlotData():
	global _cass, _mutants
	_cass.WritePlotData()
	_mutants.WritePlotData()
