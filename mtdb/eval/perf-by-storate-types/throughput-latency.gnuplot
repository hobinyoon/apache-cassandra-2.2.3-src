# Tested with gnuplot 4.6 patchlevel 4

FN_IN = system("echo $FN_IN")

FN_IN_EBS_MAG           = system("echo $FN_IN_EBS_MAG")
FN_IN_EBS_SSD           = system("echo $FN_IN_EBS_SSD")
FN_IN_LOCAL_SSD         = system("echo $FN_IN_LOCAL_SSD")
FN_IN_LOCAL_SSD_EBS_MAG = system("echo $FN_IN_LOCAL_SSD_EBS_MAG")
FN_IN_LOCAL_SSD_EBS_SSD = system("echo $FN_IN_LOCAL_SSD_EBS_SSD")

FN_OUT = system("echo $FN_OUT")
LABEL_Y = system("echo $LABEL_Y")

set print "-"
#print (sprintf("c_lat: %s", c_lat))
# Convert string to int
#   http://stackoverflow.com/questions/9739315/how-to-convert-string-to-number-in-gnuplot
#c_lat=c_lat+0

c_thrp =  5 # throughput
c_lat  =  6 # Latency
c_sat  = 12 # Saturated (overloaded)


## Get min and max values
set terminal unknown
plot \
FN_IN_EBS_MAG   u (column(c_thrp)/1000):(column(c_lat)) with linespoints, \
FN_IN_EBS_SSD   u (column(c_thrp)/1000):(column(c_lat)) with linespoints, \
FN_IN_LOCAL_SSD u (column(c_thrp)/1000):(column(c_lat)) with linespoints
X_MIN=GPVAL_DATA_X_MIN
X_MAX=GPVAL_DATA_X_MAX
Y_MIN=GPVAL_DATA_Y_MIN
Y_MAX=GPVAL_DATA_Y_MAX

set terminal pdfcairo enhanced size 2in, 1.5in
set output FN_OUT

set tmargin at screen 0.985
set bmargin at screen 0.240
set lmargin at screen 0.180
set rmargin at screen 0.990

set xlabel "Throughput (K OP/sec)" offset 0,0.3
set ylabel LABEL_Y offset 1.5,-0.3

set border (1 + 2) back lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,2
set ytics nomirror scale 0.5,0 tc rgb "#808080" #autofreq 0,20

# set label "EBS\nMagnetic" at (EBS_MAG_LABEL_X/1000)  , EBS_MAG_LABEL_Y   center offset 0,1.2 tc rgb "blue"    font ",8"
# set label "EBS\nSSD"      at (EBS_SSD_LABEL_X/1000)  , EBS_SSD_LABEL_Y   center offset 0,1.2 tc rgb "#a52a2a" font ",8"
# set label "Local\nSSD"    at (LOCAL_SSD_LABEL_X/1000), LOCAL_SSD_LABEL_Y center offset 0,1.2 tc rgb "red"     font ",8"
#
# #print (sprintf("AVG_AVG_LAT_EBS_MAG_X: %s", AVG_AVG_LAT_EBS_MAG_X))
# #print (sprintf("AVG_AVG_LAT_EBS_MAG_Y: %s", AVG_AVG_LAT_EBS_MAG_Y))
# set arrow from 0,0 to (AVG_AVG_LAT_EBS_MAG_X/1000)  , AVG_AVG_LAT_EBS_MAG_Y   nohead lt 0 lw 3 lc rgb "blue"
# set arrow from 0,0 to (AVG_AVG_LAT_EBS_SSD_X/1000)  , AVG_AVG_LAT_EBS_SSD_Y   nohead lt 0 lw 3 lc rgb "#a52a2a"
# set arrow from 0,0 to (AVG_AVG_LAT_LOCAL_SSD_X/1000), AVG_AVG_LAT_LOCAL_SSD_Y nohead lt 0 lw 3 lc rgb "red"

set xrange [0:11]
y0=Y_MAX*1.0
set yrange [0:y0]


# Gnuplot colors
#   http://www.ss.scphys.kyoto-u.ac.jp/person/yonezawa/contents/program/gnuplot/img/colorname-list2.png
#"#8060c0"

color0="blue"
#color1="slateblue1"
color1="dark-plum"
color2="red"

lw1=3

plot \
FN_IN_EBS_MAG   u (column(c_thrp)/1000):(column(c_sat) <= 1 ? column(c_lat) : 1/0) w lp pt 7 ps 0.2 lc rgb color0 not, \
FN_IN_EBS_SSD   u (column(c_thrp)/1000):(column(c_sat) <= 1 ? column(c_lat) : 1/0) w lp pt 7 ps 0.2 lc rgb color1 not, \
FN_IN_LOCAL_SSD u (column(c_thrp)/1000):(column(c_sat) <= 1 ? column(c_lat) : 1/0) w lp pt 7 ps 0.2 lc rgb color2 not, \
FN_IN_EBS_MAG   u (column(c_thrp)/1000):(column(c_sat) >= 1 ? column(c_lat) : 1/0) w l lc rgb color0 lt 0 lw lw1 not, \
FN_IN_EBS_SSD   u (column(c_thrp)/1000):(column(c_sat) >= 1 ? column(c_lat) : 1/0) w l lc rgb color1 lt 0 lw lw1 not, \
FN_IN_LOCAL_SSD u (column(c_thrp)/1000):(column(c_sat) >= 1 ? column(c_lat) : 1/0) w l lc rgb color2 lt 0 lw lw1 not, \
FN_IN_EBS_MAG   u (column(c_thrp)/1000):(column(c_sat) >= 1 ? column(c_lat) : 1/0) w p pt 6 ps 0.2 lc rgb color0 not, \
FN_IN_EBS_SSD   u (column(c_thrp)/1000):(column(c_sat) >= 1 ? column(c_lat) : 1/0) w p pt 6 ps 0.2 lc rgb color1 not, \
FN_IN_LOCAL_SSD u (column(c_thrp)/1000):(column(c_sat) >= 1 ? column(c_lat) : 1/0) w p pt 6 ps 0.2 lc rgb color2 not

# Looks too complicated
# (x, y, ylow, yhigh)
# median, avg, 99th
#plot \
#FN_IN u (column(c_thrp)/1000):(strcol(1) eq "EBS SSD GP2" ? $6 : 1/0):7:8 with yerrorbars pt 7 pointsize 0.2 t "EBS SSD", \
#FN_IN u (column(c_thrp)/1000):(strcol(1) eq "Local SSD"   ? $6 : 1/0):7:8 with yerrorbars pt 7 pointsize 0.2 t "Local SSD"
