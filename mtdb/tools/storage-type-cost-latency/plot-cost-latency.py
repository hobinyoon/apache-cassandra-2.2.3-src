#!/usr/bin/env python

import sys

import Conf
import PlotData
import Plot

def main(argv):
	# Plot storage cost on the x-axis, and avg, 1st, 99th percentile latency on
	# the y-axis

	Conf.Init()
	PlotData.Gen()
	Plot.Plot()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
