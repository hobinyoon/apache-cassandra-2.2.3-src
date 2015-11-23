#!/usr/bin/env python

# This is not right. I got confused. Each line has cumulative numbers already.

import sys

fn_in = None

class ReadCnt:
	def __init__(self, r, fp, tp):
		self.reads = r
		self.bf_fp = fp
		self.bf_tp = tp
		self.bf_n = r - fp - tp

	def __str__(self):
		return "%8d %4d %7d %8d" % (self.reads, self.bf_fp, self.bf_tp, self.bf_n)

	def Add0(self, r, fp, tp):
		self.reads += r
		self.bf_fp += fp
		self.bf_tp += tp
		self.bf_n += (r - fp - tp)

	def Add1(self, rc):
		self.reads += rc.reads
		self.bf_fp += rc.bf_fp
		self.bf_tp += rc.bf_tp
		self.bf_n += rc.bf_n


def ReadInputAndPrintCnts():
	sstable_cnts = {}

	global fn_in
	with open(fn_in) as fo:
		for line in fo.readlines():
			# print line
			if len(line) == 0:
				continue
			if line[0] == "#":
				continue

			t = line.split()
			#print len(t)
			for i in range(len(t)):
				if i == 0:
					time = t[0]
					continue

				t2 = t[i].split(":")
				if len(t2) != 2:
					raise RuntimeError("Unexpected format: [%s] [%s]" % (line, t2))
				sstable_gen = int(t2[0])
				t3 = t2[1].split(",")
				if len(t3) != 3:
					raise RuntimeError("Unexpected format: [%s] [%s]" % (line, t2))
				read_cnt = int(t3[0])
				bf_fp_cnt = int(t3[1])
				bf_tp_cnt = int(t3[2])

				if sstable_gen in sstable_cnts:
					sstable_cnts[sstable_gen].Add0(read_cnt, bf_fp_cnt, bf_tp_cnt)
				else:
					sstable_cnts[sstable_gen] = ReadCnt(read_cnt, bf_fp_cnt, bf_tp_cnt)

	print "# sstable_gen reads bf_fp bf_tp bf_n"
	total = ReadCnt(0, 0, 0)
	for k, v in sstable_cnts.iteritems():
		print "%2d %s" % (k, v)
		total.Add1(v)

	print
	print "# total: reads bf_fp bf_tp bf_n"
	print "# %s" % total


def main(argv):
	if len(argv) != 2:
		print "Usage: %s fn_in" % (argv[0])
		sys.exit(1)

	global fn_in
	fn_in = argv[1]

	ReadInputAndPrintCnts()


if __name__ == "__main__":
  sys.exit(main(sys.argv))
