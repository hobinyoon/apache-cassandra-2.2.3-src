# Tested with gnuplot 4.6 patchlevel 6

# Tablet min/max timestamps
FN_IN_TS = system("echo $FN_IN_TS")
# Tablet access counts
FN_IN_AC = system("echo $FN_IN_AC")
FN_OUT = system("echo $FN_OUT")
MAX_NUM_ACCESSES = system("echo $MAX_NUM_ACCESSES")
MIN_TIMESTAMP_RANGE = system("echo $MIN_TIMESTAMP_RANGE")
DESC = system("echo $DESC")

load "../conf/colorscheme.gnuplot"

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

x1p = (X_MAX - X_MIN) / 100
y1p = (Y_MAX - Y_MIN) / 100

# Give some margin on the left and at the bottom
x0=X_MIN - 3*x1p
x1=X_MAX + 2*x1p
y0=Y_MIN - y1p
y1=Y_MAX
set xrange [x0:x1]
set yrange [y0:y1]

set key top left font ",8"

set samples 5000

# Desc
x0 = X_MIN - x1p
y0 = Y_MAX - 3*y1p
DESC = DESC \
. "\n" \
. "\nOE: Open Early" \
. "\nON: Open Normal" \
. "\nTM0: Temperature monitor start" \
. "\nTM1: Temperature monitor stop" \
. "\nBC: Become cold"
set label DESC at x0, y0 left tc rgb "black" font ",7"

# Legend
x1 = X_MIN + 40*x1p
x2 = x1 + 10*x1p
y1 = Y_MAX - 6*y1p
y0 = y1 - 15*y1p
set object rect from x1, y0 to x2, y1 fc rgb "black" fs transparent solid 0.05 noborder
set arrow from x1, y0 to x1, y1 lc rgb "black" nohead
#set arrow from x1, y1 to x2, y1 lc rgb "black" nohead

y3 = y0 - 6*y1p
set arrow from x1, y0 to x1, y3 lt 0 lc rgb "black" nohead
set arrow from x2, y0 to x2, y3 lt 0 lc rgb "black" nohead

y4 = y3 - 3*y1p
set label "created" at x1, y4 center tc rgb "black" font ",8"
set label "deleted" at x2, y4 center tc rgb "black" font ",8"

x3 = x2 + 3*x1p
set arrow from x2, y0 to x3, y0 lt 0 lc rgb "black" nohead
set arrow from x2, y1 to x3, y1 lt 0 lc rgb "black" nohead

x4 = x3 + x1p
set label "max timestamp" at x4, y1 left tc rgb "black" font ",8"
set label "min timestamp" at x4, y0 left tc rgb "black" font ",8"

y2 = (y0 + y1)/2 + y1p
set label "sst\ngen" at x1, y2 right offset -0.5, 0 tc rgb "black" font ",8"

legendAccesses(x) = (x1 < x) && (x < x2) && (sin(x / (x2 - x1) * pi * 150) > 0) ? \
										y0 + (y1 - y0) * (1 - sin((x - x1) / (x2 - x1) * pi / 2)) + sin(x / (x2 - x1) * pi * 20) * 0.5*y1p \
										: 1 / 0

x6 = x1 + 8*x1p
x7 = x2 + 8*x1p
y5 = (y0 + y1) / 2
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
FN_IN_TS u 2:6:2:5:6:7:(color($1)) w boxxyerrorbars lc variable not, \
FN_IN_TS u 2:6:(0):9:(color($1)) w vectors nohead lc variable not, \
FN_IN_TS u 2:8:1:(color($1)) w labels right offset -0.5,0 textcolor variable font ",8" not, \
legendAccesses(x) w lines lc rgb "black" not, \
FN_IN_TS u 11:7:(0):(-y1p) w vectors nohead lc rgb "black" not, \
FN_IN_TS u 12:7:(0):(-y1p) w vectors nohead lc rgb "black" not, \
FN_IN_TS u 13:7:(0):(-y1p) w vectors nohead lc rgb "black" not, \
FN_IN_TS u 14:7:(0):(-y1p) w vectors nohead lc rgb "black" not, \
FN_IN_TS u 15:7:(0):(-y1p) w vectors nohead lc rgb "black" not, \
FN_IN_TS u 11:7:("OE")  w labels tc rgb "black" rotate by 90 right offset 0,-0.4 font ",7" not, \
FN_IN_TS u 12:7:("ON")  w labels tc rgb "black" rotate by 90 left  offset 0, 0.2 font ",7" not, \
FN_IN_TS u 13:7:("TM0") w labels tc rgb "black" rotate by 90 right offset 0,-0.4 font ",7" not, \
FN_IN_TS u 14:7:("BC")  w labels tc rgb "black" rotate by 90 left  offset 0, 0.2 font ",7" not, \
FN_IN_TS u 15:7:("TM1") w labels tc rgb "black" rotate by 90 right offset 0,-0.4 font ",7" not, \
FN_IN_AC u 2:9:(color($1)) w points pointsize 0.05 lc variable not # "# of accesses"

# "vectors" doesn't have dotted line... dang
#FN_IN_TS u 4:6:(0):9:(color($1)) w vectors nohead lc variable lt -1 not, \

# 3rd and 4th columns of "vectors" takes number, not date format... dang.
#FN_IN_TS u 2:6:(0):9:(color($1)) w vectors nohead lc variable not, \

# steps doesn't work with lc variable... dang
#FN_IN_AC u 2:8:(color($1)) w steps lc variable t "# of accesses"
