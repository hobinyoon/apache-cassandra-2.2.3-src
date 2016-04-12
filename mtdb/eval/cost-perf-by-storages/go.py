#!/usr/bin/env python

# changed to go.py from plot.py to avoid the file name conflict with Plot.py in
# the MacOS file system

import sys

import Conf
import ExpData
import Plot


def main(argv):
	Conf.Init()
	ExpData.Load()
	Plot.Plot()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
