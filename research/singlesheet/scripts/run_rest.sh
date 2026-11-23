#!/bin/sh
cd $(dirname $0)
PY=/data/data/com.termux/files/usr/bin/python3
while pgrep -f run_part1_all.sh > /dev/null; do sleep 10; done
for g in DS FB GB GL; do
 n=100; [ $g = DS ] && n=150
 nice -n 10 $PY part2.py $g $n > ../out/log_p2_$g.txt 2>&1
 nice -n 10 $PY part3.py $g 100 > ../out/log_p3_$g.txt 2>&1
 nice -n 10 $PY part5.py $g 100 > ../out/log_p5_$g.txt 2>&1
done
nice -n 10 $PY part4.py DS 30 > ../out/log_p4_DS.txt 2>&1
nice -n 10 $PY part4.py FB 60 > ../out/log_p4_FB.txt 2>&1
nice -n 10 $PY part4.py GB 40 > ../out/log_p4_GB.txt 2>&1
nice -n 10 $PY part4.py GL 40 > ../out/log_p4_GL.txt 2>&1
echo done > ../out/REST_DONE
