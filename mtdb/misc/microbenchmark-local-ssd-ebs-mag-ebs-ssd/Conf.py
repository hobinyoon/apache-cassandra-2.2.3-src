import datetime
import sys
import yaml

sys.path.insert(0, "../../util/python")
import Cons


_conf_yaml = None


def Init():
	_ParseYaml()


def Get(key):
	if key in _conf_yaml:
		return _conf_yaml[key]
	else:
		return None;


_exp_datetime = None


def ExpDatetime():
	global _exp_datetime
	if _exp_datetime == None:
		_exp_datetime = datetime.datetime.now()
	return datetime.datetime.strftime(_exp_datetime, "%y%m%d-%H%M%S")


def _ParseYaml():
	global _conf_yaml
	with open("configuration.yaml", 'r') as stream:
		_conf_yaml = yaml.load(stream)
		#Cons.P(_conf_yaml)
