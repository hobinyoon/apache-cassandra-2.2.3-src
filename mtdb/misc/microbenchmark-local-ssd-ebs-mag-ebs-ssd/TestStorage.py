import os
import re
import shutil
import sys

import Conf
import SysResMon

sys.path.insert(0, "../../util/python")
import Cons
import Util


def Test():
	_Setup()
	_Measure4kRandRead("Local-SSD", "/mnt/local-ssd", 40000)


def _Setup():
	if not os.path.isdir("data"):
		with Cons.MeasureTime("Creating dir data ..."):
			Util.MkDirs("data")

	if not os.path.isdir(Conf.dn_output):
		with Cons.MeasureTime("Creating dir %s ..." % Conf.dn_output):
			cmd = "sudo mkdir -p %s && sudo chown -R ubuntu %s" \
					% (Conf.dn_output, Conf.dn_output)
			Util.RunSubp(cmd)

	fn_ioping_local_ssd = "%s/ioping-test" % Conf.dn_local_ssd
	if not os.path.isfile(fn_ioping_local_ssd):
		with Cons.MeasureTime("Creating file %s ..." % fn_ioping_local_ssd):
			cmd = "time dd bs=1024 count=262144 < /dev/urandom > %s" % fn_ioping_local_ssd
			Util.RunSubp(cmd)

	fn_ioping_ebs_ssd = "%s/ioping-test" % Conf.dn_ebs_ssd
	if not os.path.isfile(fn_ioping_ebs_ssd):
		with Cons.MeasureTime("Creating file %s ..." % fn_ioping_ebs_ssd):
			cmd = "cp %s %s" % (fn_ioping_local_ssd, fn_ioping_ebs_ssd)
			Util.RunSubp(cmd)

	fn_ioping_ebs_mag = "%s/ioping-test" % Conf.dn_ebs_mag
	if not os.path.isfile(fn_ioping_ebs_mag):
		with Cons.MeasureTime("Creating file %s ..." % fn_ioping_ebs_mag):
			cmd = "cp %s %s" % (fn_ioping_local_ssd, fn_ioping_ebs_mag)
			Util.RunSubp(cmd)


def _Measure4kRandRead(storage_name, storage_dir, cnt):
	with Cons.MeasureTime(storage_name):
		fn_test = storage_dir + "/ioping-test"
		test_name = "4k-rand-read-%s" % storage_name
		fn_out_ram = "%s/%s-%s" % (Conf.dn_output, test_name, Conf.ExpDatetime())

		with SysResMon.Mon(test_name) as srm:
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

	Cons.P("  File: %s" % fn)
	Cons.P("  Reduced size from %d to %d" % (size_before, size_after))
	for line in lines[-2:]:
		Cons.P("  %s" % line.strip())
