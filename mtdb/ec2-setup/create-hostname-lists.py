#!/usr/bin/env python

import json
import os
import subprocess
import sys

sys.path.insert(0, "../util/python")
import Cons
import Util


def _RunSubp(cmd, env_ = os.environ.copy(), print_cmd = True):
	if print_cmd:
		Cons.P(cmd)
	p = subprocess.Popen(cmd, shell=True, env=env_, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	# communidate() waits for termination
	stdouterr = p.communicate()[0]
	rc = p.returncode
	if rc != 0:
		raise RuntimeError("Error: cmd=[%s] rc=%d stdouterr=[%s]" % (cmd, rc, stdouterr))
	return stdouterr


_inst_type_ipaddr = {}

def GetIpAddrs():
	cmd = "aws ec2 describe-instances"
	with Cons.MeasureTime(cmd):
		insts = _RunSubp(cmd, print_cmd = False)
		#Cons.P(insts)
		j = json.loads(insts)
		for i1 in j["Reservations"]:
			for i2 in i1["Instances"]:
				it = i2["InstanceType"]
				ipaddr = i2["PublicIpAddress"]

				if it not in _inst_type_ipaddr:
					_inst_type_ipaddr[it] = []
				_inst_type_ipaddr[it].append(ipaddr)
		
		#for it, v in _inst_type_ipaddr.iteritems():
		#	Cons.P(it)
		#	for ipaddr in v:
		#		Cons.P("  %s" % ipaddr)
	
		fn = "ec2-server-list"
		with open(fn, "w") as fo:
			for ipaddr in _inst_type_ipaddr["c3.2xlarge"]:
				fo.write("%s\n" % ipaddr)
		Cons.P("Created %s %d" % (fn, os.path.getsize(fn)))
		
		fn = "ec2-client-list"
		with open(fn, "w") as fo:
			for ipaddr in _inst_type_ipaddr["m4.large"]:
				fo.write("%s\n" % ipaddr)
		Cons.P("Created %s %d" % (fn, os.path.getsize(fn)))


def main(argv):
	GetIpAddrs()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
