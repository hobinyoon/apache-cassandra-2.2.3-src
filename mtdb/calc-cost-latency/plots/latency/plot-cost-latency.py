#!/usr/bin/env python

import sys

import Conf
import CassLogReader
import LoadgenLogReader
import Plot


def main(argv):
	Conf.Init()

	LoadgenLogReader.Read()
	LoadgenLogReader.GenLatencyPlotData()

	CassLogReader.Read()
	CassLogReader.GenStorageSizePlotData()

	Plot.Latency()
	Plot.StorageSize()


if __name__ == "__main__":
  sys.exit(main(sys.argv))
