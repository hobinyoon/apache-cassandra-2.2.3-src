# Tested with gnuplot 4.6 patchlevel 6

# Tablet min/max timestamps
FN_IN_TS = system("echo $FN_IN_TS")
# Tablet access counts
FN_IN_AC = system("echo $FN_IN_AC")
FN_OUT = system("echo $FN_OUT")
MAX_NUM_ACCESSES = system("echo $MAX_NUM_ACCESSES")
MIN_TIMESTAMP_RANGE = system("echo $MIN_TIMESTAMP_RANGE")
DESC = system("echo $DESC")

set xdata time
set ydata time
set timefmt "%y%m%d-%H%M%S"

# boxxyerrorbars parameters
#   x  y  xlow  xhigh  ylow  yhigh

# time data arithmetic doesn't work. label y-cord data needed to be generated with python.

# Get the plot range
set terminal unknown
plot \
FN_IN_TS u 2:6:2:5:6:7:1 w boxxyerrorbars, \
FN_IN_TS u 2:8:1:1 w labels right offset -0.5,0
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

set format x "'%y"
set format y "'%y"

# Give some margin on the left and at the bottom
x0=X_MIN-(365.25/12*1.3*24*3600)
x1=X_MAX+(365.25/12*0.5*24*3600)
y0=Y_MIN - (365.25/12*0.5*24*3600)
y1=Y_MAX
set xrange [x0:x1]
set yrange [y0:y1]

set key top left font ",8"

set samples 1000

load "../conf/colorscheme.gnuplot"

x1p = (X_MAX - X_MIN) / 100
y1p = (Y_MAX - Y_MIN) / 100

# Desc
x_1 = X_MIN
y_1 = Y_MAX - 3*y1p
set label DESC at x_1, y_1 left tc rgb "black" font ",7"

# Legend
x0 = X_MIN + 5*x1p
x1 = x0 + 10*x1p
y1 = y_1 - 15*y1p
y0 = y1 - 15*y1p
set object rect from x0, y0 to x1, y1 fc rgb "black" fs transparent solid 0.05 noborder
set arrow from x0, y0 to x0, y1 lc rgb "black" nohead
set arrow from x0, y1 to x1, y1 lc rgb "black" nohead

y2 = y0 - 6*y1p
set arrow from x0, y0 to x0, y2 lt 0 lc rgb "black" nohead
set arrow from x1, y0 to x1, y2 lt 0 lc rgb "black" nohead

y3 = y2 - 3*y1p
set label "created" at x0, y3 center tc rgb "black" font ",8"
set label "deleted" at x1, y3 center tc rgb "black" font ",8"

x2 = x1 + 3*x1p
set arrow from x1, y0 to x2, y0 lt 0 lc rgb "black" nohead
set arrow from x1, y1 to x2, y1 lt 0 lc rgb "black" nohead

x3 = x2 + x1p
set label "max timestamp" at x3, y1 left tc rgb "black" font ",8"
set label "min timestamp" at x3, y0 left tc rgb "black" font ",8"

set label "sst gen" at x0, (y0 + y1) / 2 right offset -0.5, 0 tc rgb "black" font ",8"

legendAccesses(x) = (x0 < x) && (x < x1) ? \
										y0 + (y1 - y0) * (1 - sin((x - x0) / (x1 - x0) * pi / 2)) + sin(x / (x1 - x0) * pi * 20) * 0.5*y1p \
										: 1 / 0

x5 = x0 + 5*x1p
x6 = x1 + 6*x1p
y4 = (y0 + y1) / 2
set arrow from x5, y4 to x6, y4 lt 0 lc rgb "black" nohead

x7 = x6 + x1p
set label "# of accesses" at x7, y4 left tc rgb "black" font ",8"

x8 = x7 + 12*x1p
y5 = y4 - MIN_TIMESTAMP_RANGE / 2.0
y6 = y4 + MIN_TIMESTAMP_RANGE / 2.0
set arrow from x8, y5 to x8, y6 lc rgb "black" nohead
set arrow from x8 - 0.2*x1p, y5 to x8 + 0.2*x1p, y5 lc rgb "black" nohead
set arrow from x8 - 0.2*x1p, y6 to x8 + 0.2*x1p, y6 lc rgb "black" nohead
set label "0"              at x8, y5 left offset 0.4,0 tc rgb "black" font ",7"
set label MAX_NUM_ACCESSES at x8, y6 left offset 0.4,0 tc rgb "black" font ",7"

# gnuplot doesn't have a mod function
#   http://www.macs.hw.ac.uk/~ml355/lore/gnuplot.htm
mod(a, b) = a - floor(a/b) * b
color(a) = mod(a, 6)

set style fill transparent solid 0.10 noborder

plot \
FN_IN_TS u 2:6:2:5:6:7:(color($1)) w boxxyerrorbars linecolor variable not, \
FN_IN_TS u 2:6:(0):9:(color($1)) w vectors nohead linecolor variable not, \
FN_IN_TS u 2:7:10:(0):(color($1)) w vectors nohead linecolor variable not, \
FN_IN_TS u 2:8:1:(color($1)) w labels right offset -0.5,0 textcolor variable font ",8" not, \
legendAccesses(x) w lines lc rgb "black" not, \
FN_IN_AC u 2:8:(color($1)) w lines lc variable not # "# of accesses"

# "vectors" doesn't have dotted line... dang
#FN_IN_TS u 4:6:(0):9:(color($1)) w vectors nohead linecolor variable lt -1 not, \

# 3rd and 4th columns of "vectors" takes number, not date format... dang.
#FN_IN_TS u 2:6:(0):9:(color($1)) w vectors nohead linecolor variable not, \

# steps doesn't work with lc variable... dang
#FN_IN_AC u 2:8:(color($1)) w steps linecolor variable t "# of accesses"
