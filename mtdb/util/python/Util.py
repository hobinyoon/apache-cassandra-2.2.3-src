import errno
import os
import pprint
import re
import sys
import time


_ind = 0

class MeasureTime:
	def __init__(self, msg, indent = 0):
		self.msg = msg
		self.indent = indent
		global _ind
		_ind += indent

	def __enter__(self):
		self.start_time = time.time()
		IndPrint(self.msg)
		global _ind
		_ind += 2
		return self

	def __exit__(self, type, value, traceback):
		dur = time.time() - self.start_time
		IndPrint("%.0f ms" % (dur * 1000.0))
		global _ind
		_ind -= 2

	def GetMs(self):
		return (time.time() - self.start_time) * 1000.0


# TODO: may want to use regex replace
def Indent(s0, ind):
	spaces = ""
	for i in range(ind):
		spaces += " "

	o = ""
	tokens = s0.split("\n")
	first = True
	for t in tokens:
		if len(t) == 0:
			continue
		if first == True:
			first = False
		else:
			o += "\n"
		o += spaces
		o += t
	return o


def IndPrint(s0, ind = 0):
	# Thread-safely is not considered
	global _ind
	_ind += ind
	print Indent(s0, _ind)


def BuildHeader(fmt, desc):
	name_end_pos = []
	#print fmt
	# Float, integer, or string
	nep = 0
	for m in re.findall(r"%(([-+]?[0-9]*\.?[0-9]*f)|([-+]?[0-9]*d)|([-+]?[0-9]*s))", fmt):
		#print m[0]
		# Take only the leading number part. Python int() is not as forgiving as C atoi().
		m1 = re.search(r"([1-9][0-9]*)", m[0])
		if nep != 0:
			nep += 1
		nep += int(m1.group(0))
		#print nep
		name_end_pos.append(nep)
	#IndPrint("name_end_pos: %s" % name_end_pos)

	names_flat = "# %s\n" % desc
	names_flat += "#\n"
	names = desc.split()
	#IndPrint("names: %s" % names)

	# Header lines
	lines = []
	for i in range(len(names)):
		fits = False

		for j in range(len(lines)):
			if len(lines[j]) + 1 + len(names[i]) > name_end_pos[i]:
				continue

			while len(lines[j]) + 1 + len(names[i]) < name_end_pos[i]:
				lines[j] += " "
			lines[j] += (" " + names[i])
			fits = True
			break

		if fits:
			continue

		l = "#"
		while len(l) + 1 + len(names[i]) < name_end_pos[i]:
			l += " "
		l += (" " + names[i])
		lines.append(l)

	# Indices for names starting from 1 for easy gnuplot indexing
	ilines = []
	for i in range(len(names)):
		idxstr = str(i + 1)
		fits = False
		for j in range(len(ilines)):
			if len(ilines[j]) + 1 + len(idxstr) > name_end_pos[i]:
				continue

			while len(ilines[j]) + 1 + len(idxstr) < name_end_pos[i]:
				ilines[j] += " "
			ilines[j] += (" " + idxstr)
			fits = True
			break

		if fits:
			continue

		l = "#"
		while len(l) + 1 + len(idxstr) < name_end_pos[i]:
			l += " "
		l += (" " + idxstr)
		ilines.append(l)

	header = ""
	#header = names_flat
	for l in lines:
		header += (l + "\n")
	for l in ilines:
		header += (l + "\n")
	return header


def MkDirs(path):
	try:
		os.makedirs(path)
	except OSError as exc: # Python >2.5
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else:
			raise
