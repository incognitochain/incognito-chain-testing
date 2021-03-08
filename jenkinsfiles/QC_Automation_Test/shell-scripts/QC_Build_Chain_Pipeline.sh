#!/usr/bin/env bash
echo "Script executed from: ${PWD}"
################ DECLARE #################
# abijson must be suround by single quote
#abijson='`[ { "inputs": [ { "internalType": "address", "name": "admin", "type": "address" }, { "internalType": "address", "name": "incognitoProxyAddress", "type": "address" }, { "internalType": "address", "name": "_prevVault", "type": "address" } ], "payable": false, "stateMutability": "nonpayable", "type": "constructor" }, { "anonymous": false, "inputs": [ { "indexed": false, "internalType": "address", "name": "claimer", "type": "address" } ], "name": "Claim", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": false, "internalType": "address", "name": "token", "type": "address" }, { "indexed": false, "internalType": "string", "name": "incognitoAddress", "type": "string" }, { "indexed": false, "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "Deposit", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": false, "internalType": "uint256", "name": "ndays", "type": "uint256" } ], "name": "Extend", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": false, "internalType": "address", "name": "newVault", "type": "address" } ], "name": "Migrate", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": false, "internalType": "address[]", "name": "assets", "type": "address[]" } ], "name": "MoveAssets", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": false, "internalType": "address", "name": "pauser", "type": "address" } ], "name": "Paused", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": false, "internalType": "address", "name": "pauser", "type": "address" } ], "name": "Unpaused", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": false, "internalType": "address", "name": "newIncognitoProxy", "type": "address" } ], "name": "UpdateIncognitoProxy", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": false, "internalType": "address[]", "name": "assets", "type": "address[]" }, { "indexed": false, "internalType": "uint256[]", "name": "amounts", "type": "uint256[]" } ], "name": "UpdateTokenTotal", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": false, "internalType": "address", "name": "token", "type": "address" }, { "indexed": false, "internalType": "address", "name": "to", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "Withdraw", "type": "event" }, { "payable": true, "stateMutability": "payable", "type": "fallback" }, { "constant": true, "inputs": [], "name": "ETH_TOKEN", "outputs": [ { "internalType": "address", "name": "", "type": "address" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "admin", "outputs": [ { "internalType": "address", "name": "", "type": "address" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "address", "name": "token", "type": "address" } ], "name": "balanceOf", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [], "name": "claim", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "string", "name": "incognitoAddress", "type": "string" } ], "name": "deposit", "outputs": [], "payable": true, "stateMutability": "payable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "address", "name": "token", "type": "address" }, { "internalType": "uint256", "name": "amount", "type": "uint256" }, { "internalType": "string", "name": "incognitoAddress", "type": "string" } ], "name": "depositERC20", "outputs": [], "payable": true, "stateMutability": "payable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "address", "name": "token", "type": "address" }, { "internalType": "uint256", "name": "amount", "type": "uint256" }, { "internalType": "address", "name": "recipientToken", "type": "address" }, { "internalType": "address", "name": "exchangeAddress", "type": "address" }, { "internalType": "bytes", "name": "callData", "type": "bytes" }, { "internalType": "bytes", "name": "timestamp", "type": "bytes" }, { "internalType": "bytes", "name": "signData", "type": "bytes" } ], "name": "execute", "outputs": [], "payable": true, "stateMutability": "payable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "address[]", "name": "tokens", "type": "address[]" }, { "internalType": "uint256[]", "name": "amounts", "type": "uint256[]" }, { "internalType": "address[]", "name": "recipientTokens", "type": "address[]" }, { "internalType": "address", "name": "exchangeAddress", "type": "address" }, { "internalType": "bytes", "name": "callData", "type": "bytes" }, { "internalType": "bytes", "name": "timestamp", "type": "bytes" }, { "internalType": "bytes", "name": "signData", "type": "bytes" } ], "name": "executeMulti", "outputs": [], "payable": true, "stateMutability": "payable", "type": "function" }, { "constant": true, "inputs": [], "name": "expire", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "uint256", "name": "n", "type": "uint256" } ], "name": "extend", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "address", "name": "token", "type": "address" } ], "name": "getDecimals", "outputs": [ { "internalType": "uint8", "name": "", "type": "uint8" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "address", "name": "token", "type": "address" }, { "internalType": "address", "name": "owner", "type": "address" } ], "name": "getDepositedBalance", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "incognito", "outputs": [ { "internalType": "contract Incognito", "name": "", "type": "address" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "bytes32", "name": "hash", "type": "bytes32" } ], "name": "isSigDataUsed", "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "bytes32", "name": "hash", "type": "bytes32" } ], "name": "isWithdrawed", "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "address payable", "name": "_newVault", "type": "address" } ], "name": "migrate", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "address[]", "name": "assets", "type": "address[]" } ], "name": "moveAssets", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [], "name": "newVault", "outputs": [ { "internalType": "address payable", "name": "", "type": "address" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "bytes", "name": "inst", "type": "bytes" } ], "name": "parseBurnInst", "outputs": [ { "internalType": "uint8", "name": "", "type": "uint8" }, { "internalType": "uint8", "name": "", "type": "uint8" }, { "internalType": "address", "name": "", "type": "address" }, { "internalType": "address payable", "name": "", "type": "address" }, { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "pure", "type": "function" }, { "constant": false, "inputs": [], "name": "pause", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [], "name": "paused", "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "prevVault", "outputs": [ { "internalType": "contract Withdrawable", "name": "", "type": "address" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "string", "name": "incognitoAddress", "type": "string" }, { "internalType": "address", "name": "token", "type": "address" }, { "internalType": "uint256", "name": "amount", "type": "uint256" }, { "internalType": "bytes", "name": "signData", "type": "bytes" }, { "internalType": "bytes", "name": "timestamp", "type": "bytes" } ], "name": "requestWithdraw", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "address", "name": "_successor", "type": "address" } ], "name": "retire", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "bytes32", "name": "", "type": "bytes32" } ], "name": "sigDataUsed", "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "bytes", "name": "signData", "type": "bytes" }, { "internalType": "bytes32", "name": "hash", "type": "bytes32" } ], "name": "sigToAddress", "outputs": [ { "internalType": "address", "name": "", "type": "address" } ], "payable": false, "stateMutability": "pure", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "bytes", "name": "inst", "type": "bytes" }, { "internalType": "uint256[2]", "name": "heights", "type": "uint256[2]" }, { "internalType": "bytes32[][2]", "name": "instPaths", "type": "bytes32[][2]" }, { "internalType": "bool[][2]", "name": "instPathIsLefts", "type": "bool[][2]" }, { "internalType": "bytes32[2]", "name": "instRoots", "type": "bytes32[2]" }, { "internalType": "bytes32[2]", "name": "blkData", "type": "bytes32[2]" }, { "internalType": "uint256[][2]", "name": "sigIdxs", "type": "uint256[][2]" }, { "internalType": "uint8[][2]", "name": "sigVs", "type": "uint8[][2]" }, { "internalType": "bytes32[][2]", "name": "sigRs", "type": "bytes32[][2]" }, { "internalType": "bytes32[][2]", "name": "sigSs", "type": "bytes32[][2]" } ], "name": "submitBurnProof", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [], "name": "successor", "outputs": [ { "internalType": "address", "name": "", "type": "address" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "address", "name": "", "type": "address" } ], "name": "totalDepositedToSCAmount", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [], "name": "unpause", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "address[]", "name": "assets", "type": "address[]" }, { "internalType": "uint256[]", "name": "amounts", "type": "uint256[]" } ], "name": "updateAssets", "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "address", "name": "newIncognitoProxy", "type": "address" } ], "name": "updateIncognitoProxy", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "bytes", "name": "inst", "type": "bytes" }, { "internalType": "uint256[2]", "name": "heights", "type": "uint256[2]" }, { "internalType": "bytes32[][2]", "name": "instPaths", "type": "bytes32[][2]" }, { "internalType": "bool[][2]", "name": "instPathIsLefts", "type": "bool[][2]" }, { "internalType": "bytes32[2]", "name": "instRoots", "type": "bytes32[2]" }, { "internalType": "bytes32[2]", "name": "blkData", "type": "bytes32[2]" }, { "internalType": "uint256[][2]", "name": "sigIdxs", "type": "uint256[][2]" }, { "internalType": "uint8[][2]", "name": "sigVs", "type": "uint8[][2]" }, { "internalType": "bytes32[][2]", "name": "sigRs", "type": "bytes32[][2]" }, { "internalType": "bytes32[][2]", "name": "sigSs", "type": "bytes32[][2]" } ], "name": "withdraw", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "address", "name": "", "type": "address" }, { "internalType": "address", "name": "", "type": "address" } ], "name": "withdrawRequests", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "bytes32", "name": "", "type": "bytes32" } ], "name": "withdrawed", "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ], "payable": false, "stateMutability": "view", "type": "function" } ]`'

buildFolder=inc_bin
keylistRunNode=$keylistRunNode
logFolder=logs/${BUILD_NUMBER}_$(date '+%m%d_%H%M')

mkdir -p $buildFolder/$logFolder || echo
mkdir -p $buildFolder/data || echo

### disable env-var, already config these params in metadata/constants.go
## EthereumLightNodeHost     = common.GetENV("GETH_NAME", "https://kovan.infura.io/v3/12047eb6d7e6439fa3449d00c7694a12")  // address node ethereum
## EthereumLightNodeProtocol = common.GetENV("GETH_PROTOCOL", "")
## EthereumLightNodePort     = common.GetENV("GETH_PORT", "")
# export GETH_NAME=$GETH_NAME
# export GETH_PROTOCOL=$GETH_PROTOCOL
# export GETH_PORT=$GETH_PORT
unset GETH_NAME
unset GETH_PROTOCOL
unset GETH_PORT

function stop_chain {
cat << EOF
----------------------------------------------------------------------
|--------------------         STOP CHAIN       ----------------------|
----------------------------------------------------------------------

EOF
	echo "stop $(cat $buildFolder/pid_list)"
	kill $(cat $buildFolder/pid_list) || echo
    set -x
    pgrep incognito -a
    pgrep highway -a
    set +x
}

function clear_logs {
cat << EOF
----------------------------------------------------------------------
|--------------------         CLEAR LOGS       ----------------------|
----------------------------------------------------------------------

EOF
	#rm $buildFolder/logs/* -Rf || echo
    echo "DO NOT clear log"
}


function clear_data {
cat << EOF
----------------------------------------------------------------------
|--------------------         CLEAR DATA       ----------------------|
----------------------------------------------------------------------

EOF
	set -x
	rm $buildFolder/data/* -Rf || echo
    ls $buildFolder/data/ || echo
    set +x
}



function build {
cat << EOF
----------------------------------------------------------------------
|--------------------        BUILD CHAIN       ----------------------|
----------------------------------------------------------------------
EOF

    # config chain before build
    # if building on MAC OS, it must be: sed -i '.bak'
    set x-
    ### blockchain/constants.go
    sed -i s":TestnetETHContractAddressStr            = \".*\":TestnetETHContractAddressStr = \"$testnetETHContractAddressStr\":" blockchain/constants.go
    sed -i s":TestNetShardCommitteeSize     = .*:TestNetShardCommitteeSize = $shardCommitteeSize:" blockchain/constants.go
    sed -i s":NumberOfFixedBlockValidators  = .*:NumberOfFixedBlockValidators  = $numberOfFixedBlockValidators:" blockchain/constants.go
    sed -i s":TestNetActiveShards           = 8:TestNetActiveShards           = $activeShard:" blockchain/constants.go
    sed -i s":TestnetEpoch            = .*:TestnetEpoch            = $blockPerEpoch:" blockchain/constants.go
    sed -i s":TestnetRandomTime       = .*:TestnetRandomTime       = $randomTime:" blockchain/constants.go
    sed -i s":TestNetMinShardCommitteeSize  = .*:TestNetMinShardCommitteeSize  = $MinShardCommitteeSize:" blockchain/constants.go
    sed -i s":TestNetBeaconCommitteeSize    = .*:TestNetBeaconCommitteeSize    = $BeaconCommitteeSize:" blockchain/constants.go
    sed -i s":TestNetMinBeaconCommitteeSize = .*:TestNetMinBeaconCommitteeSize = $MinBeaconCommitteeSize:" blockchain/constants.go
    sed -i s":var IsTestNet = false:var IsTestNet = true:" blockchain/constants.go
    sed -i s":TestRandom                    = false:TestRandom                    = true:" blockchain/constants.go

    sed -i s":TestnetOffset           = .*:TestnetOffset           = 2:" blockchain/constants.go
    sed -i s":TestnetSwapOffset       = .*:TestnetSwapOffset       = 2:" blockchain/constants.go
    sed -i s":TestnetAssignOffset     = .*:TestnetAssignOffset     = 4:" blockchain/constants.go

    ### blockchain/params.go
    sed -i s":BeaconHeightBreakPointBurnAddr\: .*:BeaconHeightBreakPointBurnAddr\: $beaconHeightBreakPointBurnAddr,:" blockchain/params.go
    sed -i s":ConsensusV2Epoch\: .*,:ConsensusV2Epoch\:               $consensusV2Epoch,:" blockchain/params.go
    sed -i s":ETHRemoveBridgeSigEpoch\: .*,:ETHRemoveBridgeSigEpoch\:   1,:" blockchain/params.go
    sed -i s":BCHeightBreakPointNewZKP\: .*,:BCHeightBreakPointNewZKP\:   1,:" blockchain/params.go


    ### blockchain/processnewstakingtx.go
    # sed -i s"|const ReplaceStakingTxHeight: .*,|const ReplaceStakingTxHeight: $beaconHeightSwitchStakeTX,|" blockchain/processnewstakingtx.go

    ### blockchain/salary.go
    sed -i s"|return (365\.25 \* 24 \* 60 \* 60) \/ blockCreationTimeSeconds|return 400|" blockchain/salary.go


    ### common/constants.go
    sed -i s":MaxShardNumber = 8:MaxShardNumber = $maxShardNumber:" common/constants.go
    sed -i s":BeaconBlockHeighMilestoneForMinTxFeesOnTokenRequirement = .*:BeaconBlockHeighMilestoneForMinTxFeesOnTokenRequirement = \
        $beaconBlockHeighMilestoneForMinTxFeesOnTokenRequirement:" common/constants.go
    #sed -i s"|AbiJson = .*|AbiJson = $abijson|" common/constants.go

    ### metadata/constants.go
  	sed -i s":EthereumLightNodeHost     = .*:EthereumLightNodeHost = common.GetENV\(\"GETH_NAME\", \"https\:\/\/kovan.infura.io/v3/12047eb6d7e6439fa3449d00c7694a12\"\):" metadata/constants.go
    sed -i s":EthereumLightNodeProtocol = .*:EthereumLightNodeProtocol = common.GetENV\(\"GETH_PROTOCOL\", \"\"):" metadata/constants.go
    sed -i s":EthereumLightNodePort     = .*:EthereumLightNodePort = common.GetENV\(\"GETH_PORT\", \"\"\):" metadata/constants.go

    ### change portal setting
    sed -i s"|TimeOutCustodianReturnPubToken: .*|TimeOutCustodianReturnPubToken: 30 * time.Minute,|" blockchain/params.go
    sed -i s"|TimeOutWaitingPortingRequest: .*|TimeOutWaitingPortingRequest: 30 * time.Minute,|" blockchain/params.go
	sed -i s':1580600:1:' blockchain/beaconportalprocess.go # remove chechpoint

    sed -i s"|64fbdbc6bf5b228814b58706d91ed03777f0edf6|3a829f4b97660d970428cd370c4e41cbad62092b|" blockchain/params.go
    sed -i s"|7079f3762805cff9c979a5bdc6f5648bcfee76c8|75b0622cec14130172eae9cf166b92e5c112faff|" blockchain/params.go
    sed -i s"|PortalETHContractAddressStr: .*|PortalETHContractAddressStr: \"0x40d9Fa310F14E33009c8f5ffb3E45e1913b4f88E\",|" blockchain/params.go
    sed -i s"|MinLockCollateralAmountInEpoch: .*|MinLockCollateralAmountInEpoch: 10000 * 1e9,|" blockchain/params.go


    ### compile source code
    rm -rf incognito
    go build -o incognito

    ### copy config
    rm -rf $buildFolder/incognito
    cp -f incognito $buildFolder
    cp -f "sample-config.conf" $buildFolder
    set +x
}

function start_chain {
cat << EOF
----------------------------------------------------------------------
|------------------        STARTING CHAIN         -------------------|
----------------------------------------------------------------------
              >----        STARTING FULLNODE      ----<
             -------------------------------------------
EOF
    cd ${buildFolder}
    ### Change Epoch applying replace committee in keylist.json
    cp -f keylist-newvalkey.json keylist-v2.json
    sed -i s":ABCXYZ:$epochReplaceCommittee:" ./keylist-v2.json

    export BUILD_ID=dontKillMe
    export JENKINS_NODE_COOKIE=dontKillMe
    declare -a pid_list

    #fullnodeRpcPort=$firstRpcPort
    #fullnodeWsPort=$firstWsPort
    firstStakerRpcPort=$firstRpcPort+1000
    firstStakerWsPort=$firstWsPort+1000
    firstStakerListenPort=$firstListenPort+1000
    fullnodeRpcPort=8334
    fullnodeWsPort=18334
    fullnodeListenPort=$firstListenPort

    command=(./incognito \
        --datadir "data/full_node" \
        --rpclisten "$listenAddress:$fullnodeRpcPort" \
        --rpcwslisten "$listenAddress:$fullnodeWsPort" \
        --discoverpeersaddress "$discoverPeersAddress" \
        --listen "$listenAddress:$fullnodeListenPort" \
        --externaladdress "$listenAddress:$fullnodeListenPort" \
        --norpcauth \
        --relayshards "all"  \
        --txpoolmaxtx 100000 \
        --loglevel debug)

    ${command[*]} >> $logFolder/full_node.log 2>&1 &
    printf "${command[*]} &\n\n"

    pid_list+=($!)


cat << EOF
              >----        STARTING BEACONS       ----<
             -------------------------------------------
EOF

    for i in $(seq 0 $(expr $numOfBeacon - 1))
    do
    echo $((++firstWsPort))
    key=$(cat $keylistRunNode | jq '.Beacon'[$i]'.ValidatorKey')
    command=(./incognito \
        --datadir "data/beacon_$i" \
        --rpclisten "$listenAddress:$((++firstRpcPort))" \
        --listen "$listenAddress:$((++firstListenPort))" \
        --miningkeys "$key" \
        --discoverpeersaddress "$discoverPeersAddress" \
        --externaladdress "$listenAddress:$((firstListenPort))" \
        --loglevel debug \
        --norpcauth )

    ${command[*]} >> $logFolder/beacon_${i}.log 2>&1 &
    printf "${command[*]} &\n\n"

    pid_list+=($!)

    done

cat << EOF
              >----        STARTING SHARDS        ----<
             -------------------------------------------
EOF
    for shard in $(seq 0 $(expr $activeShard - 1))
    do
      for node in $(seq 0 $(expr $numOfNodeInShardPreRun - 1))
      do
          qShard=.Shard.\"$shard\"
          key=$(cat $keylistRunNode | jq $qShard[$node]'.ValidatorKey')
          command=(\./incognito \
          --datadir "data/shard${shard}_$node" \
          --rpclisten "$listenAddress:$((++firstRpcPort))" \
          --rpcwslisten "$listenAddress:$((++firstWsPort))"\
          --discoverpeersaddress "$discoverPeersAddress" \
          --miningkeys "$key" \
          --listen "$listenAddress:$((++firstListenPort))" \
          --externaladdress "$listenAddress:$((firstListenPort))" \
          --loglevel debug \
          --norpcauth)

          ${command[*]} >> $logFolder/shard_${shard}_${node}.log 2>&1 &
          printf "${command[*]} &\n\n"

          pid_list+=($!)

      done
    done

cat << EOF
              >----        STARTING STAKERS       ----<
             -------------------------------------------
EOF

    for i in $(seq 0 $(expr $numOfStakerPreRun - 1))
    do
    echo $((++firstStakerWsPort))
    key=$(cat $keylistRunNode | jq '.Staker'[$i]'.ValidatorKey')
    command=(./incognito \
        --datadir "data/staker_$i" \
        --rpclisten "$listenAddress:$((++firstStakerRpcPort))" \
        --listen "$listenAddress:$((++firstStakerListenPort))" \
        --miningkeys "$key" \
        --discoverpeersaddress "$discoverPeersAddress" \
        --externaladdress "$listenAddress:$((firstStakerListenPort))" \
        --loglevel debug \
        --norpcauth )

    ${command[*]} >> $logFolder/staker_${i}.log 2>&1 &
    printf "${command[*]} &\n\n"

    pid_list+=($!)

    done



    # save PID of node and beacon to a file
    echo ${pid_list[*]} > pid_list
}

  ################ MAIN #################

IFS=',' read -r -a array <<< "$Additional"
for element in "${array[@]}"
do
	case $element in
    	"rebuild")
        	build
        	;;
        "clearLogs")
        	clear_logs
        	;;
        "clearData")
        	clear_data
        	;;
        *)
        	echo "Nothing in additional"
        ;;
    esac
done

case $Action in
    "start")
        start_chain
        ;;
    "restart")
        stop_chain
        sleep 1
        start_chain
        ;;
    "stop")
        stop_chain
        ;;
    *)
        echo "Do nothing"
        ;;
esac

cat << EOF
--------------------------------------------------------------------------------------
PID list: $(cat ${buildFolder}/pid_list)
--------------------------------------------------------------------------------------
EOF