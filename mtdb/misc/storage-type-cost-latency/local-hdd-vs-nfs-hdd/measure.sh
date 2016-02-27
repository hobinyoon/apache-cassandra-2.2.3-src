#!/bin/bash

HOSTNAME=`hostname`
DATETIME=`date +"%y%m%d-%H%M%S"`
echo $DATETIME

FN_PREFIX="data/"$HOSTNAME"."$DATETIME"."

DN_LOCAL_HDD=~
DN_NFS_HDD=/mnt/s5-cass-cold-storage

# HDD performance measured locally both on s7 and s5. They look about the same.
#
#   root@samoa7:~# pvs
#     PV         VG   Fmt  Attr PSize   PFree
#     /dev/sdb5  vg_0 lvm2 a--  136.49g 107.18g
#     /dev/sdc   vg1  lvm2 a--  931.51g 871.51g
#   root@samoa5:~# pvs
#     PV         VG   Fmt  Attr PSize   PFree
#     /dev/sdb1  vg0  lvm2 a--  136.73g 117.42g
#     /dev/sdc   vg1  lvm2 a--  931.51g 361.51g
#
#   root@samoa7:~# hdparm /dev/sdc
#     /dev/sdc:
#      multcount     =  0 (off)
#      readonly      =  0 (off)
#      readahead     = 256 (on)
#      geometry      = 121601/255/63, sectors = 1953525168, start = 0
#   root@samoa5:~# hdparm /dev/sdc
#     /dev/sdc:
#      multcount     =  0 (off)
#      readonly      =  0 (off)
#      readahead     = 256 (on)
#      geometry      = 121601/255/63, sectors = 1953525168, start = 0
#
#   root@samoa7:~# sudo hdparm -Tt /dev/sdc
#     /dev/sdc:
#      Timing cached reads:   11320 MB in  1.99 seconds = 5684.15 MB/sec
#      Timing buffered disk reads: 320 MB in  3.02 seconds = 106.06 MB/sec
#
#   root@samoa5:~# sudo hdparm -Tt /dev/sdc
#     /dev/sdc:
#      Timing cached reads:   11294 MB in  1.99 seconds = 5670.80 MB/sec
#      Timing buffered disk reads: 324 MB in  3.01 seconds = 107.50 MB/sec


gen_test_files() {
	# Create test files
	echo "Creating test files ..."
	time dd bs=1024 count=262144 < /dev/urandom > $DN_LOCAL_HDD/ioping-test
	time cp $DN_LOCAL_HDD/ioping-test $DN_NFS_HDD/ioping-test
}

# TODO: more like system load test of DAS and NAS
DN_OUTPUT=/run/ioping-test

mk_output_dir() {
	sudo mkdir $DN_OUTPUT \
	&& sudo chown hobin $DN_OUTPUT
}

# TODO: wanted to know the system load difference between when using DAS and NAS.

# A lot of kernel time, like 90%. I don't see any iowait time.
#   real 0m50.619s
#   user 0m 3.428s
#   sys  0m47.180s
test_4k_rand_read_cached_local_hdd() {
	FN_OUT=${DN_OUTPUT}/4k-rand-read-cached-local-hdd-${DATETIME}
	time ioping -Cq -c 10000000 -i 0 $DN_LOCAL_HDD/ioping-test > $FN_OUT
	printf "Created %s %d\n" $FN_OUT `wc -c < $FN_OUT`
}

# I see like a 100% of iowait time.
#   real 1m0.439s
#   user 0m0.004s
#   sys  0m1.136s
test_4k_rand_read_direct_local_hdd() {
	FN_OUT=${DN_OUTPUT}/4k-rand-read-direct-local-hdd-${DATETIME}
	time ioping -Dq -c 20000 -i 0 $DN_LOCAL_HDD/ioping-test > $FN_OUT
	printf "Created %s %d\n" $FN_OUT `wc -c < $FN_OUT`
}

# You can't control the caching behavior of the NFS server here.

# First run. Some iowait during the first 4 secs. After that like 90% of kernel time.
# Second run. More than 90% of kernel time.
#   real 0m54.045s
#   user 0m 3.720s
#   sys  0m50.320s
test_4k_rand_read_cached_nfs_hdd() {
	FN_OUT=${DN_OUTPUT}/4k-rand-read-cached-nfs-hdd-${DATETIME}
	time ioping -Cq -c 10000000 -i 0 $DN_NFS_HDD/ioping-test > $FN_OUT
	printf "Created %s %d\n" $FN_OUT `wc -c < $FN_OUT`
}

# I don't see any iowait, which agrees with what I wanted to get.
# Not sure if NFS test is the same as EBS test. Will have to do it directly against EBS.
#   real 0m10.428s
#   user 0m 0.000s
#   sys  0m 0.840s
test_4k_rand_read_direct_nfs_hdd() {
	FN_OUT=${DN_OUTPUT}/4k-rand-read-direct-nfs-hdd-${DATETIME}
	time ioping -Dq -c 20000 -i 0 $DN_NFS_HDD/ioping-test > $FN_OUT
	printf "Created %s %d\n" $FN_OUT `wc -c < $FN_OUT`
}

# TODO: Look for system overhead of iowait

#gen_test_files

#test_4k_rand_read_direct_local_hdd
#test_4k_rand_read_cached_local_hdd
#test_4k_rand_read_direct_nfs_hdd
#test_4k_rand_read_cached_nfs_hdd

# TODO: big sequential writes. It will be capped by the network bandwidth. How
# about iowait time?

# So, like 34% of kernel time. 66% of iowait time.
#   real 0m2.169s user 0m0.000s sys 0m0.748s
#   real 0m2.262s user 0m0.000s sys 0m0.752s
#   real 0m2.293s user 0m0.008s sys 0m0.724s
#   real 0m2.284s user 0m0.008s sys 0m0.704s
#   real 0m2.248s user 0m0.000s sys 0m0.728s
#   real 0m2.270s user 0m0.008s sys 0m0.740s
#   real 0m2.292s user 0m0.000s sys 0m0.740s
#   real 0m2.280s user 0m0.008s sys 0m0.716s
#   real 0m2.288s user 0m0.008s sys 0m0.728s
#   real 0m2.262s user 0m0.012s sys 0m0.740s
# Throughput:
#   2.10176 s, 128 MB/s
#   2.15654 s, 124 MB/s
#   2.20476 s, 122 MB/s
#   2.1997  s, 122 MB/s
#   2.15583 s, 125 MB/s
#   2.15461 s, 125 MB/s
#   2.17652 s, 123 MB/s
#   2.16075 s, 124 MB/s
#   2.17801 s, 123 MB/s
#   2.16068 s, 124 MB/s
test_256m_seq_write_local_hdd() {
	for ((i=0; i<10; i++)); do time dd bs=256M count=1 if=/dev/zero of=$DN_LOCAL_HDD/dd-test; done
}

# real 0m1.948s user 0m0.004s sys 0m0.348s
# real 0m1.893s user 0m0.000s sys 0m0.308s
# real 0m1.919s user 0m0.000s sys 0m0.288s
# real 0m1.912s user 0m0.000s sys 0m0.272s
# real 0m1.933s user 0m0.000s sys 0m0.260s
# real 0m1.919s user 0m0.000s sys 0m0.260s
# real 0m1.939s user 0m0.000s sys 0m0.296s
# real 0m1.897s user 0m0.000s sys 0m0.268s
# real 0m1.918s user 0m0.008s sys 0m0.252s
# real 0m1.883s user 0m0.000s sys 0m0.288s
# 
# Throughput:
#   1.87987 s, 143 MB/s
#   1.88499 s, 142 MB/s
#   1.91078 s, 140 MB/s
#   1.90514 s, 141 MB/s
#   1.92602 s, 139 MB/s
#   1.91126 s, 140 MB/s
#   1.9317  s, 139 MB/s
#   1.88987 s, 142 MB/s
#   1.91113 s, 140 MB/s
#   1.87621 s, 143 MB/s
#
# Direct IO skips the OS buffering of the writes, and puts them straight onto disk.
# - http://appsintheopen.com/posts/27-test-hard-disk-speed-with-dd
#
# Average (real - user - sys) time, which, I think, is the iowait time.
# - http://stackoverflow.com/questions/556405/what-do-real-user-and-sys-mean-in-the-output-of-time1
# Calculation from those two result sets shows about the same (?) performance.
# - Regular: 1.528 s
# - Direct:  1.631 s
#
test_256m_seq_write_direct_local_hdd() {
	for ((i=0; i<10; i++)); do time dd bs=256M count=1 oflag=direct if=/dev/zero of=$DN_LOCAL_HDD/dd-test; done
}

# real 0m2.855s user 0m0.000s sys 0m0.640s
# real 0m3.445s user 0m0.000s sys 0m0.632s
# real 0m3.251s user 0m0.000s sys 0m0.644s
# real 0m3.254s user 0m0.008s sys 0m0.600s
# real 0m3.118s user 0m0.000s sys 0m0.620s
# real 0m3.112s user 0m0.008s sys 0m0.640s
# real 0m3.125s user 0m0.000s sys 0m0.640s
# real 0m3.113s user 0m0.004s sys 0m0.648s
# real 0m3.146s user 0m0.008s sys 0m0.636s
#
# 2.75835 s, 97.3 MB/s
# 3.07446 s, 87.3 MB/s
# 2.76043 s, 97.2 MB/s
# 2.75623 s, 97.4 MB/s
# 2.75605 s, 97.4 MB/s
# 2.75851 s, 97.3 MB/s
# 2.76142 s, 97.2 MB/s
# 2.76182 s, 97.2 MB/s
# 2.76049 s, 97.2 MB/s
# 2.76012 s, 97.3 MB/s
#
# Capped by the network bandwidth, 1Gbps
#
# TODO: need to make a table and compare the iowait time or something.
test_256m_seq_write_nfs_hdd() {
	for ((i=0; i<10; i++)); do time dd bs=256M count=1 if=/dev/zero of=$DN_NFS_HDD/dd-test; done
}

# I don't see any iowait time here. Still, there is a decent amount of (real - user - sys) time.
# TODO: so the question should be, what's the difference between iowait and wait?
# And I guess the answer is wait is better. Even for the other jobs? CPU bound jobs?
# Scalability analysis? What's the io-load-vs-iowait curve like? Can you say
# the IO contention is really bad? Not scalable? This could explain the root cause.
# TODO: this argument should applys only to this one. The above one has quite a
# bit (like 1/3) of iowait time. Interesting.
#
# real 0m2.468s user 0m0.004s sys 0m0.180s
# real 0m2.807s user 0m0.000s sys 0m0.184s
# real 0m2.806s user 0m0.000s sys 0m0.192s
# real 0m2.796s user 0m0.000s sys 0m0.188s
# real 0m2.799s user 0m0.000s sys 0m0.188s
# real 0m2.798s user 0m0.000s sys 0m0.188s
# real 0m2.798s user 0m0.000s sys 0m0.192s
# real 0m2.799s user 0m0.008s sys 0m0.184s
# real 0m2.809s user 0m0.000s sys 0m0.192s
# real 0m2.941s user 0m0.004s sys 0m0.184s
#
# 2.457   s, 109 MB/s
# 2.45903 s, 109 MB/s
# 2.46174 s, 109 MB/s
# 2.45529 s, 109 MB/s
# 2.45613 s, 109 MB/s
# 2.45801 s, 109 MB/s
# 2.46138 s, 109 MB/s
# 2.45788 s, 109 MB/s
# 2.45805 s, 109 MB/s
# 2.45887 s, 109 MB/s
#
test_256m_seq_write_direct_nfs_hdd() {
	for ((i=0; i<10; i++)); do time dd bs=256M count=1 oflag=direct if=/dev/zero of=$DN_NFS_HDD/dd-test; done
}

# TODO: What I don't know is if EBS does any caching
# TODO: Look for NAS caching.

#test_256m_seq_write_local_hdd
#test_256m_seq_write_direct_local_hdd
test_256m_seq_write_nfs_hdd
#test_256m_seq_write_direct_nfs_hdd

# TODO: I will want to do this on SSDs too. I should. It should be what's interesting.

exit 0

# Memory file system. I don't see any iowait time. Good.
# $ for ((i=0; i<10; i++)); do time dd bs=256M count=1 if=/dev/zero of=/run/ioping-test/aa; done
#
# real 0m0.392s user 0m0.004s sys 0m0.384s
# real 0m0.390s user 0m0.000s sys 0m0.388s
# real 0m0.395s user 0m0.004s sys 0m0.392s
# real 0m0.390s user 0m0.004s sys 0m0.384s
# real 0m0.389s user 0m0.004s sys 0m0.388s
# real 0m0.396s user 0m0.004s sys 0m0.388s
# real 0m0.390s user 0m0.000s sys 0m0.388s
# real 0m0.390s user 0m0.000s sys 0m0.392s
# real 0m0.399s user 0m0.000s sys 0m0.396s
# real 0m0.390s user 0m0.004s sys 0m0.388s
#
# 0.352565 s, 761 MB/s
# 0.353787 s, 759 MB/s
# 0.355254 s, 756 MB/s
# 0.352771 s, 761 MB/s
# 0.352855 s, 761 MB/s
# 0.355424 s, 755 MB/s
# 0.35357  s, 759 MB/s
# 0.352679 s, 761 MB/s
# 0.35783  s, 750 MB/s
# 0.352901 s, 761 MB/s

# There's no direct IO to the memory file system.
#   dd bs=256M count=1 oflag=direct if=/dev/zero of=/run/ioping-test/aa
#     dd: failed to open ‘/run/ioping-test/aa’: Invalid argument


## TODO
## After this one, I will want to measure performance of below operations of AWS storages.
##
## - small random read
## - big   random read
## - small sequential read
## - big   sequential read
## - small random write
## - big   random write
## - small sequential write
## - big   sequential write
##
## It will give insights on what opportunities are there.

# TODO: by mixing some of those (including local and remote) I can probably
# identify interesting opportunities, like what I did with NoSQL databases.
