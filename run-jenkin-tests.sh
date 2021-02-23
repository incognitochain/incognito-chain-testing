#!/usr/bin/env bash
# python=./venv/bin/python3
python=python3

test_bed=$1
test_data=$2
test_folder_name=$3
mkdir -p "reports/${test_folder_name}"
html_report="reports/${test_folder_name}/$(date '+%Y.%m.%d-%H.%M.%S')-${test_bed}-${test_data}.html"
xoption=""

if [ "$test_bed" != "-" ]; then
  echo " !!! Using test bed: $test_bed"
  xoption+="-XtestBed=$test_bed "
fi
if [ "$test_data" != "-" ]; then
  echo " !!! Using test data: $test_data"
  xoption+="-XtestData=$test_data "
fi

set -x
$python $xoption -m pytest \
  --show-capture=stderr --capture=tee-sys -v --html="$html_report" --self-contained-html $4
