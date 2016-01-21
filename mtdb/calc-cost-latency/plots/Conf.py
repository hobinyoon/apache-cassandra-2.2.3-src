import argparse

args = None

def Init():
	# https://docs.python.org/2/library/argparse.html#module-argparse
	parser = argparse.ArgumentParser(description="Plot MTDB latency")
	parser.add_argument('exp_datetime', type=str, default=None, nargs='?',
			help='experiment datetime')

	global args
	args = parser.parse_args()
	#print args
