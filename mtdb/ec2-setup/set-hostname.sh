# EC2 Servers

# May want to use a separate configuration file later

# Server IPs
declare -a s_ips=(
54.147.218.163
)

set_hostname() {
	i=0
	for ip in "${s_ips[@]}"; do
		# hostname
		hn=ec2-s${i}-c3.2xlarge-26

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
