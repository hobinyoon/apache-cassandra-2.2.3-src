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
		cmd = "du -hs ~/work/cassandra/data/ && du -hs /mnt/cold-storage/mtdb-cold/"
		cmd = "ssh -o StrictHostKeyChecking=no ubuntu@%s \"%s\"" % (s_ip, cmd)
		#Cons.P(cmd)
		Cons.P("s%d %s" % (i, s_ip))
		Cons.P(Util.Indent(_RunSubp(cmd, print_cmd = False), 2))


def main(argv):
	CheckMutantsDataSize()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
