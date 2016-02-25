# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

## Get min and max values
##   GPVAL_DATA_[X|Y]_[MIN|MAX]
#set terminal unknown
#set xdata time
#set timefmt "%Y-%m-%d-%H:%M:%S"
#plot \
#FN_IN u 2:3 w points not

set terminal pdfcairo enhanced size 2in, 1.5in
set output FN_OUT

set tmargin at screen 0.965
set bmargin at screen 0.225
set lmargin at screen 0.225
set rmargin at screen 0.945

#set xlabel "SStable gen ID" #offset 0,0.3
set ylabel "Cost ($/Month)" offset 1.2,0

COST_OTHER=401.3691667

set border (2) back lc rgb "#808080"
#set xtics nomirror scale 0.5,0 tc rgb "black"
set ytics nomirror scale 0.5,0 tc rgb "#808080" format "%.0f" (0, COST_OTHER, 800, 1200)
set tics front
set noxtics

set xrange [-0.5:3.8]
set yrange [0:]

set style fill solid 0.6 #noborder

set linetype 1 lc rgb "blue"
set linetype 2 lc rgb "#a52a2a"
set linetype 3 lc rgb "red"

# X axis
set arrow from -0.5,0 to 2.5, 0 nohead front lc rgb "#808080"

# Other cost line
set arrow from -0.5,COST_OTHER to 2.5,COST_OTHER nohead front lt 0

COST_LOCAL_SSD=844.1333333

x0=2.7
y0=COST_OTHER + COST_LOCAL_SSD
set arrow from x0,0 to x0,y0 nohead front lc rgb "#808080"

x1=x0-0.1
x2=x0+0.1
set arrow from x1,         0 to x2,         0 nohead front lc rgb "#808080"
set arrow from x1,COST_OTHER to x2,COST_OTHER nohead front lc rgb "#808080"
set arrow from x1,        y0 to x2,        y0 nohead front lc rgb "#808080"

y1 = COST_OTHER / 2
set label "Others"  at x2, y1
y2 = COST_OTHER + (COST_LOCAL_SSD / 2)
set label "Storage" at x2, y2



set label "EBS\nMag"   at 0, 0 center offset 0,-0.8 tc rgb "blue"
set label "EBS\nSSD"   at 1, 0 center offset 0,-0.8 tc rgb "#a52a2a"
set label "Local\nSSD" at 2, 0 center offset 0,-0.8 tc rgb "red"

# boxxyerrorbars parameters
#   x  y  xlow  xhigh  ylow  yhigh
BOX_WIDTH=0.4

plot \
FN_IN u 0:(COST_OTHER):($0-BOX_WIDTH/2):($0+BOX_WIDTH/2):(COST_OTHER):($2+COST_OTHER):($0+1) w boxxyerrorbars lc variable not, \
FN_IN u 0:(0)         :($0-BOX_WIDTH/2):($0+BOX_WIDTH/2):(0)         :(COST_OTHER)           w boxxyerrorbars lc "#808080" not

#FN_IN u 0:2:2:($0+1) w labels offset 0,0.5 tc variable not
