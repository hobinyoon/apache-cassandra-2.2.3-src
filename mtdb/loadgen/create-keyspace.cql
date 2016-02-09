DROP KEYSPACE IF EXISTS mtdb1;

CREATE KEYSPACE mtdb1
WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

USE mtdb1;

CREATE TABLE table1 (
		key int,
		epoch_sec int,
		C0 blob,
		PRIMARY KEY (key)
		)
	WITH compression = { 'sstable_compression' : '' }
	AND compaction = {'class' : 'DateTieredCompactionStrategy'
		, 'base_time_seconds' : 5
	}
	;
--	AND compaction = {'class' : 'DateTieredCompactionStrategy'}
--	AND compaction = {'class' : 'LeveledCompactionStrategy'}
--	AND compaction = {'class' : 'SizeTieredCompactionStrategy'
--		, 'min_threshold' : 1000
--			, 'max_threshold' : 1000
--	}
