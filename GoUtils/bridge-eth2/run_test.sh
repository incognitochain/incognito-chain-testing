#!/bin/bash
mkdir logs 2>/dev/null
file=$(date '+%Y.%m.%d-%H.%M.%S')
go test -timeout 60000s -run TnTradingTestSuite 2>&1  | tee logs/${file}.log
