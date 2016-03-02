#!/usr/bin/env python

import os
import subprocess
import sys

sys.path.insert(0, "../util/python")
import Cons


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


def CopyEc2Logs():
	server_list = []

	fn = "ec2-server-list"
	with open(fn) as fo:
		for line in fo.readlines():
			server_list.append(line.strip())

	with Cons.MeasureTime("Copying ec2 server logs ..."):
		for ip in server_list:
			# Was thinkinf of labeling log file names with the server hostname, but
			# it will break log processing tools
			cmd = "rsync -ave \"ssh -o StrictHostKeyChecking=no\" ubuntu@%s:work/cassandra/mtdb/logs ~/work/cassandra/mtdb/" \
					% ip
			_RunSubp(cmd, print_cmd = True)


def main(argv):
	CopyEc2Logs()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
