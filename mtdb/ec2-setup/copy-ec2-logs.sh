s0=54.204.71.226
s1=54.145.133.12
s2=54.166.92.110
s3=54.197.124.158
s4=54.167.170.49

rsync -av ubuntu@$s0:work/cassandra/mtdb/logs ~/work/cassandra/mtdb/
rsync -av ubuntu@$s1:work/cassandra/mtdb/logs ~/work/cassandra/mtdb/
rsync -av ubuntu@$s2:work/cassandra/mtdb/logs ~/work/cassandra/mtdb/
rsync -av ubuntu@$s3:work/cassandra/mtdb/logs ~/work/cassandra/mtdb/
rsync -av ubuntu@$s4:work/cassandra/mtdb/logs ~/work/cassandra/mtdb/
