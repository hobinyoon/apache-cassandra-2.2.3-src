# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

# Get the plot range
set terminal unknown
set xdata time
set timefmt "%y%m%d-%H%M%S"
plot \
FN_IN u 2:6:2:4:6:($6+$5) w boxxyerrorbars
X_MIN=GPVAL_DATA_X_MIN
X_MAX=GPVAL_DATA_X_MAX
Y_MIN=GPVAL_DATA_Y_MIN
Y_MAX=GPVAL_DATA_Y_MAX

set terminal pdfcairo enhanced size 12in, 4in
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

set xrange [X_MIN:X_MAX]
set yrange [Y_MIN:Y_MAX]

set key top left

set style fill solid 0.15 noborder

# x  y  xlow  xhigh  ylow  yhigh
plot \
FN_IN u 2:6:2:4:6:($6+$5) w boxxyerrorbars not, \
""    u 2:6:(0):5         w vectors nohead lc rgb "red"  t "Created", \
""    u 2:($6+$5/2.0):1   w labels right offset -0.5,0 font ",10" not
