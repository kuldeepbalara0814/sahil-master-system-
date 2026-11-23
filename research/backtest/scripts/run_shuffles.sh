#!/bin/bash
# shuffled-data control runs (same harness). usage: run_shuffles.sh   (waits for real run)
PY=/data/data/com.termux/files/usr/bin/python3
cd "$(dirname "$0")/.."
while ! grep -q DONE out/progress_real.txt 2>/dev/null; do sleep 10; done
for i in 1 2 3 4 5 6 7 8; do
  m=row; [ $((i%2)) -eq 0 ] && m=col
  nice -n 10 $PY scripts/harness.py run --tag shuf_${m}${i} --shuffle $m --seed $i --blocks 100 --light-step 2 --procs 3
done
for i in 11 12 13 14 15 16 17 18 19 20 21 22; do
  m=row; [ $((i%2)) -eq 0 ] && m=col
  nice -n 10 $PY scripts/harness.py run --tag shufL_${m}${i} --shuffle $m --seed $i --light-step 2 --no-heavy --procs 3
done
echo ALLDONE > out/progress_shuffles_done.txt
