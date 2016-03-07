import math
import os
import subprocess
import sys

sys.path.insert(0, "../../util/python")
import Cons

import Conf
import ExpData


def Plot():
	with Cons.MeasureTime("Plotting ..."):
		for expg in Conf.Get():
			_Cost(expg)


def _Cost(expg):
	fn_in = "plot-data/cost.%s" % expg
	fn_out = fn_in + ".pdf"

	env = os.environ.copy()
	env["FN_IN"] = fn_in
	env["FN_OUT"] = fn_out

	cost_hot = ExpData.MaxTotalCost(expg)
	cost_mutants = ExpData.MutantsTotalCost(expg)
	env["cost_hot"] = str(cost_hot)
	env["cost_mutants"] = str(cost_mutants)

	y_max = ExpData.MaxTotalCost(expg) * 1.15
	env["Y_MAX"] = str(y_max)
	env["Y_TICS_INTERVAL"] = str(_TicsInterval(y_max))

	_RunSubp("gnuplot %s/cost-3way.gnuplot" % os.path.dirname(__file__), env)
	Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def _RunSubp(cmd, env_, print_cmd=False):
	if print_cmd:
		Cons.P(cmd)
	p = subprocess.Popen(cmd, shell=True, env=env_, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	# communidate() waits for termination
	stdouterr = p.communicate()[0]
	rc = p.returncode
	if rc != 0:
		raise RuntimeError("Error: cmd=[%s] rc=%d stdouterr=[%s]" % (cmd, rc, stdouterr))
	if len(stdouterr) > 0:
		Cons.P(stdouterr)


def _TicsInterval(v_max):
	# Get most-significant digit
	# 1 -> 0.5 : 2 tic marks
	# 2 -> 1   : 2 tic marks
	# 3 -> 1   : 3 tic marks
	# 4 -> 2   : 2 tic marks
	# 5 -> 2   : 2 tic marks
	# 6 -> 2   : 3 tic marks
	# 7 -> 2   : 3 tic marks
	# 8 -> 2   : 4 tic marks
	# 9 -> 2   : 4 tic marks
	a = [0.5, 1, 1, 2, 2, 2, 2, 4, 2]

	v_max = float(v_max)
	v = v_max
	if v >= 1.0:
		v_prev = v
		while v >= 1.0:
			v_prev = v
			v /= 10.0
		msd = int(v_prev)
	else:
		while v < 1.0:
			v *= 10.0
		msd = int(v)

	base = math.pow(10, math.floor(math.log10(v_max)))
	ti = a[msd - 1] * base
	return ti
