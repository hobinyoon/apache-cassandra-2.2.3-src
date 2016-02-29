import os
import subprocess
import sys

sys.path.insert(0, "../../util/python")
import Cons

import PlotData


def Plot():
	with Cons.MeasureTime("Plotting storage cost and latency ..."):
		fn_in = PlotData._fn_plot_data
		fn_out = fn_in + ".pdf"
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out
# TODO
		#env["Y0"] = str(CompareCost._cass.cost_total)
		#env["Y1"] = str(CompareCost._mutants.cost_total)
		Util.RunSubp("gnuplot %s/cost-latency.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))
