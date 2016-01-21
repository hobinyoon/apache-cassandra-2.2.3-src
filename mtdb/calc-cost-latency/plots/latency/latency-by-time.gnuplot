# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

set terminal pdfcairo enhanced size 3in, 2in
set output FN_OUT

#set tmargin at screen 0.975
#set bmargin at screen 0.152
#set lmargin at screen 0.185
#set rmargin at screen 0.940

set xlabel "Time (year)" offset 0,0.3
set ylabel "Latency (ms)" offset 1.3,0

set border (1 + 2) lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080"
set ytics nomirror scale 0.5,0 tc rgb "#808080"
set tics front

set xdata time
set timefmt "%y%m%d-%H%M%S"
set format x "'%y"

set key top left #opaque

set samples 1000

#set pointsize 50000
# points of linespoints are not noticeable. I wonder if they are not drawn when
# lw is 0.1
# FN_IN u 3:4 w linespoints pt 7 lw 0.1 lc rgb "#FF8080" t "write", \
#
plot \
FN_IN u 3:4 w lines lw 0.1 lc rgb "#FF8080" t "write", \
""    u 3:5 w lines lw 0.1 lc rgb "#8080FF" t "read", \
""    u 3:4 w lines smooth bezier lc rgb "red"  not, \
""    u 3:5 w lines smooth bezier lc rgb "blue" not
