#!/usr/bin/env bash
# python=./venv/bin/python3
python=python3

if [ $1 = "clear" ] || [ $1 = "clean" ]; then
  rm reports/*.html
  rm log/*.log
  exit
fi

test_bed=$1
test_data=$2
html_report="reports/$(date '+%Y.%m.%d-%H.%M.%S')-${test_bed}-${test_data}.html"
xoption="-XprepareCoin "

if [ "$test_bed" != "-" ]; then
  echo " !!! Using test bed: $test_bed"
  xoption+="-XtestBed=$test_bed "
fi
if [ "$test_data" != "-" ]; then
  echo " !!! Using test data: $test_data"
  xoption+="-XtestData=$test_data "
fi

param4=""

if [ -z "$4" ]; then
  param4=""
else
  param4="-k $4"
fi
set -x
$python $xoption -m pytest \
  --show-capture=stderr --capture=tee-sys -v --html="$html_report" --self-contained-html $3 $param4
