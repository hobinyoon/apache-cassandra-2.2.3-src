#!/usr/bin/env python

import sys

import Conf
import PlotData
import Plot


def main(argv):
	Conf.Init()
	PlotData.Gen()
	Plot.Plot()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
