#!/usr/bin/env python

import sys

import Conf
import Latency
#import CompareCost
#import CompareLatency
#import Plot

def main(argv):
	Conf.Init()
	Latency.Load()
	sys.exit(0)
	#CompareLatency.Compare()
	#CompareCost.Compare()
	#Plot.Plot()


if __name__ == "__main__":
  sys.exit(main(sys.argv))
