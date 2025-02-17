pi_user="pi"
pi_addr="10.142.155.18"
ip_range="3 4 6 7 9 10 12 13 15 16"
to_null="2> /dev/null"
bold=$(tput bold)
normal=$(tput sgr0)

# Send argument by ssh to raspberry
# 	(str) arg1: ssh command, ie: "rm -rf directory"
# 	(str) arg2: ip address subfix, ie: "13" for 192.168.3.13, or range, ie:  "12 15 9"
# 	(str) arg3: timeout in seconds
#
# 	If only arg1 is specified, send command for all raspberry in default range
if [ -z "$3" ]; then
	timeout=""
else
	timeout="-o ConnectTimeout="$3
fi

if [ -z "$1" ]; then # arg1 is null, not argument supplied, command to send needed
    echo "No argument supplied, command to send by ssh needed"
else
	if [ ! -z "$2" ]; then # arg2 is provided, change ip_range, arg2 is not null
		ip_range=$2
		to_null=""
	fi
		# Send the command to each Raspberry in ip_range
	  for i in $ip_range; do
			ip=`printf "%02d" $i` # zero fill ip address subfix
			printf "${bold}Sending to Raspi-"$ip"\n${normal}"
			ssh -t $timeout -p 22$ip $pi_user@$pi_addr $1 $to_null
		done
			printf "Done.\n"
fi


