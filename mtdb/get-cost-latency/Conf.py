import argparse

args = None

def Init():
	# https://docs.python.org/2/library/argparse.html#module-argparse
	parser = argparse.ArgumentParser(description="Process experiment logs of MTDB loadgen and Cassandra")
	parser.add_argument('exp_datetime', type=str, default=None, nargs='?',
			help='experiment datetime')
	parser.add_argument("--print_cost_by_time", action='store_true',
			help="Print cost by time")

	global args
	args = parser.parse_args()
	#print args
