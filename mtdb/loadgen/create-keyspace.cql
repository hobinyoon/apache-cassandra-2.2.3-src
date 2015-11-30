DROP KEYSPACE IF EXISTS mtdb1;

CREATE KEYSPACE mtdb1
WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

USE mtdb1;

CREATE TABLE users (
		key int,
		C0 text,
		PRIMARY KEY (key));
