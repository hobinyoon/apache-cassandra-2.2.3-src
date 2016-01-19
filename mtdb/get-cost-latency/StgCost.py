import datetime


# $ / GB / Month
INST_STORE=0.5103

EBS_SSD   =0.1

def InstStore(size_bytes, time_secs):
	# datetime.timedelta time_secs
	return INST_STORE * size_bytes * 0.000000001 * time_secs.total_seconds() / (365.25 / 12 * 24 * 3600)
	#                                  123456789

def EbsSsd(size_bytes, time_secs):
	return EBS_SSD    * size_bytes * 0.000000001 * time_secs.total_seconds() / (365.25 / 12 * 24 * 3600)
	#                                  123456789
