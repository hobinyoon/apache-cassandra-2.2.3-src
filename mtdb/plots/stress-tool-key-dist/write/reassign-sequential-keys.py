#!/usr/bin/env python

import os
import sys

fn_in = None
fn_out = None

keys_map = {}
keys = []
rea_map = {}

def LoadKeys():
	global keys_map
	fn = "read-keys"
	with open(fn_in) as fo:
		for line in fo.readlines():
			k = int(line)
			keys.append(k)
			if k not in keys_map:
				# Assign 0, which doesn't have a meaning yet
				keys_map[k] = 0
			#print keys_map[k]


def BuildReassignMap():
	global rea_map
	idx = 0
	for k in sorted(keys_map):
		#print k
		rea_map[k] = idx
		idx += 1


def PrintReassignedKeys():
	global keys
	global rea_map
	with open(fn_out, "w") as fo:
		for k in keys:
			#print k, rea_map[k]
			fo.write("%d\n" % rea_map[k])
	print "Created file %s %d" % (fn_out, os.path.getsize(fn_out))


def main(argv):
	if len(argv) != 3:
		print "Usage: %s fn_in fn_out" % (argv[0])
		sys.exit(1)

	global fn_in
	global fn_out
	fn_in = argv[1]
	fn_out = argv[2]

	LoadKeys()
	BuildReassignMap()
	PrintReassignedKeys()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
