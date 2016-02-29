import os
import subprocess
import sys
import threading
import time

sys.path.insert(0, "../../util/python")
import Cons

import Conf


# Note: Redirecting output to memory file system may have a lower overhead. Not
# a big deal though.

class Mon:
	mon_interval = 0.1

	def __init__(self, test_name):
		self.test_name = test_name
		self.stop_requested = False
		self.stdout = []

	def __enter__(self):
		# Start monitoring CPU, Disk, Network
		cmd = "collectl -i %d -sCDN -oTm 2>/dev/null" % Mon.mon_interval
		self.subp = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		self.t = threading.Thread(target=self._CollectMonitorOutput)
		self.t.start()

		# collectl has an initial of the monitoring interval. Wait for a bit.
		time.sleep(Mon.mon_interval * 2)

		return self

	def _CollectMonitorOutput(self):
		while not self.stop_requested:
			line = self.subp.stdout.readline()
			self.stdout.append(line)
			#Cons.P(line.rstrip())
		self.subp.kill()
		self.subp.wait()
	
	def _Stop(self):
		if not self.stop_requested:
			self.stop_requested = True
			self.t.join()

	def __exit__(self, type, value, traceback):
		self._Stop()
		# TODO: first write to file and see what's happening. I'll have a better idea then
		self._WriteToFile()

	def _WriteToFile(self):
		fn = "data/%s-%s-collectl" % (Conf.ExpDatetime(), self.test_name)
		with open(fn, "w") as fo:
			for line in self.stdout:
				fo.write(line)
		Cons.P("Saved collectl log to %s %d" % (fn, os.path.getsize(fn)))

		# TODO: reduce size. trim logs during first and last mon_interval.
		# It can be done later

		# TODO: what I need is just avg, _99th percentile, min, max


def Test():
	with Mon() as srm:
		for i in range(2):
			time.sleep(1)
