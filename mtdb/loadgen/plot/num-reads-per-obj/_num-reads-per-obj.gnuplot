# Tested with gnuplot 4.6 patchlevel 4

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

# To get the y range
set terminal unknown
plot FN_IN u 1:0 w lines not
Y_MIN=GPVAL_DATA_Y_MIN
Y_MAX=GPVAL_DATA_Y_MAX

set terminal pdfcairo enhanced size 3in, 2in
set output FN_OUT

set xlabel "num reads per obj"
set ylabel "CDF"

set border (1 + 2) lc rgb "#808080" back
set ytics nomirror scale 0.5,0 tc rgb "#808080" format "%0.1f" autofreq 0,0.5,1
set xtics nomirror scale 0.5,0 tc rgb "#808080" (1, 200, 400, 600, 800)

plot \
FN_IN u 1:($0/(Y_MAX - Y_MIN + 1)) w lines not
