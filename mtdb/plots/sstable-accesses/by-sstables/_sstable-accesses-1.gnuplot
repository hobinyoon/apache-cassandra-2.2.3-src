# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

# Can be parameterized later
NUM_SSTABLES=17

## Get min and max values
##   GPVAL_DATA_[X|Y]_[MIN|MAX]
#set terminal unknown
#set xdata time
#set timefmt "%Y-%m-%d-%H:%M:%S"
#plot \
#FN_IN u 2:3 w points not

set terminal pdfcairo enhanced size 3in, 2in
set output FN_OUT

#set tmargin at screen 0.975
#set bmargin at screen 0.152
#set lmargin at screen 0.185
#set rmargin at screen 0.940

set xlabel "SStable gen ID" offset 0,0.3
set ylabel "# of reads (in K)" offset 1.6,0

set border (1 + 2) back lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080"
set ytics nomirror scale 0.5,0 tc rgb "#808080"

set xrange [0.5:NUM_SSTABLES+0.5]

set style fill solid 0.2 noborder

BOX_WIDTH=0.5
plot \
FN_IN u 1:($2/1000):(BOX_WIDTH) w boxes not
