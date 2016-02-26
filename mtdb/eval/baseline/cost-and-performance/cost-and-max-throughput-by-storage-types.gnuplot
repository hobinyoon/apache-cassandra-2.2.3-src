# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

## Get min and max values
##   GPVAL_DATA_[X|Y]_[MIN|MAX]
#set terminal unknown
#set xdata time
#set timefmt "%Y-%m-%d-%H:%M:%S"
#plot \
#FN_IN u 2:3 w points not

set terminal pdfcairo enhanced size 2in, 1.5in
set output FN_OUT

set tmargin at screen 0.970
set bmargin at screen 0.220
set lmargin at screen 0.240
set rmargin at screen 0.915

set border (1+2) back lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,500
set ytics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,2
set tics front

set xlabel "Cost ($/month)"              offset 0  ,0.5
set ylabel "Max throughput\n(K IOs/sec)" offset 1.7,0

set xrange [0:]
set yrange [0:]

COST_OTHER=401.3691667

set linetype 1 lc rgb "blue"
set linetype 2 lc rgb "#a52a2a"
set linetype 3 lc rgb "red"

set label "EBS\nMag"   at (COST_OTHER +  80), (4135.49/1000) center offset 0  ,-1   tc rgb "blue"
set label "EBS\nSSD"   at (COST_OTHER + 160), (8036.78/1000) center offset 2.1,-0.8 tc rgb "#a52a2a"
set label "Local\nSSD" at (COST_OTHER + 844), (9870.73/1000) center offset 0  ,-1   tc rgb "red"

plot \
FN_IN u ($2+COST_OTHER):($3/1000):($0+1) w points pt 7 pointsize 0.5 lc variable not
