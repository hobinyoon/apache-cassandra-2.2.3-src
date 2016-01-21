# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

# Get min and max values
set terminal unknown

set xdata time
set timefmt "%y%m%d-%H%M%S"
set format x "'%y"

plot FN_IN u 2:($5/1000000) w fsteps
X_MIN=GPVAL_DATA_X_MIN
X_MAX=GPVAL_DATA_X_MAX
Y_MIN=GPVAL_DATA_Y_MIN
Y_MAX=GPVAL_DATA_Y_MAX

set terminal pdfcairo enhanced size 3in, 2in
set output FN_OUT

#set tmargin at screen 0.975
#set bmargin at screen 0.152
#set lmargin at screen 0.185
#set rmargin at screen 0.940

set xlabel "Time (year)" offset 0,0.3
set ylabel "Storage size (MB)" offset 1.3,0

set border (1 + 2) lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080"
set ytics nomirror scale 0.5,0 tc rgb "#808080"
set tics front

X_MAX="180101-120000.000000"
set xrange [X_MIN:X_MAX]
set yrange [Y_MIN:Y_MAX]

plot \
FN_IN u 2:($5/1000000) w fillsteps fs solid 0.15 noborder not, \
FN_IN u 2:($5/1000000) w steps lw 0.1 lc rgb "red" not
