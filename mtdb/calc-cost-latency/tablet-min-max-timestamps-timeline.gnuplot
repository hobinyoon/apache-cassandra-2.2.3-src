# Tested with gnuplot 4.6 patchlevel 6

# Tablet created/deleted events
FN_IN = system("echo $FN_IN")
# Tablet access counts
FN_IN_AC = system("echo $FN_IN_AC")
FN_OUT = system("echo $FN_OUT")

set xdata time
set ydata time
set timefmt "%y%m%d-%H%M%S"

set format x "'%y"
set format y "'%y"

# boxxyerrorbars parameters
#   x  y  xlow  xhigh  ylow  yhigh

# time data arithmetic doesn't work. label y-cord data needed to be generated with python.

# Get the plot range
set terminal unknown
plot \
FN_IN u 2:6:2:5:6:7:1 w boxxyerrorbars, \
FN_IN u 2:8:1:1 w labels right offset -0.5,0
X_MIN=GPVAL_DATA_X_MIN
X_MAX=GPVAL_DATA_X_MAX
Y_MIN=GPVAL_DATA_Y_MIN
Y_MAX=GPVAL_DATA_Y_MAX

set terminal pdfcairo enhanced rounded size 12in, 8in
set output FN_OUT

set border (1+2) front lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "black"
set ytics nomirror scale 0.5,0 tc rgb "black"

# Give some margin on the left and at the bottom
x0=X_MIN-(365.25/12*1.3*24*3600)
x1=X_MAX+(365.25/12*0.5*24*3600)
y0=Y_MIN - (365.25/12*1.0*24*3600)
y1=Y_MAX
set xrange [x0:x1]
set yrange [y0:y1]

set style fill transparent solid 0.15

# TODO: avoid illegible colors. define a custom color set
# gnuplot doesn't have a mod function
#   http://www.macs.hw.ac.uk/~ml355/lore/gnuplot.htm
mod(a, b) = a - floor(a/b) * b

plot \
FN_IN u 2:6:2:5:6:7:(mod($1, 2)) w boxxyerrorbars linecolor variable not, \
FN_IN u 2:8:1:1 w labels right offset -0.5,0 textcolor variable font "bold" not
