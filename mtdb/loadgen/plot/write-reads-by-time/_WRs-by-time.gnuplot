# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

set terminal pdfcairo enhanced size 3in, 2in
set output FN_OUT

set xlabel "Time"
set ylabel "Primary key" offset 1.5,0

set border (1 + 2) lc rgb "#808080"
set ytics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,10
set xtics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,365.2425*24*3600 format "%Y"

set xdata time
# seconds since the UNIX epoch
set timefmt "%s"

#set key box lc rgb "#808080" opaque
set nokey

# Plot reads first so that writes are on top
plot \
FN_IN u 3:((strcol(2) eq "R") ? $1 : 1/0) w points pt 7 ps 0.15 lc rgb "#0000FF" t "Read", \
FN_IN u 3:((strcol(2) eq "W") ? $1 : 1/0) w points pt 7 ps 0.2  lc rgb "#FF0000" t "Write"
