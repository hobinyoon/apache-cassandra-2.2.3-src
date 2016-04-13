# Tested with gnuplot 4.6 patchlevel 6

set print "-"
FN_INS = system("echo $FN_INS")
COL_IDX = system("echo $COL_IDX")
FN_OUT = system("echo $FN_OUT")
LEGEND_LABELS = system("echo $LEGEND_LABELS")

Y_MAX = system("echo $Y_MAX")
Y_TICS_INTERVAL = system("echo $Y_TICS_INTERVAL")

#print (sprintf("c_lat: %s", c_lat))
# Convert string to int
#   http://stackoverflow.com/questions/9739315/how-to-convert-string-to-number-in-gnuplot
#c_lat=c_lat+0

c_x       = 0         # column(c_x)/1000.0, when c_x=5 is throughput
c_sat     = 12        # Saturated (overloaded)

# Get min and max values
#set terminal unknown
#X_MIN=GPVAL_DATA_X_MIN

# Note: terminal size is not the same across cpu, network, and disk, if it matters.
#terminal_size_x=3.5 * 0.95
#terminal_size_y=0.45 * terminal_size_x
#set terminal pdfcairo enhanced size (terminal_size_x)in, (terminal_size_y)in

set terminal pdfcairo enhanced size 2in, 1.5in

set output FN_OUT

#set bmargin at screen 0.280
#set lmargin 8.1
#set rmargin 1.4

set xlabel "Req rate (in 10K reqs / simulation time min)"
set ylabel "Cost ($)"

set border (1 + 2) back lc rgb "#808080"
set xtics nomirror scale 0.5,0 tc rgb "#808080" #autofreq 0,4
set ytics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0,Y_TICS_INTERVAL

colors="#0000FF #FF0000 brown"

#set xrange [0:12]
set yrange [0:Y_MAX]

# Legend
y1=Y_MAX*1.21
y1p=Y_MAX*0.01
y2=y1+12*y1p

x0=14
x2=12
legend_label_x(i) = \
(i==1 ? x0-x2 : \
(i==2 ? x0 : \
x0+x2 \
))

legend_arrow_len_half = 1.5
legend_arrow_dot_height_half = 0.5*y1p

legend_label2(w) = \
(w eq "ES" ? "EBS SSD only" : \
(w eq "EM" ? "EBS Magnetic only" : \
(w eq "LS" ? "Local SSD only" : \
(w eq "LSES" ? "LS + ES" : \
(w eq "LSEM" ? "LS + EM" : \
"unexpected" \
)))))
legend_label1(i) = legend_label2(word(LEGEND_LABELS, i))

do for [i=1:3] {
set label legend_label1(i) at legend_label_x(i), y1 center font ",10" tc rgb word(colors, i)
set arrow from legend_label_x(i)-legend_arrow_len_half,y2 to legend_label_x(i)+legend_arrow_len_half,y2 nohead lc rgb word(colors, i) lw 1.5
set arrow from legend_label_x(i),y2+legend_arrow_dot_height_half to legend_label_x(i),y2-legend_arrow_dot_height_half nohead lw 3 lc rgb word(colors, i)
}

lw1=4

col_idx(i) = word(COL_IDX, i) + 0

# TODO: will need a legend

# Whether a system is saturated or not doesn't affect the cost. Probably I
# don't have to worry about presenting saturated system differently.



# TODO: x-axis needs to be 3 + 4 (num writes + num reads / simulation mins, which was 26.667 mins)

plot \
for [i=1:words(FN_INS)] word(FN_INS, i) \
	u ($3+$4):(column(col_idx(1)) + column(col_idx(2))) \
	w lp ps 0.4 lc rgb word(colors, i) t word(LEGEND_LABELS, i)

#BOX_WIDTH=500000
## boxxyerrorbars parameters
## #   x  y  xlow  xhigh  ylow  yhigh
#plot \
#for [i=1:words(FN_INS)] word(FN_INS, i) \
#	u ($3+$4):(0):($3+$4 + (i-2)*BOX_WIDTH - (BOX_WIDTH/2)):($3+$4 + (i-2)*BOX_WIDTH + (BOX_WIDTH/2)):(0):(column(col_idx(1))) \
#	w boxxyerrorbars lc rgb word(colors, i) t word(LEGEND_LABELS, i)



#
## TODO: fill white inside the empty circles
#plot \
#for [i=1:words(FN_INS)] word(FN_INS, i) u (column(c_x)):(column(c_sat) <= 1 ? column(col_idx(1)) : 1/0) w lp pt 7 ps 0.15 lc rgb word(colors, i) not, \
#for [i=1:words(FN_INS)] word(FN_INS, i) u (column(c_x)):(column(c_sat) >= 1 ? column(col_idx(1)) : 1/0) w l lc rgb word(colors, i) lt 0 lw lw1 not, \
#for [i=1:words(FN_INS)] word(FN_INS, i) u (column(c_x)):(column(c_sat) >= 1 ? column(col_idx(1)) : 1/0) w p pt 6 ps 0.2 lc rgb word(colors, i) not





