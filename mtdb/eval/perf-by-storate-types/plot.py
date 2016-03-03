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
	PlotData.Gen()

	sys.exit(0)
	Plot.Plot()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
