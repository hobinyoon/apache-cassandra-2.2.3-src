#!/usr/bin/env python

import os
import re
import subprocess
import sys
import time
import Cons


def _SubpPopen(cmd_list, stdout=None, stderr=None, env=None):
	#print cmd_list.split()
	#return subprocess.Popen(cmd_list.split(), stdout=stdout, stderr=stderr, env=env)
	p = subprocess.Popen(cmd_list.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	# communidate() waits for termination
	stdouterr = p.communicate()[0]
	rc = p.returncode
	if rc != 0:
		raise RuntimeError("Error: cmd=[%s] rc=%d stdouterr=[%s]" % (cmd_list, rc, stdouterr))
	return stdouterr


# Return rand read perf in kB/s
def _4kReadIozone(cmd):
	with Cons.Indent(cmd):
		stdouterr = _SubpPopen(cmd)
		#Cons.P(stdouterr)

		# Get random read perf from Excel-style report
		lines = stdouterr.split("\n")
		i = 0
		while i < len(lines):
			if "Random read report" in lines[i]:
				if (i + 2) >= len(lines):
					raise RuntimeError("Unexpected: i=%d len(lines)=%d" % (i, len(lines)))
				#print re.split(r" +", lines[i + 2])
				return float(re.split(r" +", lines[i + 2])[1])
			i += 1
		raise RuntimeError("Unexpected: cannot parse the output")

		## Get random read perf
		#lines = stdouterr.split("\n")
		#i = 0
		#while i < len(lines):
		#	if "kB  reclen    write  rewrite" in lines[i]:
		#		if (i + 1) >= len(lines):
		#			raise RuntimeError("Unexpected: i=%d len(lines)=%d" % (i, len(lines)))
		#		#print re.split(r" +", lines[i + 1])
		#		return float(re.split(r" +", lines[i + 1])[7])
		#	i += 1
		#raise RuntimeError("Unexpected: cannot parse the output")


# Returns latency in ms
def _4kReadIoping(cmd):
	with Cons.Indent(cmd):
		stdouterr = _SubpPopen(cmd)
		#Cons.P(stdouterr)

		# Get avg latency
		avg = []
		for line in stdouterr.split("\n"):
			if len(line) == 0:
				continue
			#print line.split()
			# avg in a time period
			avg.append(float(line.split()[5]))
		#Cons.P("Avg: %f" % (sum(avg) / len(avg)))
		return sum(avg) / len(avg)


_dnNfsRoot = "/mnt/s5-cass-cold-storage"
_dnLocal = "/mnt/data"


def _4kReads():
	with Cons.Indent("4 KB random read test ..."):
		#local = _4kReadIozone("iozone -r 4k -s 1m -R %s" % _dnLocal)
		#nfs   = _4kReadIozone("iozone -r 4k -s 1m -R %s" % _dnNfsRoot)
		#local_direct = _4kReadIozone("iozone -r 4k -s 1m -R -I %s" % _dnLocal)
		#nfs_direct   = _4kReadIozone("iozone -r 4k -s 1m -R -I %s" % _dnNfsRoot)
		local        = _4kReadIoping("ioping -c 100 -p 10 -i 0 -q %s" % _dnLocal)
		nfs          = _4kReadIoping("ioping -c 100 -p 10 -i 0 -q %s" % _dnNfsRoot)
		local_direct = _4kReadIoping("ioping -c 100 -p 10 -i 0 -D -q %s" % _dnLocal)
		nfs_direct   = _4kReadIoping("ioping -c 100 -p 10 -i 0 -D -q %s" % _dnNfsRoot)

		Cons.P("Regular:")
		Cons.P("  Local: %7.2f ms" % (local))
		Cons.P("  NFS  : %7.2f ms %5.2f%% of localFS" % (nfs, 100.0 * nfs / local))
		Cons.P("Direct:")
		Cons.P("  Local: %7.2f ms" % (local_direct))
		Cons.P("  NFS  : %7.2f ms %5.2f%% of localFS" % (nfs_direct, 100.0 * nfs_direct / local_direct))


# returns latency for writing a 160 MB file
def _160mWrite(cmd, fn):
	with Cons.Indent(cmd):
		stdouterr = _SubpPopen(cmd)
		#Cons.P(stdouterr)

	# Get the perf. Use byte and sec numbers; the computed one is rounded to integer
	lines = stdouterr.split("\n")
	bytes_ = None
	sec = None
	for line in lines:
		if "copied," in line:
			tokens = re.split(r" +", line)
			bytes_ = tokens[0]
			sec = tokens[5]
	if (bytes_ == None) or (sec == None):
		raise RuntimeError("Unexpected: cannot parse the output")

	# Delete the file
	os.remove(fn)

	return float(sec)

	# Throughput in B/sec
	#return float(bytes_) / float(sec)


def _160mWrites():
	fn = "dd-160MB-write-test"
	fnLocal = "%s/%s" % (_dnLocal, fn)
	fnNfs = "%s/%s" % (_dnNfsRoot, fn)

	with Cons.Indent("160 MB write test ..."):
		local        = _160mWrite("dd if=/dev/zero of=%s bs=160M count=1" % fnLocal, fnLocal)
		nfs          = _160mWrite("dd if=/dev/zero of=%s bs=160M count=1" % fnNfs, fnNfs)
		local_direct = _160mWrite("dd if=/dev/zero of=%s bs=160M oflag=direct count=1" % fnLocal, fnLocal)
		nfs_direct   = _160mWrite("dd if=/dev/zero of=%s bs=160M oflag=direct count=1" % fnNfs, fnNfs)

		Cons.P("Regular:")
		Cons.P("  Local: %7f sec" % local)
		Cons.P("  NFS  : %7f sec %7.2f%% of localFS" % (nfs, 100.0 * nfs / local))
		Cons.P("Direct:")
		Cons.P("  Local: %7f sec" % local_direct)
		Cons.P("  NFS  : %7f sec %7.2f%% of localFS" % (nfs_direct, 100.0 * nfs_direct / local_direct))

		#Cons.P("Regular:")
		#Cons.P("  Local: %7.2f MB/s" % (local / 1024 / 1024))
		#Cons.P("  NFS  : %7.2f MB/s %5.2f%% of localFS" % (nfs / 1024 / 1024, 100.0 * nfs / local))
		#Cons.P("Direct:")
		#Cons.P("  Local: %7.2f MB/s" % (local_direct / 1024 / 1024))
		#Cons.P("  NFS  : %7.2f MB/s %5.2f%% of localFS" % (nfs_direct / 1024 / 1024, 100.0 * nfs_direct / local_direct))


def main(argv):
	_4kReads()
	_160mWrites()


if __name__ == "__main__":
  sys.exit(main(sys.argv))
