# Tested with gnuplot 4.6 patchlevel 6

# Tablet created/deleted events
FN_IN_CD = system("echo $FN_IN_CD")
# Tablet access counts
FN_IN_AC = system("echo $FN_IN_AC")
FN_OUT = system("echo $FN_OUT")
DESC = system("echo $DESC")

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
FN_IN_AC u 3:($6+$7) w points
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
y0=Y_MIN
y1=Y_MAX-(5*1024*1024)

set xrange [x0:x1]
set yrange [y0:y1]

set key top left

x1p = (X_MAX - X_MIN) / 100
y1p = (Y_MAX - Y_MIN) / 100

# Desc
x0 = X_MIN
y0 = Y_MAX - 3*y1p
set label DESC at x0, y0 left tc rgb "black" font ",7"

# Linear scale
#AccessCountHeight(x) = x*40000

# Log scale
#   value range
#     x              : [0, AC_MAX]
#     +1             : [1, AC_MAX+1]
#     log(above)     : [0(=log(1)), log(AC_MAX+1)]
#     / log(AC_MAX+1) : [0, 1]
AccessCountHeight(x)=(log(x+1)/log(AC_MAX+1))*10000000

# Legend: Tablet size
xx0 = X_MIN
yy0 = Y_MIN + (Y_MAX - Y_MIN) * 0.6
_10MB = 10*1024*1024
y1 = yy0 + _10MB
y2 = y1 + _10MB
set arrow from xx0, yy0 to xx0, y1 lw 2 lc rgb "black" heads size graph 0.0013,90
set label "0"     at xx0,yy0 offset 0.8,0 tc rgb "black" font ",8"
set label "10 MB" at xx0,y1 offset 0.8,0 tc rgb "black" font ",8"
set label "Tablet size"       at xx0,y2 offset -0.5,0.3 tc rgb "black" font ",8"

# Legend: Access count
yy0 = Y_MIN + (Y_MAX - Y_MIN) * 0.5
y1 = yy0 + AccessCountHeight(AC_MAX)
y2 = y1 + _10MB
set arrow from xx0, yy0 to xx0, y1 lw 2 lc rgb "red" heads size graph 0.0013,90
set label "0"                   at xx0,yy0 offset 0.8,0 tc rgb "red" font ",7"
set label sprintf("%d", AC_MAX) at xx0,y1 offset 0.8,0 tc rgb "red" font ",7"
set label "# of accesses (in log scale)" at xx0,y2 offset -0.5,0.3 tc rgb "black" font ",8"

set style fill solid 0.06 noborder

# x  y  xlow  xhigh  ylow  yhigh
plot \
FN_IN_CD u 2:7:2:5:7:($7+$6) w boxxyerrorbars lc rgb "blue" not, \
FN_IN_AC u 3:2:($2 + AccessCountHeight($6+$7)) w filledcurves lc rgb "red" not, \
FN_IN_AC u 3:($2 + AccessCountHeight($6+$7)) w steps lc rgb "red" not, \
FN_IN_CD u 2:7:(0):6         w vectors nohead lw 2 lt 1 lc rgb "black" not, \
FN_IN_CD u 4:7:(0):6         w vectors nohead lw 2 lt 0 lc rgb "black" not, \
FN_IN_CD u 2:($7+$6/2.0):1   w labels right offset -0.5,0 font ",8" not

# This doesn't fill the exact same area as the steps, but was the closest thing
# that I can find.
#FN_IN_AC u 3:2:($2 + AccessCountHeight($6+$7)) w filledcurves lc rgb "red" not, \

#FN_IN_AC u 3:($2 + AccessCountHeight($6+$7)) w linespoints pt 7 pointsize 0.1 lc rgb "black" not, \

# no base y option, like y0
#FN_IN_AC u 3:($2 + AccessCountHeight($6+$7)) w fillsteps lc rgb "red" not, \
