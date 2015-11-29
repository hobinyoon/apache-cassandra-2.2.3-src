# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

# Can be parameterized later
NUM_SSTABLES=17

# Get min and max values
set terminal unknown
set xdata time
set timefmt "%Y-%m-%d-%H:%M:%S"
plot \
FN_IN u 2:($4+$5) w points not
# GPVAL_DATA_[X|Y]_[MIN|MAX] are set now

set terminal pdfcairo enhanced size 3in, 2in
set output FN_OUT

#set tmargin at screen 0.975
#set bmargin at screen 0.152
#set lmargin at screen 0.185
#set rmargin at screen 0.940

set xlabel "Time (min)" offset 0,0.3
set ylabel sprintf("Normalized # of accesses\nper sec by SSTables (max=%d)", GPVAL_DATA_Y_MAX)  offset 1.6,0

set border (1 + 2) back lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080"
set ytics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,5

set xdata time
set timefmt "%Y-%m-%d-%H:%M:%S"
set format x "%M"
#set format x ":%S"

# Draw the bottom line. Not really needed.
#set for [i=1:NUM_SSTABLES] arrow from GPVAL_DATA_X_MIN,i to GPVAL_DATA_X_MAX,i nohead lc rgb "#C0C0C0" front

set pointsize 0.02

MAX_HEIGHT=1.2*GPVAL_DATA_Y_MAX

set xrange [GPVAL_DATA_X_MIN:GPVAL_DATA_X_MAX]
set yrange [:NUM_SSTABLES]

plot \
for [i=1:NUM_SSTABLES] \
FN_IN u 2:($1==i ? (($1-1)+(($4+$5)/MAX_HEIGHT)) : 1/0) w filledcurves y1=(i-1) lc rgb "#FFC0C0" not, \
for [i=1:NUM_SSTABLES] \
FN_IN u 2:($1==i ? (($1-1)+(($4+$5)/MAX_HEIGHT)) : 1/0) w linespoints pt 7 lc rgb "#FF0000" not
