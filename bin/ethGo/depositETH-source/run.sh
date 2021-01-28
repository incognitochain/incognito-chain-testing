#!/bin/bash

# run incognito chain
cd /go/incognito-chain && ./run_node.sh shard0-0 &
cd /go/incognito-chain && ./run_node.sh shard0-1 &
cd /go/incognito-chain && ./run_node.sh shard0-2 &
cd /go/incognito-chain && ./run_node.sh shard0-3 &

cd /go/incognito-chain && ./run_node.sh shard1-0 &
cd /go/incognito-chain && ./run_node.sh shard1-1 &
cd /go/incognito-chain && ./run_node.sh shard1-2 &
cd /go/incognito-chain && ./run_node.sh shard1-3 &

cd /go/incognito-chain && ./run_node.sh beacon-0 &
cd /go/incognito-chain && ./run_node.sh beacon-1 &
cd /go/incognito-chain && ./run_node.sh beacon-2 &
cd /go/incognito-chain && ./run_node.sh beacon-3 &
cd /go/incognito-highway && ./run.sh local
