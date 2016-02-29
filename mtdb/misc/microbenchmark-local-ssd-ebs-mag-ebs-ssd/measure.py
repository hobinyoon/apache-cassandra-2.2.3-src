#!/usr/bin/env python

import sys

import Conf
import Plot
import TestStorage

sys.path.insert(0, "../../util/python")
import Cons
import Util


def main(argv):
	TestStorage.Test()

	sys.exit(0)

	# TODO
	#Conf.Init()
	#PlotData.Gen()
	#Plot.Plot()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
