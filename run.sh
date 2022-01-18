#!/usr/bin/env bash
# python=./venv/bin/python3
python=python3

if [ $1 = "clear" ] || [ $1 = "clean" ]; then
  rm reports/*.html
  rm logs/*.log*
  exit
elif [[ $CLEAR = "1" ]] || [[ $CLEAN = "1" ]]; then
  rm reports/*.html
  rm logs/*.log*
fi

if [ "$1" != "-" ]; then
  echo " !!! Using test bed: $1"
  export TESTBED=$1
fi
if [ "$2" != "-" ]; then
  echo " !!! Using test data: $2"
  export TESTDATA=$2
fi

param4=""

if [ -z "$4" ]; then
  param4=""
else
  param4="-k $4"
fi

html_report="reports/$(date '+%Y.%m.%d-%H.%M.%S')-${TESTBED}-${TESTDATA}.html"

set -x
$python -m pytest --html="$html_report" --self-contained-html $3 $param4
