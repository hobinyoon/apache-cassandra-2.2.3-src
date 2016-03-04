# Tested with gnuplot 4.6 patchlevel 6

set print "-"
FN_IN = system("echo $FN_IN")
LABELS = system("echo $LABELS")
COL_IDX_LAT = system("echo $COL_IDX_LAT")
FN_OUT = system("echo $FN_OUT")
LABEL_Y = system("echo $LABEL_Y")
Y_MAX = system("echo $Y_MAX")
Y_TICS_INTERVAL = system("echo $Y_TICS_INTERVAL")

#print (sprintf("LOCAL_SSD_LAST_X: %s", LOCAL_SSD_LAST_X))
#print (sprintf("LOCAL_SSD_LAST_Y: %s", LOCAL_SSD_LAST_Y))

#print (sprintf("c_lat: %s", c_lat))
# Convert string to int
#   http://stackoverflow.com/questions/9739315/how-to-convert-string-to-number-in-gnuplot
#c_lat=c_lat+0

c_thrp = 5               # throughput
c_ru   = COL_IDX_LAT + 0 # y metric (res usage)
c_sat  = 12              # Saturated (overloaded)

## Get min and max values
set terminal unknown
plot \
for [i=1:words(FN_IN)] word(FN_IN, i) u 0:(column(c_sat) <= 1 ? column(c_ru) : 1/0) w lp
X_MIN=GPVAL_DATA_X_MIN
X_MAX=GPVAL_DATA_X_MAX
Y_MIN=GPVAL_DATA_Y_MIN
#Y_MAX=GPVAL_DATA_Y_MAX

y_max_0=Y_MAX
x_pos(x)=X_MIN+(X_MAX-X_MIN)/100.0*x
y_pos(y)=Y_MIN+(y_max_0-Y_MIN)/100.0*y

set terminal pdfcairo enhanced size 2in, 1.5in
set output FN_OUT

set tmargin at screen 0.965
set bmargin at screen 0.260
set lmargin at screen 0.2290
set rmargin at screen 0.990

set xlabel "Throughput (K OP/sec)"
set ylabel LABEL_Y offset 1,0

set border (1 + 2) back lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,2
set ytics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,Y_TICS_INTERVAL

colors="#FF0000 #0000FF #00BB00 #DD00DD #00A0A0 #606060 #8A2BE2 #DAA520 #000000"

set xrange [0:11]
set yrange [0:y_max_0]

# Custom label. set key doesn't give you a good one.
x0=5
x1=x0+9
x2=(x0 + x1)/2.0
x3=x2+7
y0=102
y_interval=8.5
do for [i=0:words(LABELS)] { \
set arrow from x_pos(x0), y_pos(y0 - y_interval*i) to x_pos(x1), y_pos(y0 - y_interval*i) nohead lc rgb word(colors, i); \
set obj circle at x_pos(x2), y_pos(y0 - y_interval*i) size 0.04 fc rgb word(colors, i) fs solid 1.0; \
set label word(LABELS, i) at x_pos(x3), y_pos(y0 - y_interval*i) tc rgb word(colors, i) font ",8"; \
}

lw1=2

plot \
for [i=1:words(FN_IN)] word(FN_IN, i) u (column(c_thrp)/1000.0):(column(c_sat) <= 1 ? column(c_ru) : 1/0) w lp pt 7 ps 0.15 lc rgb word(colors, i) not, \
for [i=1:words(FN_IN)] word(FN_IN, i) u (column(c_thrp)/1000.0):(column(c_sat) >= 1 ? column(c_ru) : 1/0) w l lc rgb word(colors, i) lt 0 lw lw1 not, \
for [i=1:words(FN_IN)] word(FN_IN, i) u (column(c_thrp)/1000.0):(column(c_sat) >= 1 ? column(c_ru) : 1/0) w p pt 6 ps 0.2 lc rgb word(colors, i) not
