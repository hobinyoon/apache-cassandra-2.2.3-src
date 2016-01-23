# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

# Get the plot range
set terminal unknown
set xdata time
set timefmt "%y%m%d-%H%M%S"
plot \
FN_IN u 2:7:2:5:7:($7+$6) w boxxyerrorbars
X_MIN=GPVAL_DATA_X_MIN
X_MAX=GPVAL_DATA_X_MAX
Y_MIN=GPVAL_DATA_Y_MIN
Y_MAX=GPVAL_DATA_Y_MAX

set terminal pdfcairo enhanced rounded size 12in, 4in
set output FN_OUT

set ylabel "Size (MB)" offset 2,0

set border (1 + 2) front lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080"
set ytics nomirror scale 0.5,0 tc rgb "#808080" ( \
"0"   0, \
"50"  50*1024*1024, \
"100" 100*1024*1024)
set tics front

set xdata time
set timefmt "%y%m%d-%H%M%S"
set format x "'%y"

# Give some margin on the left and at the bottom
X_MIN=X_MIN-(365.25/12*1.3*24*3600)
X_MAX=X_MAX+(365.25/12*0.5*24*3600)
Y_MIN=-(5*1024*1024)

set xrange [X_MIN:X_MAX]
set yrange [Y_MIN:Y_MAX]

set key top left

set style fill solid 0.08 noborder

# x  y  xlow  xhigh  ylow  yhigh
plot \
FN_IN u 2:7:2:5:7:($7+$6) w boxxyerrorbars not, \
""    u 2:7:(0):6         w vectors nohead lw 3 lc rgb "red"  t "Created", \
""    u 4:7:(0):6         w vectors nohead lw 3 lc rgb "blue" t "Deleted", \
""    u 2:($7+$6/2.0):1   w labels right offset -0.5,0 font ",10" not
