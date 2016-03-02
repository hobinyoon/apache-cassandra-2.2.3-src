#!/usr/bin/env python

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


def CheckMutantsDataSize():
	server_list = []

	fn = "ec2-server-list"
	with open(fn) as fo:
		for line in fo.readlines():
			server_list.append(line.strip())

	for i in range(len(server_list)):
		s_ip = server_list[i]
		#cmd = "ls -tl ~/work/cassandra/mtdb/logs/loadgen/ | head -n 2 | tail -n 1 | awk '{ print $9 }'"
		cmd = "ls -tl ~/work/cassandra/mtdb/logs/loadgen/ | head -n 2 | tail -n 1"
		cmd = "ssh -o StrictHostKeyChecking=no ubuntu@%s \"%s\"" % (s_ip, cmd)
		#Cons.P(cmd)
		line = _RunSubp(cmd, print_cmd = False)
		loadgen_log_datetime = line.split()[8]
		Cons.P("%3s %15s %s" % ("s%d" % i, s_ip, loadgen_log_datetime))


def main(argv):
	CheckMutantsDataSize()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
