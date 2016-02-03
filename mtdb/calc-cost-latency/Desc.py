import re
import sys

sys.path.insert(0, "../util/python")
import Cons
import Util

_exp_datetime = None

# Compaction strategy
_cs = None
_cs_options = None
_memtable_heap_space_in_mb = None
_mutants_options = None


def SetExpDatetime(dt):
	# In yymmdd-HHMMSS
	global _exp_datetime
	_exp_datetime = dt


def ExpDatetime():
	return _exp_datetime


def SetNodeConfiguration(line_from_op):
	mo = re.search(re.compile(r"memtable_heap_space_in_mb=\d+"), line_from_op)
	#Cons.P(mo.group(0))
	global _memtable_heap_space_in_mb
	_memtable_heap_space_in_mb = mo.group(0)

	mo = re.search(re.compile(r"mutants_options={[^}]+}"), line_from_op)
	#Cons.P(mo.group(0))
	global _mutants_options
	_mutants_options = mo.group(0).replace("{", "\n  ").replace(", ", "\n  ").replace("}", "")


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
			"\n%s" \
			"\n%s" \
			% (_exp_datetime
					, _cs
					, _cs_options
					, _memtable_heap_space_in_mb
					, _mutants_options)
	return desc.replace("\n", "\\n").replace("_", "\_")
