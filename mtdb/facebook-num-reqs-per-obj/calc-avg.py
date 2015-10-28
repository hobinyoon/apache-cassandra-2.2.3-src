#!/usr/bin/env python

import sys

obj_rank_num_reqs = {}

def LoadData():
	fn = "facebook-num-reqs-by-rank"
	with open(fn) as fo:
		for line in fo.readlines():
			if len(line) == 0:
				continue
			if line[0] == "#":
				continue
			tokens = line.split()
			if len(tokens) != 2:
				raise RuntimeError("Unexpected format line=[%s]" % (line))
			obj_rank = int(tokens[0])
			num_reqs = float(tokens[1])
			if obj_rank not in obj_rank_num_reqs:
				obj_rank_num_reqs[obj_rank] = num_reqs
	#print obj_rank_num_reqs


def CalcAvg():
	prev_rank = 0
	total_reqs = 0.0

	# Assume num_reqs in the range of (r_i, r_(i+1)], num_reqs is that of
	# r_(i+1).
	for rank, num_req in sorted(obj_rank_num_reqs.items()):
		while prev_rank != rank:
			prev_rank += 1
			total_reqs += num_req
	
	print prev_rank, total_reqs, (total_reqs / prev_rank)


def main(argv):
	LoadData()
	CalcAvg()


if __name__ == "__main__":
  sys.exit(main(sys.argv))
