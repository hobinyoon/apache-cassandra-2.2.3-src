# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

# Get min and max values
set terminal unknown
set xdata time
set timefmt "%y%m%d-%H%M%S"
set format x "'%y"

plot \
FN_IN u 1:($2/1024/1024/1024) w fsteps, \
FN_IN u 1:($3/1024/1024/1024) w fsteps, \
FN_IN u 1:($4+$5) w lines axes x1y2

X_MIN=GPVAL_DATA_X_MIN
X_MAX=GPVAL_DATA_X_MAX
Y_MIN=GPVAL_DATA_Y_MIN
Y_MAX=GPVAL_DATA_Y_MAX
Y2_MIN=GPVAL_DATA_Y2_MIN
Y2_MAX=GPVAL_DATA_Y2_MAX


set terminal pdfcairo enhanced size 3in, 2in
set output FN_OUT

set tmargin at screen 0.995
set bmargin at screen 0.175
set lmargin at screen 0.105
set rmargin at screen 0.870

set xlabel "Time" offset 0,0.3
set ylabel "Storage size (GB)" offset 1.3,0
set y2label "Cumulative storage cost ($)" offset -1.5,0

set border (1 + 2 + 8) back lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080" #autofreq 0,(365.25*24*3600)

# Not sure if this is what I wanted. Not important.
x1(a)=(10**floor(log10(a)))
x2(a)=floor(a/x1(a))*x1(a)
x3(a)=floor(a/x1(a)/2)*x1(a)*2
startsWith1(a)=(a == x1(a))
yTicsStep(a, b)=(startsWith1(x2(a/b)) ? x2(a/b) : x3(a/b))

set print "-"
print (sprintf("Y_MAX: %f", Y_MAX))
print (sprintf("Y2_MAX: %f", Y2_MAX))
print (sprintf("yTicsStep(Y_MAX, 2)=%f", yTicsStep(Y_MAX, 2)))
print (sprintf("yTicsStep(Y2_MAX, 2)=%f", yTicsStep(Y2_MAX, 2)))

# TODO: disabled for "generates increment must be positive"
#   160226-140338
set ytics  nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,1
set y2tics nomirror scale 0.5,0 tc rgb "#808080" offset -1,0 #autofreq 0,yTicsStep(Y2_MAX, 2)
set tics front

set xrange [X_MIN:X_MAX]
set yrange [Y_MIN:Y_MAX]
set y2range [Y2_MIN:Y2_MAX]

set key top left

set pointsize 0.1

plot \
FN_IN u 1:($2/1024/1024/1024) w steps lc rgb "red" t "Hot", \
FN_IN u 1:($3/1024/1024/1024) w steps lc rgb "blue" t "Cold", \
FN_IN u 1:4 w linespoints axes x1y2 pt 7 lc rgb "red" not, \
FN_IN u 1:5 w linespoints axes x1y2 pt 7 lc rgb "blue" not, \
FN_IN u 1:($4+$5) w linespoints axes x1y2 pt 7 lc rgb "black" not

#FN_IN u 1:($2/1000000) w fillsteps fs solid 0.15 noborder not, \
