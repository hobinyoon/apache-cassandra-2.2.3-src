CREATE KEYSPACE demo
WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

USE demo;

CREATE TABLE users (
firstname text,
lastname text,
age int,
email text,
city text,
PRIMARY KEY (lastname));
