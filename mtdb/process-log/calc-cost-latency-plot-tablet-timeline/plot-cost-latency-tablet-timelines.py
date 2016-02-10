#!/usr/bin/env python

import sys

import Conf
import CassLogReader
import LoadgenLogReader
import Plot
import StorageSizeByTimePlotDataGenerator
import TabletSizeTimelinePlotDataGenerator
import TabletAccessesForTabletSizeTimelinePlotDataGenerator
import TabletMinMaxTimestampsTimelinePlotDataGenerator
import TabletAccessesForTabletMinMaxTimestampsTimelinePlotDataGenerator


def main(argv):
	Conf.Init()

	LoadgenLogReader.Read()
	LoadgenLogReader.GenLatencyPlotData()

	CassLogReader.Read()
	StorageSizeByTimePlotDataGenerator.Gen()

	TabletSizeTimelinePlotDataGenerator.Gen()
	TabletAccessesForTabletSizeTimelinePlotDataGenerator.Gen()

	TabletMinMaxTimestampsTimelinePlotDataGenerator.Gen()
	TabletAccessesForTabletMinMaxTimestampsTimelinePlotDataGenerator.Gen()

	Plot.Latency()
	Plot.StorageSize()
	Plot.TabletSizesTimeline()
	Plot.TabletMinMaxTimestampsTimeline()


if __name__ == "__main__":
  sys.exit(main(sys.argv))
