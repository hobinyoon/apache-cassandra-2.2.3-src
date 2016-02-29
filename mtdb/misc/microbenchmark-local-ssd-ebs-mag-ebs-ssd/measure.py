#!/usr/bin/env python

import os
import re
import shutil
import sys

import Conf
import PlotData
import Plot
import SysResMon

sys.path.insert(0, "../../util/python")
import Cons
import Util


def Measure4kRandRead(storage_name, storage_dir, cnt):
	with Cons.MeasureTime(storage_name):
		fn_test = storage_dir + "/ioping-test"
		fn_out_ram = "%s/4k-rand-read-%s-%s" % (Conf.dn_output, storage_name, Conf.ExpDatetime())

		with SysResMon.Mon() as srm:
			cmd = "ioping -D -c %d -i 0 %s > %s" % (cnt, fn_test, fn_out_ram)
			#cmd = "ioping -D -c %d -i 0.001 %s > %s" % (cnt, fn_test, fn_out_ram)
			Util.RunSubp(cmd)

		fn_out_here = "data/4k-rand-read-%s-%s" % (storage_name, Conf.ExpDatetime())
		#Cons.P("[%s] [%s]" % (fn_out_ram, fn_out_here))
		shutil.move(fn_out_ram, fn_out_here)

		_ReduceIopingResultFileSize(fn_out_here)


def _ReduceIopingResultFileSize(fn):
	# Reduce
	#   4.0 KiB from /mnt/local-ssd/ioping-test (ext3 /dev/xvdb): request=23 time=166 us
	# to 
	#   166 us
	pattern = re.compile(r".+KiB from .+: request=.+ time=")

	size_before = os.path.getsize(fn)

	lines = []
	with open(fn) as fo:
		for line in fo.readlines():
			mo = pattern.match(line)
			if mo == None:
				lines.append(line)
			else:
				#Cons.P("[%s]" % line[mo.end():])
				lines.append(line[mo.end():])
	
	with open(fn, "w") as fo:
		for line in lines:
			fo.write(line)

	size_after = os.path.getsize(fn)

	Cons.P("File: %s" % fn)
	Cons.P("Reduced size from %d to %d" % (size_before, size_after))
	for line in lines[-2:]:
		Cons.P("%s" % line.strip())


# Implement when needed
#
#setup() {
#	sudo mkdir -p ${DN_OUTPUT}
#	sudo chown -R ubuntu ${DN_OUTPUT}
#
#	# Create test files
#	echo "Creating test files ..."
#	time dd bs=1024 count=262144 < /dev/urandom > $DN_LOCAL_SSD/ioping-test
#	time cp $DN_LOCAL_SSD/ioping-test $DN_EBS_SSD/ioping-test
#	time cp $DN_LOCAL_SSD/ioping-test $DN_EBS_MAG/ioping-test
#}


def main(argv):
	Measure4kRandRead("Local-SSD", "/mnt/local-ssd", 40000)
	#Measure4kRandRead("Local-SSD", "/mnt/local-ssd", 1000)

	sys.exit(0)

	# TODO
	#Conf.Init()
	#PlotData.Gen()
	#Plot.Plot()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
