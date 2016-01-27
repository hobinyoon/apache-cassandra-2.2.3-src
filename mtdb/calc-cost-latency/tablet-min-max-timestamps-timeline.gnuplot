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

set samples 5000

load "../conf/colorscheme.gnuplot"

x1p = (X_MAX - X_MIN) / 100
y1p = (Y_MAX - Y_MIN) / 100

# Desc
x0 = X_MIN
y0 = Y_MAX - 3*y1p
set label DESC at x0, y0 left tc rgb "black" font ",7"

# Legend
x1 = X_MIN + 5*x1p
x2 = x1 + 10*x1p
y2 = y0 - 15*y1p
y0 = y2 - 15*y1p
set object rect from x1, y0 to x2, y2 fc rgb "black" fs transparent solid 0.05 noborder
set arrow from x1, y0 to x1, y2 lc rgb "black" nohead
#set arrow from x1, y2 to x2, y2 lc rgb "black" nohead

y3 = y0 - 6*y1p
set arrow from x1, y0 to x1, y3 lt 0 lc rgb "black" nohead
set arrow from x2, y0 to x2, y3 lt 0 lc rgb "black" nohead

y4 = y3 - 3*y1p
set label "created" at x1, y4 center tc rgb "black" font ",8"
set label "deleted" at x2, y4 center tc rgb "black" font ",8"

x3 = x2 + 3*x1p
set arrow from x2, y0 to x3, y0 lt 0 lc rgb "black" nohead
set arrow from x2, y2 to x3, y2 lt 0 lc rgb "black" nohead

x4 = x3 + x1p
set label "max timestamp" at x4, y2 left tc rgb "black" font ",8"
set label "min timestamp" at x4, y0 left tc rgb "black" font ",8"

set label "sst gen" at x1, (y0 + y2) / 2 right offset -0.5, 0 tc rgb "black" font ",8"

legendAccesses(x) = (x1 < x) && (x < x2) && (sin(x / (x2 - x1) * pi * 150) > 0) ? \
										y0 + (y2 - y0) * (1 - sin((x - x1) / (x2 - x1) * pi / 2)) + sin(x / (x2 - x1) * pi * 20) * 0.5*y1p \
										: 1 / 0

x6 = x1 + 5*x1p
x7 = x2 + 6*x1p
y5 = (y0 + y2) / 2
set arrow from x6, y5 to x7, y5 lt 0 lc rgb "black" nohead

x8 = x7 + x1p
y6 = y5 + 2*y1p
set label "# of accesses\nper day" at x8, y6 left tc rgb "black" font ",8"

x9 = x8 + 12*x1p
y7 = y5 - MIN_TIMESTAMP_RANGE / 2.0
y8 = y5 + MIN_TIMESTAMP_RANGE / 2.0
set arrow from x9, y7 to x9, y8 lc rgb "black" nohead
set arrow from x9 - 0.2*x1p, y7 to x9 + 0.2*x1p, y7 lc rgb "black" nohead
set arrow from x9 - 0.2*x1p, y8 to x9 + 0.2*x1p, y8 lc rgb "black" nohead
set label "0"              at x9, y7 left offset 0.4,0 tc rgb "black" font ",7"
set label MAX_NUM_ACCESSES at x9, y8 left offset 0.4,0 tc rgb "black" font ",7"

# gnuplot doesn't have a mod function
#   http://www.macs.hw.ac.uk/~ml355/lore/gnuplot.htm
mod(a, b) = a - floor(a/b) * b

color(a) = mod(a, 6)

set style fill transparent solid 0.10 noborder

plot \
FN_IN_TS u 2:6:2:5:6:7:(color($1)) w boxxyerrorbars linecolor variable not, \
FN_IN_TS u 2:6:(0):9:(color($1)) w vectors nohead linecolor variable not, \
FN_IN_TS u 2:8:1:(color($1)) w labels right offset -0.5,0 textcolor variable font ",8" not, \
legendAccesses(x) w lines lc rgb "black" not, \
FN_IN_AC u 2:8:(color($1)) w points pointsize 0.01 lc variable not # "# of accesses"

# "vectors" doesn't have dotted line... dang
#FN_IN_TS u 4:6:(0):9:(color($1)) w vectors nohead linecolor variable lt -1 not, \

# 3rd and 4th columns of "vectors" takes number, not date format... dang.
#FN_IN_TS u 2:6:(0):9:(color($1)) w vectors nohead linecolor variable not, \

# steps doesn't work with lc variable... dang
#FN_IN_AC u 2:8:(color($1)) w steps linecolor variable t "# of accesses"
