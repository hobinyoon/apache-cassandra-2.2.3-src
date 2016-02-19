import argparse
import sys
import yaml

sys.path.insert(0, "../../util/python")
import Cons

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
