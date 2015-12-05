#!/usr/bin/env python

import os
import string
import sys

fn_in = None
fn_out = None

class ReadCnt:
	def __init__(self, r, fp, tp):
		self.reads = r
		self.bf_fp = fp
		self.bf_tp = tp
		self.bf_n = r - fp - tp

	def __str__(self):
		return "%8d %4d %7d %8d" % (self.reads, self.bf_fp, self.bf_tp, self.bf_n)

	def __sub__(self, r):
		return ReadCnt(
				self.reads - r.reads,
				self.bf_fp - r.bf_fp,
				self.bf_tp - r.bf_tp)


def ReadInputAndGenFormattedFile():
	sstgen_time_cnt = {}

	global fn_in
	with open(fn_in) as fo:
		for line in fo.readlines():
			# print line
			if len(line) == 0:
				continue
			if line[0] == "#":
				continue

			time = None
			event_type = None
			t = line.split()
			#print len(t)
			for i in range(len(t)):
				if i == 0:
					time = t[i]
					continue
				elif i == 1:
					# replace decimal point , with .
					time += ("-" + string.replace(t[i], ",", "."))
					continue
				elif i == 2:
					event_type = t[i]
					continue

				if event_type != "SstAccess":
					break

				t2 = t[i].split(":")
				if len(t2) != 2:
					raise RuntimeError("Unexpected format: [%s] [%s]" % (line, t2))
				sstable_gen = int(t2[0][3:])
				t3 = t2[1].split(",")
				if len(t3) != 3:
					raise RuntimeError("Unexpected format: [%s] [%s]" % (line, t2))
				read_cnt = int(t3[0])
				bf_fp_cnt = int(t3[1])
				bf_tp_cnt = int(t3[2])

				if sstable_gen not in sstgen_time_cnt:
					sstgen_time_cnt[sstable_gen] = {}

				sstgen_time_cnt[sstable_gen][time] = ReadCnt(read_cnt, bf_fp_cnt, bf_tp_cnt)

	with open(fn_out, "w") as fo:
		fo.write("# sstable_gen              read_cnt    bf_tp_cnt bf_n_cnt\n")
		fo.write("#                     time     bf_fp_cnt\n")
		for k, v in sorted(sstgen_time_cnt.iteritems()):
			v2_prev = None
			v2_inc = None
			for k2, v2 in sorted(v.iteritems()):
				if v2_prev == None:
					v2_inc = v2
				else:
					v2_inc = v2 - v2_prev
				v2_prev = v2
				fo.write("%2d %s %s\n" % (k, k2, v2_inc))
			fo.write("\n")
	print "Created file %s %d" % (fn_out, os.path.getsize(fn_out))


def main(argv):
	if len(argv) != 2:
		print "Usage: %s fn_in" % (argv[0])
		sys.exit(1)

	global fn_in
	global fn_out
	fn_in = argv[1]
	fn_out = fn_in + "-by-sstables-by-time"

	ReadInputAndGenFormattedFile()


if __name__ == "__main__":
  sys.exit(main(sys.argv))
