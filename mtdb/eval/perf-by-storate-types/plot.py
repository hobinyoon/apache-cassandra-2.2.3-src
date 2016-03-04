#!/usr/bin/env python

import sys

import Conf
import ExpData

# TODO
import PlotData
import Plot


def main(argv):
	Conf.Init()
	ExpData.Load()
	sys.exit(0)
	PlotData.Gen()

	Plot.Plot()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
