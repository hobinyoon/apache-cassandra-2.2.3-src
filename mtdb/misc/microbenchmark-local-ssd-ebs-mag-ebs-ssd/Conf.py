import argparse
import datetime
import sys
import yaml

sys.path.insert(0, "../../util/python")
import Cons

dn_output="/run/storage-perf-test"

dn_local_ssd="/mnt/local-ssd"
dn_ebs_ssd="/mnt/ebs-ssd-gp2"
dn_ebs_mag="/mnt/ebs-mag"

_exp_datetime = None

def ExpDatetime():
	global _exp_datetime
	if _exp_datetime == None:
		_exp_datetime = datetime.datetime.now()
	return datetime.datetime.strftime(_exp_datetime, "%y%m%d-%H%M%S") 












_conf = None



def Init():
	_ParseYaml()
	#_ParseCmdlineArgs()


def Get(key):
	return _conf[key]


def _ParseYaml():
	global _conf
	with open("configuration.yaml", 'r') as stream:
		_conf = yaml.load(stream)
		#Cons.P(_conf)


# Implement when needed
def _ParseCmdlineArgs():
	global _conf
	# https://docs.python.org/2/library/argparse.html#module-argparse
	parser = argparse.ArgumentParser(description="Cassandra vs Mutants"
			, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("--cass", type=str, default=_conf["cassandra_experiment_datetime"], help="Cassandra experiment datetime")
	parser.add_argument("--mutants", type=str, default=_conf["mutants_experiment_datetime"], help="Mutants experiment datetime")

	args = parser.parse_args()
	#Cons.P(args)
	_conf["cassandra_experiment_datetime"] = args.cass
	_conf["mutants_experiment_datetime"] = args.mutants
	#Cons.P(_conf)
