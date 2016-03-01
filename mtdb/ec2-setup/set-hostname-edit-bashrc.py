#!/usr/bin/env python

import datetime
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


def SetHostnameAndEditBashrc():
	server_list = []
	client_list = []

	fn = "ec2-server-list"
	with open(fn) as fo:
		for line in fo.readlines():
			server_list.append(line.strip())

	fn = "ec2-client-list"
	with open(fn) as fo:
		for line in fo.readlines():
			client_list.append(line.strip())
	
	if len(server_list) != len(client_list):
		raise RuntimeError("len(server_list)(%d) != len(client_list)(%d)" % (len(server_list), len(client_list)))

	with Cons.MeasureTime("Setting hostname and edit .bashrc ..."):
		for i in range(len(server_list)):
			s_ip = server_list[i]
			c_ip = client_list[i]
			hn = "s%d-c3-2xlarge-%s" % (i, _cur_day)
			#Cons.P(hn)
			cmd = "sudo sed -i 's/localhost$/localhost %s/g' /etc/hosts" \
					" && sudo bash -c 'echo %s > /etc/hostname'" \
					" && sudo hostname --file /etc/hostname" \
					" && echo 'export CASSANDRA_CLIENT_ADDR=%s' >> ~/.bashrc" \
					% (hn, hn, c_ip)
			#Cons.P(cmd)
			cmd = "ssh -o StrictHostKeyChecking=no ubuntu@%s \"%s\"" % (s_ip, cmd)
			#Cons.P(cmd)
			_RunSubp(cmd, print_cmd = True)

		for i in range(len(server_list)):
			s_ip = server_list[i]
			c_ip = client_list[i]
			hn = "c%d-m4-large-%s" % (i, _cur_day)
			#Cons.P(hn)
			cmd = "sudo sed -i 's/localhost$/localhost %s/g' /etc/hosts" \
					" && sudo bash -c 'echo %s > /etc/hostname'" \
					" && sudo hostname --file /etc/hostname" \
					" && echo 'export CASSANDRA_SERVER_ADDR=%s' >> ~/.bashrc" \
					% (hn, hn, s_ip)
			#Cons.P(cmd)
			cmd = "ssh -o StrictHostKeyChecking=no ubuntu@%s \"%s\"" % (c_ip, cmd)
			#Cons.P(cmd)
			_RunSubp(cmd, print_cmd = True)


_cur_day = datetime.datetime.now().strftime("%d")

def main(argv):
	Cons.P("_cur_day=%s" % _cur_day)
	SetHostnameAndEditBashrc()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
