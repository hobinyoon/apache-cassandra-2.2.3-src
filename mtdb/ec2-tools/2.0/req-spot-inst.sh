#!/bin/bash

ec2-request-spot-instances \
	ami-1fc7d575 \
	--region us-east-1 \
	--price 1.0 \
	--availability-zone us-east-1d \
	--instance-count 2 \
	--group cass-server \
	--ebs-optimized \
	--type one-time \
	--instance-type c3.2xlarge \
	--user-data-file userdata-helloworld

# --price PRICE
# Specifies the maximum hourly price for any spot instance launched to
# fulfill the request.
#
# -z, --availability-zone ZONE
# Specifies the availability zone to launch the instance(s) in. Run the
# 'ec2-describe-availability-zones' command for a list of values, and
# see the latest Developer's Guide for their meanings.
#
# -n, --instance-count COUNT
# The maximum number of spot instances to launch.
#
# --ebs-optimized
# Provides dedicated throughput to Amazon EBS and a software
# stack optimized for EBS I/O. Additional usage charges apply
# when using this option.
#
# -r, --type REQUEST
# Specified the spot instance request type; either 'one-time' or
# 'persistent'.
#
# -t, --instance-type TYPE
# Specifies the type of instance to be launched. Refer to the latest
# Developer's Guide for valid values.
#
# -g, --group GROUP [--group GROUP...]
# Specifies the security group (or groups if specified multiple times)
# within which the instance(s) should be run. Determines the ingress
# firewall rules that will be applied to the launched instances.
# Defaults to the user's default group if not supplied.
#	  Here, they want a group name, not a group ID like sg-67d1330a. Interesting.
#
# -D, --auth-dry-run
# Check if you can perform the requested action rather than actually performing it.
#
# c3.2xlarge
# Compute optimized 8 vCPUs, 15 GiB memory, 2 x 80 GB SSD, Network performance: High

# Example:
#   hobin@mts7:~/work/cassandra/mtdb/ec2-tools/2.0$ ./launch-inst.sh
#   SPOTINSTANCEREQUEST	sir-029h551a	1.000000	one-time	Linux/UNIX	open	2016-04-14T16:42:20-0400						ami-1fc7d575	c3.2xlarge		sg-d0b9cab9	us-east-1d			monitoring-disabled			
#   SPOTINSTANCESTATUS	pending-evaluation	2016-04-14T16:42:20-0400	Your Spot request has been submitted for review, and is pending evaluation.
#   SPOTINSTANCEREQUEST	sir-029kf0mc	1.000000	one-time	Linux/UNIX	open	2016-04-14T16:42:20-0400						ami-1fc7d575	c3.2xlarge		sg-d0b9cab9	us-east-1d			monitoring-disabled			
#   SPOTINSTANCESTATUS	pending-evaluation	2016-04-14T16:42:20-0400	Your Spot request has been submitted for review, and is pending evaluation.

# $ ec2-describe-spot-instance-requests
# SPOTINSTANCEREQUEST	sir-029h551a	1.000000	one-time	Linux/UNIX	active	2016-04-14T16:42:20-0400					i-941ace13	ami-1fc7d575	c3.2xlarge		sg-d0b9cab9	us-east-1d			monitoring-disabled		us-east-1d	
# SPOTINSTANCESTATUS	fulfilled	2016-04-14T16:43:02-0400	Your Spot request is fulfilled.
# SPOTINSTANCEREQUEST	sir-029kf0mc	1.000000	one-time	Linux/UNIX	active	2016-04-14T16:42:20-0400					i-3d1aceba	ami-1fc7d575	c3.2xlarge		sg-d0b9cab9	us-east-1d			monitoring-disabled		us-east-1d	
# SPOTINSTANCESTATUS	fulfilled	2016-04-14T16:43:02-0400	Your Spot request is fulfilled.

# $ ./ec2-describe-instances
# RESERVATION	r-64070cb6	998754746880	default
# INSTANCE	i-3d1aceba	ami-1fc7d575	ec2-54-160-170-177.compute-1.amazonaws.com	ip-10-13-198-12.ec2.internal	running		0		c3.2xlarge	2016-04-14T20:43:02+0000	us-east-1d				monitoring-disabled	54.160.170.177	10.13.198.12			ebs	spot	sir-029kf0mc		hvm	xen	4149c7ae-0738-4c39-90c0-da33c69968be	sg-d0b9cab9	default	true	
# BLOCKDEVICE	/dev/sda1	vol-da9fd372	2016-04-14T20:43:03.000Z	true		
# RESERVATION	r-6a060db8	998754746880	default
# INSTANCE	i-941ace13	ami-1fc7d575	ec2-54-227-1-182.compute-1.amazonaws.com	ip-10-180-48-246.ec2.internal	running		0		c3.2xlarge	2016-04-14T20:43:02+0000	us-east-1d				monitoring-disabled	54.227.1.182	10.180.48.246			ebs	spot	sir-029h551a		hvm	xen	c8353db3-d50a-4c8b-baf3-ed56905f41a4	sg-d0b9cab9	default	true	
# BLOCKDEVICE	/dev/sda1	vol-aa9fd302	2016-04-14T20:43:02.000Z	true
