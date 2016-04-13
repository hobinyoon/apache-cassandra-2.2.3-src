import os
import sys

sys.path.insert(0, "../../util/python")
import Cons
import Util


def Read(log_datetime):
	return Log(log_datetime)


class Log:
	def __init__(self, log_datetime):
		self.log_datetime = log_datetime
		self._GetStorageSizeCost()

	def _GetStorageSizeCost(self):
		# Note: What other info might be worth it from the Cassndra log file?
		# - When tablets migrate.
		# - Number of requests to each tablet.

		# Get hot and cold storage size
		fn = "%s/work/cassandra/mtdb/process-log/calc-cost-latency-plot-tablet-timeline/plot-data/%s-storage-size-by-time" \
				% (os.path.expanduser("~"), self.log_datetime)
		# Generate one, if it doesn't exist
		if not os.path.isfile(fn):
			cmd = "%s/work/cassandra/mtdb/process-log/calc-cost-latency-plot-tablet-timeline/plot-cost-latency-tablet-timelines.py %s" \
					% (os.path.expanduser("~"), self.log_datetime)
			Util.RunSubp(cmd)

		with open(fn) as fo:
			lines = []
			for line in fo.readlines():
				#Cons.P(line)
				line = line.rstrip()
				lines.append(line)
			lines = lines[-5:]
			t = lines[0].split()
			if len(t) != 6:
				raise RuntimeError("Unexpected format [%s]" % lines[0])

			# The storage size for the cold and the hot at the end of the
			# simulation.  The total size will be used to calculate the
			# fill-up-1.6TB-disks cost.
			self.hot_stg_usage  = float(t[1])
			self.cold_stg_usage = float(t[2])

			# Cumulative cost for the entire the simulation period
			self.hot_stg_cost   = float(t[3])
			self.cold_stg_cost  = float(t[4])

			#Cons.P(self.hot_stg_usage)
			#Cons.P(self.cold_stg_usage)
			#Cons.P(self.hot_stg_cost)
			#Cons.P(self.cold_stg_cost)

			# Some of the last simulated times are longer than 8 years because the
			# system was saturated.  Logs from unsaturated systems says 8 years.
			# For instance,
			# ~/work/apache-cassandra-2.2.3-src/mtdb/process-log/calc-cost-latency-plot-tablet-timeline/plot-data/160302-151257-storage-size-by-time

	def __str__(self):
		return " ".join("%s=%s" % item for item in vars(self).items())
