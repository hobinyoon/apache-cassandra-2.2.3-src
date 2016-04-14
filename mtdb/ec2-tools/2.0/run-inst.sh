#!/bin/bash

ec2-run-instances \
	ami-1fc7d575 \
	--region us-east-1 \
	--availability-zone us-east-1d \
	--instance-count 2 \
	--group cass-server \
	--ebs-optimized \
	--instance-type c3.2xlarge \
	--user-data-file userdata-helloworld

# --region REGION
# 		Specify REGION as the web service region to use.
# 		This option will override the URL specified by the "-U URL" option
# 		and EC2_URL environment variable.
# 		This option defaults to the region specified by the EC2_URL environment variable
# 		or us-east-1 if this environment variable is not set.
#
# -z, --availability-zone ZONE
# 		Specifies the availability zone to launch the instance(s) in. Run the
# 		'ec2-describe-availability-zones' command for a list of values, and
# 		see the latest Developer's Guide for their meanings.
#
# -n, --instance-count MIN[-MAX]
# 		The number of instances to attempt to launch. May be specified as a
# 		single integer or as a range (min-max). This specifies the minimum
# 		and maximum number of instances to attempt to launch. If a single
# 		integer is specified min and max are both set to that value.
#
# -g, --group GROUP [--group GROUP...]
# 		Specifies the security group (or groups if specified multiple times)
# 		within which the instance(s) should be run. Determines the ingress
# 		firewall rules that will be applied to the launched instances.
# 		Defaults to the user's default group if not supplied.
# #	  Here, they want a group name, not a group ID like sg-67d1330a. Interesting.
#
# --ebs-optimized
# 		Provides dedicated throughput to Amazon EBS and a software
# 		stack optimized for EBS I/O. Additional usage charges apply
# 		when using this option.
#
# -t, --instance-type TYPE
# 		Specifies the type of instance to be launched. Refer to the latest
# 		Developer's Guide for valid values.
#
# -f, --user-data-file DATA-FILE
# 		Specifies the file containing user data to be made available to the
# 		instance(s) in this reservation.
