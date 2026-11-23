#!/bin/sh
cd "$(dirname "$0")"; PY=/data/data/com.termux/files/usr/bin/python3
nice -n 10 $PY run_heavy_inc.py incrow51 row 51
nice -n 10 $PY run_heavy_inc.py inccol52 col 52
nice -n 10 $PY run_heavy_inc.py incrow53 row 53
