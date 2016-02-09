import pprint
import sys


class ParseError(RuntimeError):
	def __init__(self, i):
		self.i = i

	def __str__(self):
		return "_i=%d _line_until_error=[%s]" % (self.i, _line[0:self.i])


_line = None
_i = 0

# List is another type of map, i.e.,
#   db={requests=true, num_threads=500}
# It is weird, but should be fine for now.
def NewList():
	global _line, _i
	curMap = {}
	key = None
	value = None
	state = "ParsingKey"
	while _i < len(_line):
		c = _line[_i]
		#print "list: %s " % c
		if c == "[":
			if key == None:
				raise ParseError(_i)
			if value != None:
				raise ParseError(_i)
			if state != "ParsingValue":
				raise ParseError(_i)
			# Begin a child map
			_i += 1
			value = NewMap()
		elif c == "]":
			raise ParseError(_i)
		elif c == "{":
			# key can be None. There is a weird one like [{a=b}]
			#if key == None:
			#	raise ParseError(_i)
			if value != None:
				raise ParseError(_i)
			if state != "ParsingValue":
				raise ParseError(_i)
			# Begin a child list
			_i += 1
			value = NewList()
		elif c == "}":
			# End of the current list
			if key == None:
				raise ParseError(_i)
			if state != "ParsingValue":
				raise ParseError(_i)
			curMap[key] = value
			#key = None
			#value = None
			#state = "ParsingKey"
			_i += 1
			#print "New list:"
			#pprint.pprint(curMap, indent=2)
			return curMap
		elif c == ",":
			# List item delimiter
			_i += 1
			c1 = _line[_i]
			if c1 != " ":
				raise ParseError(_i)
			_i += 1
			curMap[key] = value
			key = None
			value = None
			state = "ParsingKey"
		elif c == "=":
			state = "ParsingValue"
			_i += 1
		else:
			# Parse map key or value
			if state == "ParsingKey":
				if key == None:
					key = c
				else:
					key += c
			else:
				if value == None:
					value = c
				else:
					try:
						value += c
					except TypeError as e:
						print "Exception: _i=%d _line_until_exception=[%s] value=[%s] c=[%s]" % (_i, _line[0:_i], value, c)
						raise e
			_i += 1


def NewMap():
	global _line, _i
	curMap = {}
	key = None
	value = None
	state = "ParsingKey"
	while _i < len(_line):
		c = _line[_i]
		#print "map: %s " % c
		#pprint.pprint(curMap)
		if c == "[":
			if key == None:
				raise ParseError(_i)
			if value != None:
				raise ParseError(_i)
			if state != "ParsingValue":
				raise ParseError(_i)
			# Begin a child map
			_i += 1
			value = NewMap()
		elif c == "]":
			# End of the current map
			#if key == None:
			#	raise ParseError(_i)
			#if state != "ParsingValue":
			#	raise ParseError(_i)
			curMap[key] = value
			#key = None
			#value = None
			#state = "ParsingKey"
			_i += 1
			#print "New map:"
			#pprint.pprint(curMap, indent=2)
			return curMap
		elif c == "{":
			# key can be None. There is a weird one like [{a=b}]
			#if key == None:
			#	raise ParseError(_i)
			if value != None:
				raise ParseError(_i)
			#if state != "ParsingValue":
			#	raise ParseError(_i)
			# Begin a child list
			_i += 1
			value = NewList()
		elif c == "}":
			raise ParseError(_i)
		elif c == ";":
			# Map item delimiter
			_i += 1
			c1 = _line[_i]
			if c1 != " ":
				raise ParseError(_i)
			_i += 1
			curMap[key] = value
			key = None
			value = None
			state = "ParsingKey"
		elif c == "=":
			state = "ParsingValue"
			_i += 1
		else:
			# Parse map key or value
			if state == "ParsingKey":
				if key == None:
					key = c
				else:
					key += c
			else:
				if value == None:
					value = c
				else:
					value += c
			_i += 1


def Parse(line):
	global _line, _i
	_line = line
	#Cons.P(_line)
	global _i
	# Expect the top level as a Map
	if _line[0] != "[":
		raise ParseError(_i)
	_i = 1
	root = NewMap()
	return root


def Test():
	# root = Parse("[]")

	# root = Parse("[authenticator=AllowAllAuthenticator]")
	# root = Parse("[authenticator=AllowAllAuthenticator; write_request_timeout_in_ms=2000; client_encryption_options=<REDACTED>; db={requests=true, num_threads=500}]")
	# root = Parse("[db={requests=true, num_threads=500}]")

	# root = Parse("[mutants_loadgen_options={global={num_writes_per_simulation_time_mins=20000, write_time_dist=Uniform}, per_obj={avg_reads=1000, num_reads_dist=Custom: facebook-num-reqs-by-rank, read_time_dist=Custom: facebook-num-reads-by-age, obj_size=3000}, db={requests=true, num_threads=500}}]")

	root = Parse("[authenticator=AllowAllAuthenticator; authorizer=AllowAllAuthorizer; auto_snapshot=true; batch_size_fail_threshold_in_kb=50; batch_size_warn_threshold_in_kb=5; batchlog_replay_throttle_in_kb=1024; cas_contention_timeout_in_ms=1000; client_encryption_options=<REDACTED>; cluster_name=Test Cluster; column_index_size_in_kb=64; commit_failure_policy=stop; commitlog_segment_size_in_mb=32; commitlog_sync=periodic; commitlog_sync_period_in_ms=10000; compaction_large_partition_warning_threshold_mb=100; compaction_throughput_mb_per_sec=16; concurrent_counter_writes=32; concurrent_reads=32; concurrent_writes=32; counter_cache_save_period=7200; counter_cache_size_in_mb=null; counter_write_request_timeout_in_ms=5000; cross_node_timeout=false; disk_failure_policy=stop; dynamic_snitch_badness_threshold=0.1; dynamic_snitch_reset_interval_in_ms=600000; dynamic_snitch_update_interval_in_ms=100; enable_user_defined_functions=false; endpoint_snitch=SimpleSnitch; hinted_handoff_enabled=true; hinted_handoff_throttle_in_kb=1024; incremental_backups=false; index_summary_capacity_in_mb=null; index_summary_resize_interval_in_minutes=60; inter_dc_tcp_nodelay=false; internode_compression=all; key_cache_save_period=14400; key_cache_size_in_mb=null; listen_address=localhost; max_hint_window_in_ms=10800000; max_hints_delivery_threads=2; memtable_allocation_type=heap_buffers; memtable_heap_space_in_mb=32; memtable_offheap_space_in_mb=32; mutants_loadgen_options={global={num_writes_per_simulation_time_mins=20000, write_time_dist=Uniform}, per_obj={avg_reads=1000, num_reads_dist=Custom: facebook-num-reqs-by-rank, read_time_dist=Custom: facebook-num-reads-by-age, obj_size=3000}, db={requests=true, num_threads=500}}; mutants_options={simulated_time_years=8, simulation_time_mins=0.5, tablet_temperature_monitor_interval_simulation_time_ms=100, cold_storage_dir=/mnt/s5-cass-cold-storage/mtdb-cold, tablet_coldness_monitor_time_window_simulated_time_days=45, tablet_coldness_threshold=0.05, tablet_access_stat_report_interval_simulation_time_ms=100}; native_transport_port=9042; num_tokens=256; partitioner=org.apache.cassandra.dht.Murmur3Partitioner; permissions_validity_in_ms=2000; range_request_timeout_in_ms=10000; read_request_timeout_in_ms=5000; request_scheduler=org.apache.cassandra.scheduler.NoScheduler; request_timeout_in_ms=10000; role_manager=CassandraRoleManager; roles_validity_in_ms=2000; row_cache_save_period=0; row_cache_size_in_mb=0; rpc_address=localhost; rpc_keepalive=true; rpc_port=9160; rpc_server_type=sync; seed_provider=[{class_name=org.apache.cassandra.locator.SimpleSeedProvider, parameters=[{seeds=127.0.0.1}]}]; server_encryption_options=<REDACTED>; snapshot_before_compaction=false; ssl_storage_port=7001; sstable_preemptive_open_interval_in_mb=50; start_native_transport=true; start_rpc=false; storage_port=7000; thrift_framed_transport_size_in_mb=15; tombstone_failure_threshold=100000; tombstone_warn_threshold=1000; tracetype_query_ttl=86400; tracetype_repair_ttl=604800; trickle_fsync=false; trickle_fsync_interval_in_kb=10240; truncate_request_timeout_in_ms=60000; windows_timer_interval=1; write_request_timeout_in_ms=2000]")
	pprint.pprint(root, indent=2)
