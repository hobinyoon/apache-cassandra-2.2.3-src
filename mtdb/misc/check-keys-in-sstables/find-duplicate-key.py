#!/usr/bin/env python

import sys

def LoadKeysAndPrintDups():
	key_sstgen = {}
	for i in range(17):
		sstgen = i+1
		#print sstgen
		fn = "keys-%d" % sstgen
		print "loading file %s ..." % fn
		with open(fn) as fo:
			for line in fo.readlines():
				key = line.strip()
				if key not in key_sstgen:
					key_sstgen[key] = []
				key_sstgen[key].append(sstgen)

	for k, v in sorted(key_sstgen.iteritems()):
		if len(v) != 1:
			print k, v


def main(argv):
	LoadKeysAndPrintDups()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
