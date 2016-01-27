# Tested with gnuplot 4.6 patchlevel 6

# Tablet created/deleted events
FN_IN_CD = system("echo $FN_IN_CD")
# Tablet access counts
FN_IN_AC = system("echo $FN_IN_AC")
FN_OUT = system("echo $FN_OUT")
DESC = system("echo $DESC")

load "../conf/colorscheme.gnuplot"

# Get the plot range
set terminal unknown
set xdata time
set timefmt "%y%m%d-%H%M%S"
plot \
FN_IN_CD u 2:7:2:5:7:($7+$6) w boxxyerrorbars
X_MIN=GPVAL_DATA_X_MIN
X_MAX=GPVAL_DATA_X_MAX
Y_MIN=GPVAL_DATA_Y_MIN
Y_MAX=GPVAL_DATA_Y_MAX

# Get AC_MAX, access count max
set terminal unknown
plot \
FN_IN_AC u 3:6 w points
AC_MAX=GPVAL_DATA_Y_MAX
set print "-"
print sprintf("Max access count of all tablets: %d", AC_MAX)

set terminal pdfcairo enhanced rounded size 6, 3in
set output FN_OUT

set border (1) front lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,(365.25*24*3600)
unset ytics

set format x "'%y"

# Give some margin on the left and at the bottom
x0=X_MIN-(365.25/12*1.3*24*3600)
x1=X_MAX+(365.25/12*0.5*24*3600)
y0=Y_MIN-(5*1024*1024)
y1=Y_MAX

set xrange [x0:x1]
set yrange [y0:y1]

set key top left

x1p = (X_MAX - X_MIN) / 100
y1p = (Y_MAX - Y_MIN) / 100

# Desc
x0 = X_MIN
y0 = Y_MAX - 3*y1p
set label DESC at x0, y0 left tc rgb "black" font ",7"

TRANSP0=0.06

# Legend
x1 = X_MIN + 11.5*x1p
x2 = x1 + 7*x1p
y2 = y0 - 15*y1p
y1 = y2 - 10*y1p
set object rect from x1, y1 to x2, y2 fc rgb "black" fs transparent solid TRANSP0 noborder
set arrow from x1, y1 to x1, y2 lc rgb "black" nohead

y3 = (y2 + y1) / 2
y4 = y3 + 1.5*y1p
set label "sst\ngen" at x1, y4 right offset -0.5, 0 tc rgb "black" font ",8"

x3 = x1 - 5*x1p
set arrow from x3, y1 to x3, y2 lc rgb "black" nohead

set arrow from x3 - 0.2*x1p, y2 to x3 + 0.2*x1p, y2 lc rgb "black" nohead
set arrow from x3 - 0.2*x1p, y1 to x3 + 0.2*x1p, y1 lc rgb "black" nohead

set label (sprintf("%d MB", (y2 - y1)/1024/1024)) at x3, y2 right offset -0.5, 0 tc rgb "black" font ",8"
set label "0"                                     at x3, y1 right offset -0.5, 0 tc rgb "black" font ",8"

x4 = x3 - 6.5*x1p
set label "Tablet size" at x4, y3 center rotate by 90 tc rgb "black" font ",8"

y4 = y1 - 4*y1p
set arrow from x1, y1 to x1, y4 lt 0 lc rgb "black" nohead
set arrow from x2, y1 to x2, y4 lt 0 lc rgb "black" nohead

y5 = y4 - 2*y1p
set label "created" at x1, y5 center tc rgb "black" font ",8"
set label "deleted" at x2, y5 center tc rgb "black" font ",8"


legendAccesses(x) = (x1 < x) && (x < x2) && (sin(x / (x2 - x1) * pi * 150) > 0) ? \
										y1 + (y2 - y1) * cos((x - x1) / (x2 - x1) * pi / 2) + sin(x / (x2 - x1) * pi * 20) * 0.5*y1p \
										: 1 / 0

x5 = x1 + 5.5*x1p
x6 = x2 + 2*x1p
set arrow from x5, y3 to x6, y3 lt 0 lc rgb "black" nohead

x7 = x6 + x1p
y6 = y3 + 2*y1p
set label "# of accesses\nper day" at x7, y6 left tc rgb "black" font ",8"

# Log scale
#   value range
#     x              : [0, AC_MAX]
#     +1             : [1, AC_MAX+1]
#     log(above)     : [0(=log(1)), log(AC_MAX+1)]
#     / log(AC_MAX+1) : [0, 1]
AccessCountHeight(x) = x == 0 ? \
											 1/0 \
											 : (log(x+1)/log(AC_MAX+1))*10000000

x8 = x7 + 11*x1p
y7 = y3 - AccessCountHeight(AC_MAX) / 2.0
y8 = y3 + AccessCountHeight(AC_MAX) / 2.0
set arrow from x8, y7 to x8, y8 lc rgb "red" nohead
set arrow from x8 - 0.2*x1p, y7 to x8 + 0.2*x1p, y7 lc rgb "red" nohead
set arrow from x8 - 0.2*x1p, y8 to x8 + 0.2*x1p, y8 lc rgb "red" nohead
set label (sprintf("%d", AC_MAX)) at x8, y8 left offset 0.4, 0.1 tc rgb "red" font ",7"
set label "0"                     at x8, y7 left offset 0.4,-0.1 tc rgb "red" font ",7"

set samples 5000

# gnuplot doesn't have a mod function
#   http://www.macs.hw.ac.uk/~ml355/lore/gnuplot.htm
mod(a, b) = a - floor(a/b) * b

color(a) = mod(a, 6)

set style fill solid TRANSP0 noborder

# x  y  xlow  xhigh  ylow  yhigh
plot \
FN_IN_CD u 2:7:2:5:7:($7+$6):(color($1)) w boxxyerrorbars lc variable not, \
FN_IN_AC u 3:($2 + AccessCountHeight($6)):(color($1)) w points pointsize 0.01 lc variable not, \
FN_IN_CD u 2:7:(0):6:(color($1)) w vectors nohead      lt 1 lc variable not, \
FN_IN_CD u 2:($7+$6/2.0):1:(color($1)) w labels right offset -0.5,0 font ",8" tc variable not, \
legendAccesses(x) w lines lc rgb "black" not

# dotted line doesn't work with lc variable
#FN_IN_CD u 4:7:(0):6:(color($1)) w vectors nohead lw 2 lt 0 lc variable not, \

# steps doesn't work with lc variable
#FN_IN_AC u 3:($2 + AccessCountHeight($6)):(color($1)) w steps lc variable not, \
#FN_IN_AC u 3:2:($2 + AccessCountHeight($6)):(color($1)) w filledcurves lc variable not, \

# This doesn't fill the exact same area as the steps, but was the closest thing
# that I can find.
#FN_IN_AC u 3:2:($2 + AccessCountHeight($6)) w filledcurves lc rgb "red" not, \

#FN_IN_AC u 3:($2 + AccessCountHeight($6)) w linespoints pt 7 pointsize 0.1 lc rgb "black" not, \

# no base y option, like y0
#FN_IN_AC u 3:($2 + AccessCountHeight($6)) w fillsteps lc rgb "red" not, \
