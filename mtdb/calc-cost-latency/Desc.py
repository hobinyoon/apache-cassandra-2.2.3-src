import sys

sys.path.insert(0, "../util/python")
import Cons

_exp_datetime = None

# Compaction strategy
_cs = None
_cs_options = None


def SetExpDatetime(dt):
	# In yymmdd-HHMMSS
	global _exp_datetime
	_exp_datetime = dt


def ExpDatetime():
	return _exp_datetime


def SetCassMetadata(line):
	global _cs, _cs_options
	t = line.split("compactionStrategyClass=class org.apache.cassandra.db.compaction.")
	if len(t) != 2:
		raise RuntimeError("Unexpected: %s" % line)
	t1 = t[1].split(",")
	_cs = t1[0]
	Cons.P("compaction strategy: %s" % _cs)

	for i in range(1, len(t1)):
		t2 = t1[i].split("compactionStrategyOptions={")
		if len(t2) != 2:
			continue
		_cs_options = t2[1].split("}")[0]
		break
	Cons.P("compaction strategy options: %s" % _cs_options)


def GnuplotDesc():
	desc = "exp datetime: %s" \
			"\ncompaction strategy: %s" \
			"\ncompaction strategy options: %s" \
			% (_exp_datetime, _cs, _cs_options);
	return desc.replace("\n", "\\n")
