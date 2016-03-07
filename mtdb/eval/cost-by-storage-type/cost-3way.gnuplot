# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")
cost_hot = system("echo $cost_hot") + 0
cost_mutants = system("echo $cost_mutants") + 0
Y_MAX = system("echo $Y_MAX")
Y_TICS_INTERVAL = system("echo $Y_TICS_INTERVAL")

set terminal pdfcairo enhanced size 2in, 1.5in
set output FN_OUT

set lmargin at screen 0.2
set rmargin at screen 1.0
set tmargin at screen 0.98
set bmargin at screen 0.13

set ylabel "Storage cost" offset 1.2,0

set border (1 + 2) back lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "black"
set ytics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0, Y_TICS_INTERVAL

set xrange [-0.5 : 2.5]
set yrange [0 : Y_MAX]

set linetype 1 lc rgb "blue"
set linetype 2 lc rgb "brown"
set linetype 3 lc rgb "red"

BOX_WIDTH=0.4

set arrow from (1-BOX_WIDTH/2),cost_hot to 2,cost_hot nohead lt 0 lw 2
set arrow from 1,cost_hot to 1,cost_mutants size screen 0.04,25
set label (sprintf("-%.2f%%", 100.0 * (cost_hot - cost_mutants)/cost_hot)) at (1-BOX_WIDTH*0.2),(cost_hot+cost_mutants)/2 right

set style fill solid 0.3 #noborder

# boxxyerrorbars parameters
#   x  y  xlow  xhigh  ylow  yhigh

plot \
FN_IN u                   0:(0):($0-BOX_WIDTH/2):($0+BOX_WIDTH/2):(0):2:xtic(1) w boxxyerrorbars lc rgb "red"  not, \
FN_IN u ($3 == 0 ? 1/0 : 0):2  :($0-BOX_WIDTH/2):($0+BOX_WIDTH/2):2  :4         w boxxyerrorbars lc rgb "blue" not
