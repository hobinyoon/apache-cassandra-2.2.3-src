# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")
Y0 = system("echo $Y0")
Y1 = system("echo $Y1")

# Get the plot range
set terminal unknown
BOX_WIDTH=0.5
plot \
FN_IN u 0:4:(BOX_WIDTH):xtic(1) w boxes not
Y_MAX=GPVAL_DATA_Y_MAX

set terminal pdfcairo enhanced size 2in, 1.5in

set output FN_OUT

#set tmargin at screen 0.98
set bmargin at screen 0.255
#set lmargin at screen 0.183
#set rmargin at screen 0.99

set border (1 + 2) lc rgb "#808080" back
set ylabel "Storage cost ($)"

set xtics nomirror scale 0.5,0 tc rgb "black" font ",8"
set ytics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,2

set style fill solid 0.3 border

set yrange [0:Y_MAX]

set arrow from (BOX_WIDTH/2)  ,Y0 to (1+BOX_WIDTH/2),Y0 nohead lt 0 lc "#000000" front
x0=1
set arrow from x0,Y0 to x0,Y1 head   lt 1 lc "#000000" front
x1=x0-0.125*BOX_WIDTH
set label (sprintf("-%.2f%%", 100.0*(Y0-Y1)/Y0)) at x1,((Y0+Y1)/2) right font ",10"

plot \
FN_IN u 0:4:(BOX_WIDTH):xtic(1) w boxes lc rgb "red" not, \
FN_IN u 0:2:($0-BOX_WIDTH/2):($0+BOX_WIDTH/2):2:4 w boxxyerrorbars lc rgb "blue" not
