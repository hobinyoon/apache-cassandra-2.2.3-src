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
	_Measure4kRandRead("Local-SSD", "/mnt/local-ssd")


def _Setup():
	if not os.path.isdir("data"):
		with Cons.MeasureTime("Creating dir data ..."):
			Util.MkDirs("data")

	if not os.path.isdir(Conf.Get("dn_output")):
		with Cons.MeasureTime("Creating dir %s ..." % Conf.dn_output):
			cmd = "sudo mkdir -p %s && sudo chown -R ubuntu %s" \
					% (Conf.dn_output, Conf.dn_output)
			Util.RunSubp(cmd)

	fn_ioping_local_ssd = "%s/ioping-test" % Conf.Get("dn_local_ssd")
	if not os.path.isfile(fn_ioping_local_ssd):
		with Cons.MeasureTime("Creating file %s ..." % fn_ioping_local_ssd):
			cmd = "time dd bs=1024 count=262144 < /dev/urandom > %s" % fn_ioping_local_ssd
			Util.RunSubp(cmd)

	fn_ioping_ebs_ssd = "%s/ioping-test" % Conf.Get("dn_ebs_ssd")
	if not os.path.isfile(fn_ioping_ebs_ssd):
		with Cons.MeasureTime("Creating file %s ..." % fn_ioping_ebs_ssd):
			cmd = "cp %s %s" % (fn_ioping_local_ssd, fn_ioping_ebs_ssd)
			Util.RunSubp(cmd)

	fn_ioping_ebs_mag = "%s/ioping-test" % Conf.Get("dn_ebs_mag")
	if not os.path.isfile(fn_ioping_ebs_mag):
		with Cons.MeasureTime("Creating file %s ..." % fn_ioping_ebs_mag):
			cmd = "cp %s %s" % (fn_ioping_local_ssd, fn_ioping_ebs_mag)
			Util.RunSubp(cmd)


# TODO: won't be able to generalize this function with reuse_4k_rand_read_Local_SSD_exp
def _Measure4kRandRead(storage_name, storage_dir):
	with Cons.MeasureTime(storage_name):
		test_name = "4k-rand-read-%s" % storage_name
		fn_out = None
		if Conf.Get("reuse_4k_rand_read_Local_SSD_exp") == None:
			fn_test = storage_dir + "/ioping-test"
			fn_out_ram = "%s/%s-%s" % (Conf.Get("dn_output"), Conf.ExpDatetime(), test_name)

			ioping_cmd = "ioping -D -c %d -i 0 %s > %s" % (Conf.Get("4k_rand_read_cnt"), fn_test, fn_out_ram)
			with SysResMon.Mon(test_name) as srm:
				# TODO: Configure the interval? Parallel request?
				Util.RunSubp(ioping_cmd)

			fn_out = "data/%s-4k-rand-read-%s" % (Conf.ExpDatetime(), storage_name)
			#Cons.P("[%s] [%s]" % (fn_out_ram, fn_out))
			shutil.move(fn_out_ram, fn_out)
			_ReduceIopingResultFileSize(fn_out, ioping_cmd)
		else:
			Cons.P("Using stored experiment %s" % Conf.Get("reuse_4k_rand_read_Local_SSD_exp"))
			SysResMon.PrintReport(Conf.Get("reuse_4k_rand_read_Local_SSD_exp"), test_name)
			fn_out = "data/%s-4k-rand-read-%s" % (Conf.Get("reuse_4k_rand_read_Local_SSD_exp"), storage_name)

		# Print last two lines of ioping result
		Cons.P("ioping result:")
		with open(fn_out) as fo:
			lines = fo.readlines()
			Cons.P("  %s" % lines[0].strip())
			for line in lines[-2:]:
				Cons.P("  %s" % line.strip())


# TODO: Should I do parallel random accesses?
# TODO: do some scalability analysis by increasing the load little by little.


def _ReduceIopingResultFileSize(fn, ioping_cmd):
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
		fo.write("# %s\n" % ioping_cmd)
		for line in lines:
			fo.write(line)

	size_after = os.path.getsize(fn)

	Cons.P("File: %s" % fn)
	Cons.P("  Reduced size from %d to %d" % (size_before, size_after))
