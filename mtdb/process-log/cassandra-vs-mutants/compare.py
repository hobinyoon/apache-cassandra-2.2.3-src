#!/usr/bin/env python

import sys

import Conf
import CompareCost
import CompareLatency
import Plot

def main(argv):
	Conf.Init()
	CompareLatency.Compare()
	CompareCost.Compare()
	Plot.Plot()


if __name__ == "__main__":
  sys.exit(main(sys.argv))
