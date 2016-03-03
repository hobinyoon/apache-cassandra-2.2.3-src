import sys

sys.path.insert(0, "../../util/python")
import Cons


def Read(log_datetime):
	fn = "../../logs/num-cass-threads/%s" % log_datetime
	return Log(fn)


class Log:
	def __init__(self, fn):
		self.dt_num_threads = {}
		#self.avg = None
		self.min = None
		self.max = None
		#self._50 = None
		#self._99 = None
		self._Read(fn)
		self._CalcStatMinMax()
	
	def _Read(self, fn):
		with open(fn) as fo:
			for line in fo.readlines():
				#Cons.P(line)
				t = line.split()
				if len(t) != 2:
					continue
				self.dt_num_threads[t[0]] = int(t[1])

	def _CalcStatMinMax(self):
		for dt, num_t in self.dt_num_threads.iteritems():
			if self.min == None:
				self.min = num_t
			else:
				self.min = min(self.min, num_t)

			if self.max == None:
				self.max = num_t
			else:
				self.max = max(self.max, num_t)

	# need to know loadgen start and end time to scope the experiment time range.
	# Not a big deal. Just check min and max.
	def _CalcStat(self):
		sum = 0
		num_threads = []

		for dt, num_t in self.dt_num_threads.iteritems():
			sum += num_t
			num_threads.append(num_t)

			if self.min == None:
				self.min = num_t
			else:
				self.min = min(self.min, num_t)

			if self.max == None:
				self.max = num_t
			else:
				self.max = max(self.max, num_t)

		self.avg = float(sum) / len(self.dt_num_threads)
		num_threads.sort()
		self._50 = num_threads[int(len(num_threads) * 0.5 ) - 1]
		self._99 = num_threads[int(len(num_threads) * 0.99) - 1]
