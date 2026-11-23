#!/bin/sh
# yearshuffle khatam hone ka intezar, phir real + 3 shuffle heavy sample (ek ke baad ek)
cd "$(dirname "$0")"

PY=/data/data/com.termux/files/usr/bin/python3
nice -n 10 $PY run_heavy_sample.py real
nice -n 10 $PY run_heavy_sample.py shufrow41 row 41
nice -n 10 $PY run_heavy_sample.py shufcol42 col 42
nice -n 10 $PY run_heavy_sample.py shufrow43 row 43
