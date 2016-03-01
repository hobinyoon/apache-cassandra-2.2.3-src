# EC2 Servers

# May want to use a separate configuration file later

# Server IPs
declare -a s_ips=(
54.204.181.71
54.159.233.173
54.161.229.124
54.144.192.247
54.92.250.154
54.167.175.25
54.204.226.200
54.158.180.253
54.166.59.107
54.211.121.32
54.159.237.249
54.204.166.140
)

declare -a c_ips=(
52.91.205.141
52.90.87.73
52.90.52.102
52.91.210.175
52.87.161.125
52.87.161.198
52.91.69.148
52.91.211.40
52.87.161.65
52.90.64.191
52.87.164.240
52.23.167.165
)

set_hostname() {
	i=0
	for ip in "${s_ips[@]}"; do
		# hostname
		hn=ec2-s${i}-c3.2xlarge-29

		cmd="sudo sed -i 's/localhost$/localhost '$hn'/g' /etc/hosts \
			&& sudo bash -c 'echo '$hn' > /etc/hostname' \
			&& sudo hostname --file /etc/hostname"

		#printf "%s %s [%s]\n" ${ip} ${hn} "${cmd}"
		printf "%s %s\n" ${ip} ${hn}
		ssh -o StrictHostKeyChecking=no ubuntu@${ip} "${cmd}"

		i=$((i+1))
	done

	i=0
	for ip in "${c_ips[@]}"; do
		# hostname
		hn=ec2-s${i}-m4.large-29

		cmd="sudo sed -i 's/localhost$/localhost '$hn'/g' /etc/hosts \
			&& sudo bash -c 'echo '$hn' > /etc/hostname' \
			&& sudo hostname --file /etc/hostname"

		#printf "%s %s [%s]\n" ${ip} ${hn} "${cmd}"
		printf "%s %s\n" ${ip} ${hn}
		ssh -o StrictHostKeyChecking=no ubuntu@${ip} "${cmd}"

		i=$((i+1))
	done
}

set_hostname
