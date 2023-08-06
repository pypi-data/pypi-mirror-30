from myhdlpeek import *

trc1 = Trace([Sample(0,0), Sample(10,5), Sample(20,3), Sample(30,0)])
trc2 = Trace([Sample(5,5), Sample(10,6), Sample(15,0), Sample(20,3)])
trc1.name = 'Trace1'
trc2.name = 'Trace2'

print(traces_to_dataframe(trc1, trc2))
print(traces_to_dataframe(trc1, trc2, start_time=10, stop_time=20))
print(traces_to_dataframe(trc1, trc2, start_time=10, stop_time=20, step=1))

traces_to_text_table(trc1.delay(1).binarize() ^ trc1.binarize())
traces_to_text_table(trc1.anyedge())
print(trc1.anyedge().trig_times())
traces_to_text_table(trc1>3)
traces_to_text_table(trc1.anyedge() & (trc1>3))
