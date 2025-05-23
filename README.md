#Script for processing MX-One SDR files. 

Specify the path to the folder with the files, after processing you will receive an Excel file with data by day:
- Total duration of calls
- Time of the hour of the greatest load
- Number of simultaneous calls at the greatest load


 CDR file format: CSV
 Hrader:
```csv
# Call and quality data stored by DAREQ in comma separated format
# First 8 lines are comments, after that every line is comma separated data
# "&" in data is stored as "&amp;" and "," as "&comma;"
# The number of endpoints is open. If "QoS endpoint block x valid'
# is false (=0) no (more) endpoint(s) will follow.
# The following line is comma separated column heading (for 6 endpoints)
# start time UTC, stop time UTC, start time local, stop time local, duration, calling number, calling number type, calling number valid, access code 1, access code 2, dialed number, connected number, condition code, call case data, charged number, account code, account code valid, tax pulses, tax pulses valid, cil code, cil code valid, tns code, tns code valid, osa code, osa code valid, og trnk id, trunk queue time, og trnk id and trunk queue time valid, op queue time, op queue time valid, flex digit 1, flex digit 2, flex ascii, ring time counter, queue time counter, time counters valid, equ, equ valid, event level, is mobile logging, inc trnk id, inc trnk id valid, seq num, seq lim, call ref , QoS endpoint block 1 valid, endpoint type 1, rtp addr 1,  extension 1, QoS data block 1 valid,worst estimated end to end delay 1, mean estimated end to end dealy 1, cum num of packets lost 1, packet lost rate 1, worst jitter 1, estimated throughput 1, fraction lost rate 1, mean jitter 1 ,codec 1-1 type, codec 1-1, codec 1-2 type, codec 1-2, codec 1-3 type, codec 1-3, simple R value 1, QoS endpoint block 2 valid, endpoint type 2, rtp addr 2,  extension 2, QoS data block 2 valid,worst estimated end to end delay 2, mean estimated end to end dealy 2, cum num of packets lost 2, packet lost rate 2, worst jitter 2, estimated throughput 2, fraction lost rate 2, mean jitter 2 ,codec 2-1 type, codec 2-1, codec 2-2 type, codec 2-2, codec 2-3 type, codec 2-3, simple R value 2, QoS endpoint block 3 valid, endpoint type 3, rtp addr 3,  extension 3, QoS data block 3 valid,worst estimated end to end delay 3, mean estimated end to end dealy 3, cum num of packets lost 3, packet lost rate 3, worst jitter 3, estimated throughput 3, fraction lost rate 3, mean jitter 3 ,codec 3-1 type, codec 3-1, codec 3-2 type, codec 3-2, codec 3-3 type, codec 3-3, simple R value 3, QoS endpoint block 4 valid, endpoint type 4, rtp addr 4,  extension 4, QoS data block 4 valid,worst estimated end to end delay 4, mean estimated end to end dealy 4, cum num of packets lost 4, packet lost rate 4, worst jitter 4, estimated throughput 4, fraction lost rate 4, mean jitter 4 ,codec 4-1 type, codec 4-1, codec 4-2 type, codec 4-2, codec 4-3 type, codec 4-3, simple R value 4, QoS endpoint block 5 valid, endpoint type 5, rtp addr 5,  extension 5, QoS data block 5 valid,worst estimated end to end delay 5, mean estimated end to end dealy 5, cum num of packets lost 5, packet lost rate 5, worst jitter 5, estimated throughput 5, fraction lost rate 5, mean jitter 5 ,codec 5-1 type, codec 5-1, codec 5-2 type, codec 5-2, codec 5-3 type, codec 5-3, simple R value 5, QoS endpoint block 6 valid, endpoint type 6, rtp addr 6,  extension 6, QoS data block 6 valid,worst estimated end to end delay 6, mean estimated end to end dealy 6, cum num of packets lost 6, packet lost rate 6, worst jitter 6, estimated throughput 6, fraction lost rate 6, mean jitter 6 ,codec 6-1 type, codec 6-1, codec 6-2 type, codec 6-2, codec 6-3 type, codec 6-3, simple R value 6
```
