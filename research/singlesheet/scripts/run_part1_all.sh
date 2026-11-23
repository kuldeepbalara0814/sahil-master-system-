#!/bin/sh
cd $(dirname $0)
PY=/data/data/com.termux/files/usr/bin/python3
for g in FB DS GB GL; do for s in month block30; do
 n=100; [ $g = FB ] && n=150; [ $g = DS ] && n=150
 nice -n 10 $PY part1.py $g $s $n > ../out/log_p1_${g}_$s.txt 2>&1
done; done
