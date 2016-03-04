# Tested with gnuplot 4.6 patchlevel 6

FN_IN_0 = system("echo $FN_IN_0")
FN_IN_1 = system("echo $FN_IN_1")
FN_IN_2 = system("echo $FN_IN_2")

LAST_X_0 = system("echo $LAST_X_0")
LAST_Y_0 = system("echo $LAST_Y_0")
LAST_X_1 = system("echo $LAST_X_1")
LAST_Y_1 = system("echo $LAST_Y_1")
LAST_X_2 = system("echo $LAST_X_2")
LAST_Y_2 = system("echo $LAST_Y_2")

LABEL_0 = system("echo $LABEL_0")
LABEL_1 = system("echo $LABEL_1")
LABEL_2 = system("echo $LABEL_2")

COL_IDX_LAT = system("echo $COL_IDX_LAT")

FN_OUT = system("echo $FN_OUT")
LABEL_Y = system("echo $LABEL_Y")
Y_MAX = system("echo $Y_MAX")
X_TICS_INTERVAL = system("echo $X_TICS_INTERVAL")
Y_TICS_INTERVAL = system("echo $Y_TICS_INTERVAL")

set print "-"

#print (sprintf("LOCAL_SSD_LAST_X: %s", LOCAL_SSD_LAST_X))
#print (sprintf("LOCAL_SSD_LAST_Y: %s", LOCAL_SSD_LAST_Y))

#print (sprintf("c_lat: %s", c_lat))
# Convert string to int
#   http://stackoverflow.com/questions/9739315/how-to-convert-string-to-number-in-gnuplot
#c_lat=c_lat+0

c_thrp =  5              # throughput
c_lat  = COL_IDX_LAT + 0 # Latency
c_sat  = 12              # Saturated (overloaded)

## Get min and max values
set terminal unknown
plot \
FN_IN_0 u (column(c_thrp)/1000):(column(c_lat)) with linespoints, \
FN_IN_1 u (column(c_thrp)/1000):(column(c_lat)) with linespoints, \
FN_IN_2 u (column(c_thrp)/1000):(column(c_lat)) with linespoints
X_MIN=GPVAL_DATA_X_MIN
X_MAX=GPVAL_DATA_X_MAX
Y_MIN=GPVAL_DATA_Y_MIN

set terminal pdfcairo enhanced size 2in, 1.5in
set output FN_OUT

set tmargin at screen 0.985
set bmargin at screen 0.240
set lmargin at screen 0.2190
set rmargin at screen 0.990

set xlabel "Throughput (K OP/sec)" offset 0,0.3
set ylabel LABEL_Y offset 1.9,-0.5

set border (1 + 2) back lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,X_TICS_INTERVAL
set ytics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,Y_TICS_INTERVAL

# Gnuplot colors
#   http://www.ss.scphys.kyoto-u.ac.jp/person/yonezawa/contents/program/gnuplot/img/colorname-list2.png
color0="blue"
#color1="slateblue1"
color1="dark-plum"
color2="red"

set label LABEL_0 at (LAST_X_0 / 1000.0), LAST_Y_0 center offset 0,1.2 tc rgb color0 font ",8"
set label LABEL_1 at (LAST_X_1 / 1000.0), LAST_Y_1 center offset 0,1.2 tc rgb color1 font ",8"
set label LABEL_2 at (LAST_X_2 / 1000.0), LAST_Y_2 center offset 0,1.2 tc rgb color2 font ",8"

set xrange [0:11]
set yrange [0:Y_MAX]

lw1=3

plot \
FN_IN_0 u (column(c_thrp)/1000.0):(column(c_sat) <= 1 ? column(c_lat) : 1/0) w lp pt 7 ps 0.2 lc rgb color0 not, \
FN_IN_1 u (column(c_thrp)/1000.0):(column(c_sat) <= 1 ? column(c_lat) : 1/0) w lp pt 7 ps 0.2 lc rgb color1 not, \
FN_IN_2 u (column(c_thrp)/1000.0):(column(c_sat) <= 1 ? column(c_lat) : 1/0) w lp pt 7 ps 0.2 lc rgb color2 not, \
FN_IN_0 u (column(c_thrp)/1000.0):(column(c_sat) >= 1 ? column(c_lat) : 1/0) w l lc rgb color0 lt 0 lw lw1 not, \
FN_IN_1 u (column(c_thrp)/1000.0):(column(c_sat) >= 1 ? column(c_lat) : 1/0) w l lc rgb color1 lt 0 lw lw1 not, \
FN_IN_2 u (column(c_thrp)/1000.0):(column(c_sat) >= 1 ? column(c_lat) : 1/0) w l lc rgb color2 lt 0 lw lw1 not, \
FN_IN_0 u (column(c_thrp)/1000.0):(column(c_sat) >= 1 ? column(c_lat) : 1/0) w p pt 6 ps 0.2 lc rgb color0 not, \
FN_IN_1 u (column(c_thrp)/1000.0):(column(c_sat) >= 1 ? column(c_lat) : 1/0) w p pt 6 ps 0.2 lc rgb color1 not, \
FN_IN_2 u (column(c_thrp)/1000.0):(column(c_sat) >= 1 ? column(c_lat) : 1/0) w p pt 6 ps 0.2 lc rgb color2 not
