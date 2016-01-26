# Tested with gnuplot 4.6 patchlevel 6

# Tablet created/deleted events
FN_IN = system("echo $FN_IN")
# Tablet access counts
FN_IN_AC = system("echo $FN_IN_AC")
FN_OUT = system("echo $FN_OUT")

set xdata time
set ydata time
set timefmt "%y%m%d-%H%M%S"

set format x "'%y"
set format y "'%y"

# boxxyerrorbars parameters
#   x  y  xlow  xhigh  ylow  yhigh

# time data arithmetic doesn't work. label y-cord data needed to be generated with python.

# Get the plot range
set terminal unknown
plot \
FN_IN u 2:6:2:5:6:7:1 w boxxyerrorbars, \
FN_IN u 2:8:1:1 w labels right offset -0.5,0
X_MIN=GPVAL_DATA_X_MIN
X_MAX=GPVAL_DATA_X_MAX
Y_MIN=GPVAL_DATA_Y_MIN
Y_MAX=GPVAL_DATA_Y_MAX

set terminal pdfcairo enhanced rounded size 6in, 3in
set output FN_OUT

set xlabel "Time"
set ylabel "Tablet timestamp range"

set border (1+2) front lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,(365.25*24*3600)
set ytics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,(365.25*24*3600)

# Give some margin on the left and at the bottom
x0=X_MIN-(365.25/12*1.3*24*3600)
x1=X_MAX+(365.25/12*0.5*24*3600)
y0=Y_MIN - (365.25/12*0.5*24*3600)
y1=Y_MAX
set xrange [x0:x1]
set yrange [y0:y1]

set key top left

load "../conf/colorscheme.gnuplot"

set style fill transparent solid 0.05

# Legend
MONTH = 365.25/12*24*3600
x0 = X_MIN + 2.0 * MONTH
x1 = x0 + 4.0 * MONTH
y1 = Y_MAX - 1.0 * MONTH
y0 = y1 - 4.0 * MONTH
set object rect from x0, y0 to x1, y1 fc rgb "black" fs transparent solid 0.05 border lc rgb "#404040"

y2 = y0 - 2.0 * MONTH
set arrow from x0, y0 to x0, y2 lt 0 lc rgb "black" nohead
set arrow from x1, y0 to x1, y2 lt 0 lc rgb "black" nohead

y3 = y2 - 1.5 * MONTH
set label "created" at x0, y3 center tc rgb "black" font ",8"
set label "deleted" at x1, y3 center tc rgb "black" font ",8"

x2 = x1 + MONTH
set arrow from x1, y0 to x2, y0 lt 0 lc rgb "black" nohead
set arrow from x1, y1 to x2, y1 lt 0 lc rgb "black" nohead

x3 = x2 + 0.5 * MONTH
set label "max timestamp" at x3, y1 left tc rgb "black" font ",8"
set label "min timestamp" at x3, y0 left tc rgb "black" font ",8"

set label "sst gen" at x0, (y0 + y1) / 2 right offset -0.5, 0 tc rgb "black" font ",8"

# gnuplot doesn't have a mod function
#   http://www.macs.hw.ac.uk/~ml355/lore/gnuplot.htm
mod(a, b) = a - floor(a/b) * b
color(a) = mod(a, 6)

plot \
FN_IN u 2:6:2:5:6:7:(color($1)) w boxxyerrorbars linecolor variable not, \
FN_IN u 2:8:1:(color($1)) w labels right offset -0.5,0 textcolor variable font ",8" not
