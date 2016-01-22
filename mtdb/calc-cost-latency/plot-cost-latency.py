#!/usr/bin/env python

import sys

import Conf
import CassLogReader
import LoadgenLogReader
import Plot
import TabletTimelinePlotDataGenerator


def main(argv):
	Conf.Init()

	LoadgenLogReader.Read()
	LoadgenLogReader.GenLatencyPlotData()

	CassLogReader.Read()
	# TODO: I may want to parameterize some of these
	#CassLogReader.GenStorageSizePlotData()
	TabletTimelinePlotDataGenerator.Gen()

	# TODO
	#Plot.Latency()
	#Plot.StorageSize()
	Plot.TabletTimeline()


if __name__ == "__main__":
  sys.exit(main(sys.argv))
