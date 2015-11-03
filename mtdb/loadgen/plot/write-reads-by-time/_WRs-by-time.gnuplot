# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

set terminal pdfcairo enhanced size 3in, 2in
set output FN_OUT

set xlabel "Time"
set ylabel "Primary key"

# TODO: get R times right
# TODO: dep file doesn't have to be built everytime. compare with .jar file!

set border (1 + 2) lc rgb "#808080"
set ytics nomirror scale 0.5,0 tc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080"
#set xtics nomirror scale 0.5,0 tc rgb "#808080" ( \
#		"1h" 3600 \
#		, "1d" 24*3600 \
#		, "1m" 365.0/12*24*3600 \
#		, "1y" 365.0*24*3600 \
#		, "XX" 30*365.0*24*3600 \
#		)

set pointsize 0.2

set key box lc rgb "#808080" opaque

plot \
FN_IN u 3:((strcol(2) eq "W") ? $1 : 1/0) w points pt 7 lc rgb "#FF0000" t "Write", \
FN_IN u 3:((strcol(2) eq "R") ? $1 : 1/0) w points pt 7 lc rgb "#0000FF" t "Read"
