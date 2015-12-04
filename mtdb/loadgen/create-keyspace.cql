DROP KEYSPACE IF EXISTS mtdb1;

CREATE KEYSPACE mtdb1
WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

USE mtdb1;

CREATE TABLE table1 (
		key int,
		epoch_sec int,
		C0 text,
		PRIMARY KEY (key));
