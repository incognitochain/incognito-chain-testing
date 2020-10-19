#!/usr/bin/env bash
# python=./venv/bin/python3
python=python3
html_report="reports/$(date '+%Y.%m.%d-%H.%M.%S')-sanity.html"

url='https://164.90.180.0:29334'
wsPort=39334

if [ -n "$1" ]; then
  url=$1
  echo here
fi

if [ -n "$2" ]; then
  wsPort=$2
  echo here
fi

set -x
$python -XskipLoad -XprepareCoin -XfullNodeUrl="$url" -XwsPort="$wsPort" \
  -m pytest --show-capture=no -s -v --html="$html_report" --self-contained-html \
  IncognitoChain/TestCases/Sanity/
