import pprint
import re
import sys

sys.path.insert(0, "../util/python")
import Cons
import Util

import ListMapParser

_exp_datetime = None

# Compaction strategy
_cs = None
_cs_options = None
_memtable_heap_space_in_mb = None
_mutants_options = None
_mutants_loadgen_options = None


def SetExpDatetime(dt):
	# In yymmdd-HHMMSS
	global _exp_datetime
	_exp_datetime = dt


def ExpDatetime():
	return _exp_datetime


def SetNodeConfiguration(line_from_op):
	nc = ListMapParser.Parse(line_from_op)

	global _memtable_heap_space_in_mb
	_memtable_heap_space_in_mb = nc["memtable_heap_space_in_mb"]

	global _mutants_options
	#_mutants_options = pprint.pformat(nc["mutants_options"], indent=2)
	mo = nc["mutants_options"]
	_mutants_options = "cold storage dir: %s" \
			"\nsimulated_time_years: %s" \
			"\nsimulation_time_mins: %s" \
			"\ntablet_coldness_monitor_time_window_simulated_time_days: %s" \
			"\ntablet_coldness_threshold: %s" \
			% (mo["cold_storage_dir"]
					, mo["simulated_time_years"]
					, mo["simulation_time_mins"]
					, mo["tablet_coldness_monitor_time_window_simulated_time_days"]
					, mo["tablet_coldness_threshold"]
					)

	global _mutants_loadgen_options
	mlo = nc["mutants_loadgen_options"]
	_mutants_loadgen_options = "global.num_writes_per_simulation_time_mins: %s" \
			"\nper_obj.avg_reads: %s" \
			"\nper_obj.read_time_dist: %s" \
			"\nper_obj.obj_size: %s" \
			"\ndb.num_threads: %s" \
			% (mlo["global"]["num_writes_per_simulation_time_mins"]
					, mlo["per_obj"]["avg_reads"]
					, mlo["per_obj"]["read_time_dist"]
					, mlo["per_obj"]["obj_size"]
					, mlo["db"]["num_threads"]
					)


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
			"\nmemtable heap space in mb: %s" \
			"\n%s" \
			"\n%s" \
			% (_exp_datetime
					, _cs
					, _cs_options
					, _memtable_heap_space_in_mb
					, _mutants_options
					, _mutants_loadgen_options)
	return desc.replace("\n", "\\n").replace("_", "\_")
