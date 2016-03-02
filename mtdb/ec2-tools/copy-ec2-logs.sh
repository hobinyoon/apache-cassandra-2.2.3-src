# EC2 Servers
declare -a ec2s=(
23.22.13.183
23.22.38.77
54.197.159.32
184.73.58.105
54.161.196.221
54.211.16.110
54.144.232.33
54.211.146.69
54.197.108.12
54.167.151.65
)

for ip in "${ec2s[@]}"; do
	echo "${ip}"
	# Ignore fingerprint validation
	#   http://stackoverflow.com/questions/20816547/stricthostkeychecking-not-ignoring-fingerprint-validation
	rsync -ave "ssh -o StrictHostKeyChecking=no" ubuntu@${ip}:work/cassandra/mtdb/logs ~/work/cassandra/mtdb/
done
