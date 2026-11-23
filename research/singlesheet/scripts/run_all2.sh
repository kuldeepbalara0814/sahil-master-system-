#!/bin/sh
# resumable runner: skips outputs that already exist with enough shuffles. one process at a time.
cd $(dirname $0)
PY=/data/data/com.termux/files/usr/bin/python3
P=../out/PROGRESS_run.txt
step() { # name outfile cmd...
  n=$1; o=$2; shift 2
  if [ -f ../out/$o ]; then echo "skip $n" >> $P; return; fi
  avail=$(free -m | awk '/Mem:/{print $7}')
  while [ "$avail" -lt 600 ]; do echo "wait mem $avail" >> $P; sleep 30; avail=$(free -m | awk '/Mem:/{print $7}'); done
  echo "start $n $(date +%T)" >> $P
  nice -n 10 "$@" > ../out/log_$n.txt 2>&1
  echo "end $n $(date +%T)" >> $P
}
step p1_DS_month p1_DS_month.npz $PY part1.py DS month 100
step p1_FB_block30 p1_FB_block30.npz $PY part1.py FB block30 100
step p1_GB_month p1_GB_month.npz $PY part1.py GB month 100
step p1_GL_month p1_GL_month.npz $PY part1.py GL month 100
step p1_DS_block30 p1_DS_block30.npz $PY part1.py DS block30 100
step p1_GB_block30 p1_GB_block30.npz $PY part1.py GB block30 100
step p1_GL_block30 p1_GL_block30.npz $PY part1.py GL block30 100
for g in DS FB GB GL; do
 n=100; [ $g = DS ] && n=100
 for p in 2 3 5; do step p${p}_$g p${p}_$g.npz $PY part$p.py $g $n; done
done
step p4_DS p4_DS.npz $PY part4.py DS 40
step p4_FB p4_FB.npz $PY part4.py FB 60
step p4_GB p4_GB.npz $PY part4.py GB 40
step p4_GL p4_GL.npz $PY part4.py GL 40
echo ALLDONE >> $P
