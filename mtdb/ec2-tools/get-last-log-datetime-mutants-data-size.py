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


def _RunSubpSsh(s_ip, cmd):
	cmd = "ssh -o StrictHostKeyChecking=no ubuntu@%s \"%s\"" % (s_ip, cmd)
	return _RunSubp(cmd, print_cmd = False)


def GetLogDatetimeAndMutantsDataSize():
	server_list = []

	fn = "ec2-server-list"
	with open(fn) as fo:
		for line in fo.readlines():
			server_list.append(line.strip())

	fmt = "%3s %15s %13s %13s %13s %8s %8s"
	Cons.P(Util.BuildHeader(fmt, "server_name server_ip" \
			" loadgen_log_datetime" \
			" num_cass_threads_datetime" \
			" collectl_datetime" \
			" hot_data_size" \
			" cold_data_size" \
			))

	for i in range(len(server_list)):
		s_ip = server_list[i]
		cmd = "ls -tl ~/work/cassandra/mtdb/logs/loadgen/ | head -n 2 | tail -n 1"
		line = _RunSubpSsh(s_ip, cmd)
		#Cons.P(line)
		loadgen_log_datetime = line.split()[8]

		cmd = "ls -tl ~/work/cassandra/mtdb/logs/cassandra/ | head -n 2 | tail -n 1"
		line = _RunSubpSsh(s_ip, cmd)
		cass_log_datetime = line.split()[8]
		if loadgen_log_datetime != cass_log_datetime:
			Cons.P("Unexpected: loadgen_log_datetime(%s) != cass_log_datetime(%s)" % (loadgen_log_datetime, cass_log_datetime))

		cmd = "ls -tl ~/work/cassandra/mtdb/logs/num-cass-threads/ | head -n 2 | tail -n 1"
		line = _RunSubpSsh(s_ip, cmd)
		num_cass_threads_datetime = line.split()[8]

		cmd = "ls -tl ~/work/cassandra/mtdb/logs/collectl/ | head -n 2 | tail -n 1"
		line = _RunSubpSsh(s_ip, cmd)
		collectl_datetime = line.split()[8]
		if not collectl_datetime.startswith("collectl-"):
			Cons.P("Unexpected: collectl_datetime=[%s]" % collectl_datetime)
		collectl_datetime = collectl_datetime[9:]

		cmd = "du -hs ~/work/cassandra/data/ && du -hs /mnt/cold-storage/mtdb-cold/"
		lines = _RunSubpSsh(s_ip, cmd)
		#Cons.P(lines)
		# 556M	/home/ubuntu/work/cassandra/data/
		# 12K	/mnt/cold-storage/mtdb-cold/
		lines = lines.split("\n")
		t = lines[0].split()
		if t[1] != "/home/ubuntu/work/cassandra/data/":
			raise RuntimeError("Unexpected: line=[%s]" % lines[0])
		hot_data_size = t[0]

		t = lines[1].split()
		if t[1] != "/mnt/cold-storage/mtdb-cold/":
			raise RuntimeError("Unexpected: line=[%s]" % lines[1])
		cold_data_size = t[0]

		Cons.P(fmt % ("s%d" % i, s_ip
			, loadgen_log_datetime
			, num_cass_threads_datetime
			, collectl_datetime
			, hot_data_size
			, cold_data_size
			))


def main(argv):
	GetLogDatetimeAndMutantsDataSize()


if __name__ == "__main__":
	sys.exit(main(sys.argv))
