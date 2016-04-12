# Tested with gnuplot 4.6 patchlevel 6

set print "-"
FN_INS = system("echo $FN_INS")
EGNS = system("echo $EGNS")
COL_METRIC = system("echo $COL_METRIC")
FN_OUT = system("echo $FN_OUT")
LABEL_Y = system("echo $LABEL_Y")
Y_MAX = system("echo $Y_MAX")
Y_TICS_INTERVAL = system("echo $Y_TICS_INTERVAL")

c_thrp =  5                # throughput
c_metric  = COL_METRIC + 0 # Latency
c_sat  = 12                # Saturated (overloaded)

## Get min and max values
#set terminal unknown
#X_MIN=GPVAL_DATA_X_MIN

#set terminal pdfcairo enhanced size 2in, 1.8in
#set tmargin at screen 0.995
#set bmargin at screen 0.202
#set lmargin at screen 0.165
#set rmargin at screen 1.0

set terminal pdfcairo enhanced size 1.5in, (1.5*0.9)in
set tmargin at screen 0.990
set bmargin at screen 0.272
set lmargin at screen 0.240365
set rmargin at screen 0.99

set output FN_OUT

set xlabel "Throughput (K op/s)" offset 0,0.3
set ylabel LABEL_Y offset 1.5,0

set border (1 + 2) back lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,2
set ytics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,Y_TICS_INTERVAL

colors="#0000FF brown #FF0000"

label0(i) = label2(word(EGNS, i))
label1(w) = \
(w eq "ebs-mag" ? "EBS\nMagnetic" : \
(w eq "ebs-ssd" ? "EBS\nSSD" : \
(w eq "local-ssd" ? "Local\nSSD" : \
(w eq "local-ssd-ebs-mag" ? "Local SSD\n+ EBS Mag" : \
(w eq "local-ssd-ebs-ssd" ? "Local SSD\n+ EBS SSD" : \
(w eq "local-ssd-local-ssd" ? "Local SSD\n+ Local SSD" : \
"unexpected" \
))))))
label2(w) = \
(w eq "ebs-mag" ? "EM" : \
(w eq "ebs-ssd" ? "ES" : \
(w eq "local-ssd" ? "LS" : \
(w eq "local-ssd-ebs-mag" ? "LS+EM" : \
(w eq "local-ssd-ebs-ssd" ? "LS+ES" : \
(w eq "local-ssd-local-ssd" ? "LS+LS" : \
"unexpected" \
))))))

# Legend
x0=0.5
x1=x0+1.0
x2=x1+0.2
label_y(i)=Y_MAX * (0.95 - 0.1 * (i - 1))
do for [i=1:words(EGNS)] {
set arrow from x0, label_y(i) to x1, label_y(i) lc rgb word(colors, i) nohead
set object circle at (x0+x1)/2, label_y(i) size screen 0.003 fc rgb word(colors, i) fs solid 1
set label label0(i) at x2, label_y(i) tc rgb word(colors, i) font ",8"
}

set xrange [0:11]
set yrange [0:Y_MAX]

lw1=3

plot \
for [i=1:words(FN_INS)] word(FN_INS, i) \
  u (column(c_thrp)/1000.0):(column(c_sat) <= 1 ? column(c_metric) : 1/0) \
    w lp pt 7 ps 0.2 lc rgb word(colors, i) not, \
for [i=1:words(FN_INS)] word(FN_INS, i) \
  u (column(c_thrp)/1000.0):(column(c_sat) >= 1 ? column(c_metric) : 1/0) \
    w l lc rgb word(colors, i) lt 0 lw lw1 not, \
for [i=1:words(FN_INS)] word(FN_INS, i) \
  u (column(c_thrp)/1000.0):(column(c_sat) >= 1 ? column(c_metric) : 1/0) \
    w p pt 6 ps 0.2 lc rgb word(colors, i) not
