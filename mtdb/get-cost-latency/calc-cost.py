#!/usr/bin/env python

import sys

sys.path.insert(0, "../util/python")
import Cons

import CassLogReader
import Conf
import LoadgenLogReader


def main(argv):
	Conf.Init()

	# Loadgen log has latency and simulation/simulated time begin/end
	LoadgenLogReader.Read()

	# Cassandra MTDB log has events of memtables and sstables
	CassLogReader.Read()

	CassLogReader.CalcCost()


if __name__ == "__main__":
  sys.exit(main(sys.argv))
