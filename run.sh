#!/usr/bin/env bash
html_report="reports/$(date '+%Y-%m-%d-%H-%M-%S').html"
test_bed=$1
test_data=$2
xoption=""
if [ "$test_bed" != "-" ]; then
  echo " !!! Using test bed: $test_bed"
  xoption+="-XtestBed=$test_bed "
fi
if [ "$test_data" != "-" ]; then
  echo " !!! Using test data: $test_data"
  xoption+="-XtestData=$test_data "
fi

python $xoption -m pytest --show-capture=no -s -v --html="$html_report" "$3"
