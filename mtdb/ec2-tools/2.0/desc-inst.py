#!/usr/bin/env python

import os
import subprocess
import sys

sys.path.insert(0, "../../util/python")
import Cons
import Util


def _RunSubp(cmd, env_ = os.environ.copy()):
	p = subprocess.Popen(cmd, shell=True, env=env_, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	# communidate() waits for termination
	stdouterr = p.communicate()[0]
	rc = p.returncode
	if rc != 0:
		raise RuntimeError("Error: cmd=[%s] rc=%d stdouterr=[%s]" % (cmd, rc, stdouterr))
	return stdouterr


class Ec2Inst:
	def __init__(self, line):
		#Cons.P(line)

		self.running = False
		t = line.split()

		# INSTANCE	i-3d1aceba	ami-1fc7d575			terminated		0		c3.2xlarge
		# 2016-04-14T20:43:02+0000	us-east-1d				monitoring-disabled
		# ebs	spot	sir-029kf0mc	hvm	xen	4149c7ae-0738-4c39-90c0-da33c69968be
		# sg-d0b9cab9	default	true
		if (len(t) == 18) and (t[3] == "terminated"):
			return

		# INSTANCE	i-3d1aceba	ami-1fc7d575
		# ec2-54-160-170-177.compute-1.amazonaws.com
		# ip-10-13-198-12.ec2.internal	running		0	c3.2xlarge
		# 2016-04-14T20:43:02+0000	us-east-1d				monitoring-disabled
		# 54.160.170.177	10.13.198.12		ebs	spot	sir-029kf0mc		hvm	xen
		# 4149c7ae-0738-4c39-90c0-da33c69968be	sg-d0b9cab9	default	true
		if len(t) != 22:
			raise RuntimeError("Unexpected format: [%s]" % line)
		self.type = t[7]
		self.ip_addr = t[11]
		self.running = True


def _GetEc2InstInfo():
	cmd = "ec2-describe-instances"
	insts = []
	lines = _RunSubp(cmd).split("\n")
	for line in lines:
		#Cons.P(line)
		if line.startswith("INSTANCE"):
			e = Ec2Inst(line)
			if e.running:
				insts.append(e)

	for i in insts:
		#Cons.P(i.type)
		Cons.P(i.ip_addr)

	return insts


def main(argv):
	insts = _GetEc2InstInfo()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
