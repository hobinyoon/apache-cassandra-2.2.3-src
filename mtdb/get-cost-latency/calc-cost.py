#!/usr/bin/env python

import datetime
import os
import re
import string
import sys

sys.path.insert(0, "../util/python")
import Cons

import CassLogReader
import LoadgenLogReader
import SimTime
import StgCost


def main(argv):
	# Read loadgen log for latency and simulation/simulated time begin/end.
	LoadgenLogReader.Read()

	CassLogReader.Read()
	# TODO: keep the Cassandra log to a separate file for future use
	# TODO:   in the future, may want to get a simulation start time for plotting non-latest simulations

	CassLogReader.CalcCost()

	# TODO: find an equivalent of program_options
	#if len(argv) != 3:
	#	print "Usage: %s fn_in simulated_time_in_year" % (argv[0])
	#	sys.exit(1)


if __name__ == "__main__":
  sys.exit(main(sys.argv))
