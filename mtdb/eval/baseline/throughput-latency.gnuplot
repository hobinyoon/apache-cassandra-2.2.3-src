# Tested with gnuplot 4.6 patchlevel 4

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

## Get min and max values
#set terminal unknown
#set logscale xy
#plot \
#FN_IN u 5:($2/1000):($3/1000):($4/1000) with yerrorbars
#X_MIN=GPVAL_DATA_X_MIN
#X_MAX=GPVAL_DATA_X_MAX
#Y_MIN=GPVAL_DATA_Y_MIN
#Y_MAX=GPVAL_DATA_Y_MAX

set terminal pdfcairo enhanced size 2in, 1.5in
set output FN_OUT

set xlabel "Throughput (K OP/sec)" #offset 0,0.2
set ylabel "Latency (ms)" offset 1,0

set border (1 + 2) back lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,2
set ytics nomirror scale 0.5,0 tc rgb "#808080"

set xrange [0:]
set yrange [0:]

set nokey

plot \
FN_IN u ($5/1000):(strcol(1) eq "EBS SSD GP2" ? $6 : 1/0) with linespoints pt 7 pointsize 0.2 t "EBS SSD", \
FN_IN u ($5/1000):(strcol(1) eq "EBS Mag"     ? $6 : 1/0) with linespoints pt 7 pointsize 0.2 t "EBS Mag", \
FN_IN u ($5/1000):(strcol(1) eq "Local SSD"   ? $6 : 1/0) with linespoints pt 7 pointsize 0.2 t "Local SSD"

# Looks too complicated
# (x, y, ylow, yhigh)
# median, avg, 99th
#plot \
#FN_IN u ($5/1000):(strcol(1) eq "EBS SSD GP2" ? $6 : 1/0):7:8 with yerrorbars pt 7 pointsize 0.2 t "EBS SSD", \
#FN_IN u ($5/1000):(strcol(1) eq "Local SSD"   ? $6 : 1/0):7:8 with yerrorbars pt 7 pointsize 0.2 t "Local SSD"



#FN_IN u ($5/1000):(strcol(1) eq "EBS SSD GP2" ? $6 : 1/0):(0):7 with vector nohead t "EBS SSD"

#, \
#FN_IN u ($5/1000):(strcol(1) eq "EBS Mag"     ? $9 : 1/0) with linespoints pt 7 pointsize 0.2 t "EBS Mag", \
#FN_IN u ($5/1000):(strcol(1) eq "Local SSD"   ? $9 : 1/0) with linespoints pt 7 pointsize 0.2 t "Local SSD"

#x1p=(X_MAX-X_MIN)*0.01
#y1p=(Y_MAX-Y_MIN)*0.01
#
#set tmargin at screen 0.970
#set bmargin at screen 0.210
#set lmargin at screen 0.205
#set rmargin at screen 0.970
#
#
#
#set print "-"
#print (sprintf("X_MIN: %f", X_MIN))
#print (sprintf("X_MAX: %f", X_MAX))
#print (sprintf("Y_MIN: %f", Y_MIN))
#print (sprintf("Y_MAX: %f", Y_MAX))
#
## Legend
#x0=0.7
#y0=10
#y1=y0*5
#set arrow from x0, y0 to x0, y1 lc rgb "red" nohead
#
#x1=x0/1.05
#x2=x0*1.05
#set arrow from x1, y0 to x2, y0 lc rgb "red" nohead
#set arrow from x1, y1 to x2, y1 lc rgb "red" nohead
#
#y2=y1/2.3
#set object 1 circle at x0,y2 size scr 0.004 fc rgb "red" fill solid
#set label "avg" at x0,y2 right offset -0.4,0 tc rgb "#404040" font ",9"
#set label "99%" at x0,y1 right offset -0.4,0 tc rgb "#404040" font ",9"
#set label "1%"  at x0,y0 right offset -0.4,0 tc rgb "#404040" font ",9"
#
#set xrange [0.02:1]
#
## with yerrorbars
##   (x, y, ylow, yhigh)
#plot \
#FN_IN u 5:($2/1000):($3/1000):($4/1000) with yerrorbars pt 7 pointsize 0.2 not, \
#FN_IN u 5:($2/1000):1 with labels offset 0,-0.5 font ",10" not
