#!/usr/bin/env python

import os
import sys


fn_read_keys = None
dn_sstable_keys = None
read_keys = []
key_sstgen = {}


def LoadReadKeys():
	global read_keys
	print "loading read keys from %s ..." % fn_read_keys
	with open(fn_read_keys) as fo:
		for line in fo.readlines():
			read_keys.append(line.strip().lower())


def LoadSSTableKeys():
	global dn_sstable_keys
	global key_sstgen
	print "loading sstable keys from %s ..." % dn_sstable_keys

	sst_gen = 0
	while True:
		sst_gen += 1
		fn = "%s/keys-%d" % (dn_sstable_keys, sst_gen)
		if not os.path.isfile(fn): 
			break

		with open(fn) as fo:
			for line in fo.readlines():
				key = line.strip()
				if key not in key_sstgen:
					key_sstgen[key] = []
				key_sstgen[key].append(sst_gen)

	print "len(key_sstgen)=%d" % len(key_sstgen)
	

def CheckDupKeys():
	print "Checking duplicate keys ..."
	for k, v in key_sstgen.iteritems():
		if len(v) > 1:
			print k, v


def CountReadsBySSTables():
	sstgen_readcnt_first = {}
	sstgen_readcnt_all = {}
	memtable_read_cnt = 0
	print "len(read_keys)=%d" % len(read_keys)

	for rk in read_keys:
		# If a read key is not in any of the sstables, it may be in the memtable
		if rk not in key_sstgen:
			memtable_read_cnt += 1
			continue

		# Get the youngest sstable, which is the last one in the list
		sstgen = key_sstgen[rk][-1]
		if sstgen not in sstgen_readcnt_first:
			sstgen_readcnt_first[sstgen] = 1
		else:
			sstgen_readcnt_first[sstgen] += 1

		for sstgen in key_sstgen[rk]:
			if sstgen not in sstgen_readcnt_all:
				sstgen_readcnt_all[sstgen] = 1
			else:
				sstgen_readcnt_all[sstgen] += 1
	
	print "memtable_read_cnt=%d" % memtable_read_cnt
	print "sstable_readcnt: sstgen first_hit all_hit:"
	for k, v in sorted(sstgen_readcnt_first.iteritems()):
		print "  %2d %6d %6d" % (k, v, sstgen_readcnt_all[k])


def main(argv):
	if len(argv) != 3:
		print "Usage: %s fn_read_keys dn_sstable_keys" % (argv[0])
		print "  E.g.: %s data/read-keys-15-11-26-18:15:55 ../check-keys-in-sstables/standard1-2d180380949311e5945a1d822de6a4f1" % (argv[0])
		sys.exit(1)
	
	global fn_read_keys
	global dn_sstable_keys
	fn_read_keys = argv[1]
	dn_sstable_keys = argv[2]
	
	LoadReadKeys()
	LoadSSTableKeys()

	#CheckDupKeys()
	CountReadsBySSTables()

	# Stopping when the max timestamp of a sstable is older than the current timestamp is not simulated.
	# We assume that bigger sstable gens have younger keys (records)


if __name__ == "__main__":
	sys.exit(main(sys.argv))
