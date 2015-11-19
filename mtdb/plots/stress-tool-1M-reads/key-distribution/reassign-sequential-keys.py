#!/usr/bin/env python

import sys


idx_key = {}
keys = []
rea_map = {}

def LoadKeys():
	global idx_key
	fn = "read-keys"
	with open(fn) as fo:
		for line in fo.readlines():
			k = int(line)
			keys.append(k)
			if k not in idx_key:
				# Assign 0, which doesn't have a meaning yet
				idx_key[k] = 0
			#print idx_key[k]


def BuildReassignMap():
	global rea_map
	idx = 0
	for k in sorted(idx_key):
		#print k
		rea_map[k] = idx
		idx += 1


def PrintReassignedKeys():
	for k in keys:
		#print k, rea_map[k]
		print rea_map[k]


def main(argv):
	LoadKeys()
	BuildReassignMap()
	PrintReassignedKeys()


if __name__ == "__main__":
  sys.exit(main(sys.argv))
