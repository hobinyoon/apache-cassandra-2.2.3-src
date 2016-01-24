# Tested with gnuplot 4.6 patchlevel 6

# Tablet created/deleted events
FN_IN_CD = system("echo $FN_IN_CD")
# Tablet access counts
FN_IN_AC = system("echo $FN_IN_AC")
FN_OUT = system("echo $FN_OUT")

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

set terminal pdfcairo enhanced rounded size 12in, 4in
set output FN_OUT

set border (1) front lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080"
unset ytics

set format x "'%y"

# Give some margin on the left and at the bottom
X_MIN1=X_MIN-(365.25/12*1.3*24*3600)
X_MAX=X_MAX+(365.25/12*0.5*24*3600)
Y_MIN=-(5*1024*1024)

set xrange [X_MIN1:X_MAX]
set yrange [Y_MIN:Y_MAX]

set key top left

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
x0 = X_MIN + (365.25/12*0.7*24*3600)
y0 = Y_MIN + (Y_MAX - Y_MIN) * 0.7
_10MB = 10*1024*1024
y1 = y0 + _10MB
y2 = y1 + _10MB
set arrow from x0, y0 to x0, y1 lw 2 lc rgb "black" heads size graph 0.0013,90
set label "0"     at x0,y0 offset 0.8,0 tc rgb "black" font ",10"
set label "10 MB" at x0,y1 offset 0.8,0 tc rgb "black" font ",10"
set label "Tablet size"       at x0,y2 offset -0.5,0.3 tc rgb "black"

# Legend: Access count
y0 = Y_MIN + (Y_MAX - Y_MIN) * 0.5
y1 = y0 + AccessCountHeight(AC_MAX)
y2 = y1 + _10MB
set arrow from x0, y0 to x0, y1 lw 2 lc rgb "red" heads size graph 0.0013,90
set label "0"                   at x0,y0 offset 0.8,0 tc rgb "red" font ",10"
set label sprintf("%d", AC_MAX) at x0,y1 offset 0.8,0 tc rgb "red" font ",10"
set label "# of accesses (in log scale)" at x0,y2 offset -0.5,0.3 tc rgb "black"

set style fill solid 0.02 noborder

# x  y  xlow  xhigh  ylow  yhigh
plot \
FN_IN_CD u 2:7:2:5:7:($7+$6) w boxxyerrorbars lc rgb "blue" not, \
FN_IN_AC u 3:2:($2 + AccessCountHeight($6+$7)) w filledcurves lc rgb "red" not, \
FN_IN_AC u 3:($2 + AccessCountHeight($6+$7)) w steps lc rgb "red" t "# of accesses", \
FN_IN_CD u 2:7:(0):6         w vectors nohead lw 2 lt 1 lc rgb "black" t "Created", \
FN_IN_CD u 4:7:(0):6         w vectors nohead lw 2 lt 0 lc rgb "black" t "Deleted", \
FN_IN_CD u 2:($7+$6/2.0):1   w labels right offset -0.5,0 font ",10" not

# This doesn't fill the exact same area as the steps, but was the closest thing
# that I can find.
#FN_IN_AC u 3:2:($2 + AccessCountHeight($6+$7)) w filledcurves lc rgb "red" not, \

#FN_IN_AC u 3:($2 + AccessCountHeight($6+$7)) w linespoints pt 7 pointsize 0.1 lc rgb "black" not, \

# no base y option, like y0
#FN_IN_AC u 3:($2 + AccessCountHeight($6+$7)) w fillsteps lc rgb "red" not, \
