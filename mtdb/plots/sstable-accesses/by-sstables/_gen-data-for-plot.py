#!/usr/bin/env python

import os
import string
import sys

sys.path.insert(0, "../../../util/python")
import Util

fn_in = None
fn_out = None

class ReadCnt:
	def __init__(self, r, fp, tp):
		self.reads = r
		self.bf_fp = fp
		self.bf_tp = tp
		self.bf_n = r - fp - tp
		self.reads_miss = r - tp

	def __str__(self):
		return "%8d %4d %7d %8d %8d" % (self.reads, self.bf_fp, self.bf_tp, self.bf_n, self.reads_miss)

	def __add__(self, r):
		return ReadCnt(
				self.reads + r.reads,
				self.bf_fp + r.bf_fp,
				self.bf_tp + r.bf_tp)

	def __sub__(self, r):
		return ReadCnt(
				self.reads - r.reads,
				self.bf_fp - r.bf_fp,
				self.bf_tp - r.bf_tp)


def ReadInputAndGenFormattedFile():
	global fn_in
	last_line = None
	with open(fn_in) as fo:
		for line in fo.readlines():
			# print line
			if len(line) == 0:
				continue
			if line[0] == "#":
				continue
			last_line = line
	
	if last_line == None:
		raise RuntimeError("Can't find the last line")

	time = None
	sst_readcnt = {}
	t = last_line.split()
	#print len(t)
	for i in range(len(t)):
		if i == 0:
			time = t[i]
			continue
		elif i == 1:
			# replace decimal point , with .
			time += ("-" + string.replace(t[i], ",", "."))
			continue

		t2 = t[i].split(":")
		if len(t2) != 2:
			raise RuntimeError("Unexpected format: [%s] [%s]" % (last_line, t2))
		sstable_gen = int(t2[0])
		t3 = t2[1].split(",")
		if len(t3) != 3:
			raise RuntimeError("Unexpected format: [%s] [%s]" % (last_line, t2))
		read_cnt = int(t3[0])
		bf_fp_cnt = int(t3[1])
		bf_tp_cnt = int(t3[2])
	
		sst_readcnt[sstable_gen] = ReadCnt(read_cnt, bf_fp_cnt, bf_tp_cnt)

	with open(fn_out, "w") as fo:
		fo.write("# time: %s\n" % time)
		fo.write("#\n")
		fmt = "%2d %8d %4d %7d %8d %8d"
		header = Util.BuildHeader(fmt, "sstable_gen read_cnt bf_fp_cnt bf_tp_cnt(read_hit) bf_n_cnt read_miss")
		fo.write(header)
		for k, v in sorted(sst_readcnt.iteritems()):
			fo.write("%2d %s\n" % (k, v))
	print "Created file %s %d" % (fn_out, os.path.getsize(fn_out))




def main(argv):
	if len(argv) != 2:
		print "Usage: %s fn_in" % (argv[0])
		sys.exit(1)

	global fn_in
	global fn_out
	fn_in = argv[1]
	fn_out = fn_in + "-by-sstables"

	ReadInputAndGenFormattedFile()


if __name__ == "__main__":
  sys.exit(main(sys.argv))
