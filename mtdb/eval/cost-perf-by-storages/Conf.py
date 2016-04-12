import sys
import yaml

sys.path.insert(0, "../../util/python")
import Cons

_conf = None

def Init():
	_ParseYaml()


def Get(key):
	return _conf[key]


def _ParseYaml():
	global _conf
	with open("configuration.yaml", 'r') as stream:
		_conf = yaml.load(stream)
		#Cons.P(_conf)
