#!/bin/bash

ec2-run-instances \
	ami-1fc7d575 \
	--region us-east-1 \
	--instance-count 1 \
	--group cass-server \
	--ebs-optimized \
	--instance-type r3.xlarge \
	-b "/dev/sdc=:1638:true:gp2"

#	-b "/dev/sdc=:16384:true:gp2"
# 16384 didn't work. 1638 worked. Hmm. It is only in a specific zone?

#	--instance-type c3.2xlarge \

# seems like the default value (when not specified) of encrypted is false

#     -b, --block-device-mapping MAPPING
#          Defines a block device mapping for the image, in the form
#          '<device>=<block-device>', where 'block-device' can be one of the
#          following:
#          
#           - 'none': indicates that a block device that would be exposed at the
#             specified device should be suppressed. For example: '/dev/sdb=none'
#          
#           - 'ephemeral[0-3]': indicates that the Amazon EC2 ephemeral store
#             (instance local storage) should be exposed at the specified device.
#             For example: '/dev/sdc=ephemeral0'.
#          
#           - '[<snapshot-id>][:<size>[:<delete-on-termination>][:<type>[:<iops>]][:encrypted]]': indicates
#             that an Amazon EBS volume, created from the specified Amazon EBS
#             snapshot, should be exposed at the specified device. The following
#             combinations are supported:
#          
#              - '<snapshot-id>': the ID of an Amazon EBS snapshot, which must
#                be owned by the caller. May be left out if a <size> is
#                specified, creating an empty Amazon EBS volume of the specified
#                size.
#          
#              - '<size>': the size (GiBs) of the Amazon EBS volume to be
#                created. If a snapshot was specified, this may not be smaller
#                than the size of the snapshot itself.
#          
#              - '<delete-on-termination>': indicates whether the Amazon EBS
#                volume should be deleted on instance termination. If not
#                specified, this will default to 'true' and the volume will be
#                deleted.
#          
#              - '<type>': specifies the volume type. This can be either
#                'gp2', 'io1' or 'standard'. Defaults to standard.
#          
#              - '<iops>': The requested number of I/O operations per
#                second that the volume can support. Only valid for io1
#                volumes.
#          
#              - 'encrypted': Indicates that the volume should be encrypted.
#          
#             For example: '/dev/sdb=snap-7eb96d16'
#                          '/dev/sdc=snap-7eb96d16:80:false'
#                          '/dev/sdc=snap-7eb96d16:80:false:io1:100'
	
#	ami-1fc7d575 (mutants-server) \
#--availability-zone us-east-1d \
#	--user-data-file userdata-helloworld

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
