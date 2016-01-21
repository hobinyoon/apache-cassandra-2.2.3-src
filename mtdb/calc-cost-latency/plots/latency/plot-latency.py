#!/usr/bin/env python

import sys

import Conf
import LoadgenLogReader
import Plot


def main(argv):
	Conf.Init()

	LoadgenLogReader.Read()
	LoadgenLogReader.GenPlotData()

	Plot.Plot()


if __name__ == "__main__":
  sys.exit(main(sys.argv))
