#!/bin/bash

declare -a SERVER_IPS=()
declare -a CLIENT_IPS=()

load_server_ips() {
	while IFS='' read -r line || [[ -n "$line" ]]; do
		ip=${line}
		SERVER_IPS+=(${ip})
	done < server-list

	#for ip in "${SERVER_IPS[@]}"; do
	#	echo ${ip}
	#done
}

load_client_ips() {
	while IFS='' read -r line || [[ -n "$line" ]]; do
		ip=${line}
		CLIENT_IPS+=(${ip})
	done < client-list

	#for ip in "${CLIENT_IPS[@]}"; do
	#	echo ${ip}
	#done
}

edit_server_bashrc() {
	i=0
	for ip in "${SERVER_IPS[@]}"; do
		s_ip=${SERVER_IPS[${i}]}
		c_ip=${CLIENT_IPS[${i}]}
		cmd="echo 'export CASSANDRA_CLIENT_ADDR="${c_ip}"' >> ~/.bashrc"
		printf "%s\n" ${s_ip}
		echo "  "${cmd}
		ssh -o StrictHostKeyChecking=no ubuntu@${s_ip} "${cmd}"

		i=$((i+1))
	done
}

edit_client_bashrc() {
	i=0
	for ip in "${SERVER_IPS[@]}"; do
		s_ip=${SERVER_IPS[${i}]}
		c_ip=${CLIENT_IPS[${i}]}
		cmd="echo 'export CASSANDRA_SERVER_ADDR="${s_ip}"' >> ~/.bashrc"
		printf "%s\n" ${c_ip}
		echo "  "${cmd}
		ssh -o StrictHostKeyChecking=no ubuntu@${c_ip} "${cmd}"

		i=$((i+1))
	done
}

load_server_ips
load_client_ips

edit_server_bashrc
edit_client_bashrc
