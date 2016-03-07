import sys
import yaml

sys.path.insert(0, "../../util/python")
import Cons

_conf = None

def Init():
	_ParseYaml()


def Get(key = None):
	if key == None:
		return _conf
	else:
		return _conf[key]


def _ParseYaml():
	global _conf
	with open("configuration.yaml", 'r') as stream:
		_conf = yaml.load(stream)
		#Cons.P(_conf)
