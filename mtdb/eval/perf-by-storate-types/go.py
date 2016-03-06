#!/usr/bin/env python

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
