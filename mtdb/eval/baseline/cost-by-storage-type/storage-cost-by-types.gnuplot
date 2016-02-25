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

set tmargin at screen 0.965
set bmargin at screen 0.225
set lmargin at screen 0.205
set rmargin at screen 0.990

#set xlabel "SStable gen ID" #offset 0,0.3
set ylabel "Cost ($/GB/Month)" offset 1.8,0

set border (1 + 2) back lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "black"
set ytics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,0.2
set tics front

set yrange [0:]

set style fill solid 0.6 #noborder

set linetype 1 lc rgb "blue"
set linetype 2 lc rgb "#a52a2a"
set linetype 3 lc rgb "red"

BOX_WIDTH=0.4
plot \
FN_IN u 0:2:(BOX_WIDTH):($0+1):xtic(1) w boxes lc variable not, \
FN_IN u 0:2:2:($0+1) w labels offset 0,0.5 tc variable not
