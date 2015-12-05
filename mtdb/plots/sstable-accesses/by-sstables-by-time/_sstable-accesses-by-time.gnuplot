# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")
FN_OUT_LOGSCALE = system("echo $FN_OUT_LOGSCALE")

# Get min and max values by plotting to unknown terminal.
# GPVAL_DATA_[X|Y]_[MIN|MAX] are set.
set terminal unknown
plot FN_IN u 0:1 w points not
NUM_SSTABLES=GPVAL_DATA_Y_MAX

set xdata time
set timefmt "%Y-%m-%d-%H:%M:%S"
plot FN_IN u 2:($4+$5) w points not
Y_MAX=GPVAL_DATA_Y_MAX
X_MIN=GPVAL_DATA_X_MIN
X_MAX=GPVAL_DATA_X_MAX

set terminal pdfcairo enhanced size 3in, 2in
set output FN_OUT

#set tmargin at screen 0.975
#set bmargin at screen 0.152
#set lmargin at screen 0.185
#set rmargin at screen 0.940

set print "-"
print sprintf("Y-axis normalized. Max SSTable accesses=%d", Y_MAX)

set xlabel "Time (year)" offset 0,0.3
set ylabel "# of SSTable accesses" offset 2,0

set border (1 + 2) back lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080"
set ytics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,5

set xdata time
set timefmt "%Y-%m-%d-%H:%M:%S"
set format x "'%y"
#set format x ":%S"

# Draw the bottom line. Not really needed.
#set for [i=1:NUM_SSTABLES] arrow from GPVAL_DATA_X_MIN,i to GPVAL_DATA_X_MAX,i nohead lc rgb "#C0C0C0" front

set pointsize 0.02

Height(x)=((x)/Y_MAX)

set xrange [X_MIN:X_MAX]
set yrange [:NUM_SSTABLES]

plot \
for [i=1:NUM_SSTABLES] \
FN_IN u 2:($1==i ? (($1-1)+Height($4+$5)) : 1/0) w filledcurves y1=(i-1) lc rgb "#FFC0C0" not, \
for [i=1:NUM_SSTABLES] \
FN_IN u 2:($1==i ? (($1-1)+Height($4+$5)) : 1/0) w lines lc rgb "#FF0000" not
#FN_IN u 2:($1==i ? (($1-1)+Height($4+$5)) : 1/0) w linespoints pt 7 lc rgb "#FF0000" not

# Plot in logscale for get better insights
set output FN_OUT_LOGSCALE

# value range
#   ($4+$5)        : [0, Y_MAX]
#   +1             : [1, Y_MAX+1]
#   log(above)     : [0(=log(1)), log(Y_MAX+1)]
#   / log(Y_MAX+1) : [0, 1]
Height(x)=(log(x+1)/log(Y_MAX+1))

plot \
for [i=1:NUM_SSTABLES] \
FN_IN u 2:($1==i ? (($1-1)+Height($4+$5)) : 1/0) w filledcurves y1=(i-1) lc rgb "#FFC0C0" not, \
for [i=1:NUM_SSTABLES] \
FN_IN u 2:($1==i ? (($1-1)+Height($4+$5)) : 1/0) w lines lc rgb "#FF0000" not
