# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

## Get min and max values
##   GPVAL_DATA_[X|Y]_[MIN|MAX]
#set terminal unknown
#plot \
#FN_IN u 6:2:($4-$6):(0) with vectors not

set terminal pdfcairo enhanced size 3in, 2in
set output FN_OUT

#set tmargin at screen 0.975
#set bmargin at screen 0.152
#set lmargin at screen 0.185
#set rmargin at screen 0.940

set xlabel "Timestamp (min, max)" offset 0,0.3
set ylabel "SStable gen ID" offset 1.6,0

set border (1 + 2) back lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080" #rotate by -90
set ytics nomirror scale 0.5,0 tc rgb "#808080"

set timefmt "%Y-%m-%d-%H:%M:%S"
set xdata time
#set format x "%H:%M:%S"
set format x ":%S"

set style arrow 8 heads back nofilled lc rgb "#FF0000" size screen 0.004,90.000,90.000

plot \
FN_IN u 2:1:($4/1000000):(0) with vectors arrowstyle 8 not

#X_RANGE=GPVAL_DATA_X_MAX-GPVAL_DATA_X_MIN
#print X_RANGE
#plot \
#FN_IN u (($6-GPVAL_DATA_X_MIN)/X_RANGE):2:(($4-$6)/X_RANGE):(0) with vectors arrowstyle 8 not
