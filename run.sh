#!/usr/bin/env bash
python=python3
runShVer="2022.01"

if [[ -n $PYTHON ]]; then
  python=$PYTHON
fi


if [[ $1 == "clear" ]] || [[ $1 == "clean" ]]; then
  rm reports/*.html
  rm logs/*.log*
  exit
elif [[ $CLEAR == "1" ]] || [[ $CLEAN == "1" ]]; then
  rm reports/*.html
  rm logs/*.log*
fi

more_header=""
if [ "$1" != "-" ]; then
  more_header+="Test bed: $1. "
  export TESTBED=$1
fi
if [ "$2" != "-" ]; then
  more_header+="Test data: $2. "
  export TESTDATA=$2
fi
cat <<EOF
===============================================================================
|| $(basename "$0") version $runShVer
|| $more_header
===============================================================================
EOF

param4=""
if [ -z "$4" ]; then
  param4=""
else
  param4="-k $4"
fi

html_report="reports/$(date '+%Y.%m.%d-%H.%M.%S')-${TESTBED}-${TESTDATA}.html"
$python -m pytest --html="$html_report" --self-contained-html $3 $param4
