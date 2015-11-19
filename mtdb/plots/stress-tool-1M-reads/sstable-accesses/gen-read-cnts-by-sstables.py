#!/usr/bin/env python

import sys


class ReadCnt:
	def __init__(self, r, fp, tp):
		self.reads = r
		self.bf_fp = fp
		self.bf_tp = tp
		self.bf_n = r - fp - tp

	def __str__(self):
		return "%8d %4d %7d %8d" % (self.reads, self.bf_fp, self.bf_tp, self.bf_n)

	def Add(self, r, fp, tp):
		self.reads += r
		self.bf_fp += fp
		self.bf_tp += tp
		self.bf_n += (r - fp - tp)


def Load():
	sstable_cnts = {}

	fn = "data-sstable-accesses"
	with open(fn) as fo:
		for line in fo.readlines():
			# print line
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
					sstable_cnts[sstable_gen].Add(read_cnt, bf_fp_cnt, bf_tp_cnt)
				else:
					sstable_cnts[sstable_gen] = ReadCnt(read_cnt, bf_fp_cnt, bf_tp_cnt)

	print "# sstable_gen reads bf_fp bf_tp bf_n"
	for k, v in sstable_cnts.iteritems():
		print "%2d %s" % (k, v)



def main(argv):
  # Load input file
  Load()

  # Generate data
  # Plot can be done with a shell script


if __name__ == "__main__":
  sys.exit(main(sys.argv))
