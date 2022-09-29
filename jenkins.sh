#!/usr/bin/env bash

################ DECLARE #################

buildFolder=inctest
logFolder=logs/${BUILD_NUMBER}
configDir=$buildFolder/config/$INCOGNITO_NETWORK_KEY

yamlParamFile=$configDir/param.yaml
yamlConfigFile=$configDir/config.yaml
unifiedTokenParamFile=$configDir/unified_token.json

keyListV2File=config/local/keylist-v2.json
keyListFile=config/local/keylist.json

firstStakerRpcPort=$firstRpcPort+1000
firstStakerWsPort=$firstWsPort+1000
firstStakerListenPort=$firstListenPort+1000

firstmStakerRpcPort=$firstRpcPort+2000
firstmStakerWsPort=$firstWsPort+2000
firstmStakerListenPort=$firstListenPort+2000

fullnodeListenPort=$firstListenPort
firstProfilingPort=11110

set -x
mkdir -p $configDir || echo
cp -Rf config/$INCOGNITO_NETWORK_KEY $buildFolder/config
set +x
if [[ -z $keyList ]]; then
  echo "!!! Using exiting keylist.json file"
  wget -O $buildFolder/$keyListFile "https://raw.githubusercontent.com/incognitochain/incognito-chain-testing/dev/keylist.json"
else
  echo "!!! Create keylist.json file"
cat > $keyListFile <<-EOF
$yamlParam
EOF
fi

if [[ -z $yamlParam ]]; then
  echo "!!! Using exiting YAML param file"
else
  echo "!!! Create YAML param file"
cat > $yamlParamFile <<-EOF
$yamlParam
EOF
fi

if [[ -z $yamlConfig ]]; then
  echo "!!! Using exiting YAML config file"
else
  echo "!!! Create YAML config file"
cat > $yamlConfigFile <<-EOF
$yamlConfig
EOF
fi

if [[ -z $unifiedTokenParam ]]; then
  echo "!!! Using exiting unified_token.json"
else
  echo "!!! Create new unified_token.json"
cat > $unifiedTokenParamFile <<-EOF
$unifiedTokenParam
EOF
fi

activeShard=$(grep "active_shards" $yamlParamFile | cut -d ' ' -f 2)
numOfFixNode=$(grep "number_of_fixed_shard_block_validators" $yamlParamFile | cut -d ':' -f 2 | tr -d " ")
numOfBeacon=$(grep "min_beacon_committee_size" $yamlParamFile | cut -d ':' -f 2 | tr -d " ")
unset GETH_NAME
unset GETH_PROTOCOL
unset GETH_PORT

BIN=incognito.${branch//\//.}

function keyListGet {
    list=$1
    type=$2
    index=$3
    if [[ -z $4 ]]; then numKeyToGet=1; else numKeyToGet=$4; fi
    case $type in
        "miningkeys")
            key=$(cat $keyListFile | jq '.'$list[$index]'.ValidatorKey')
            ;;
        "privatekey")
            key=$(cat $keyListFile | jq '.'$list[$index]'.PrivateKey')
            ;;
        ?)
            key=$(cat $keyListFile | jq $list)
            ;;
    esac

    check=($key)
    if [ ${check[-1]} == null ]; then
        echo "keylist.json error: please check $list $i, $type"
        # exit 10
    else
        echo $key
    fi
}

function stop_chain {
cat << EOF
----------------------------------------------------------------------
|--------------------         STOP CHAIN       ----------------------|
----------------------------------------------------------------------

EOF
    set -x
	pkill incognito && sleep 5
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
	rm $buildFolder/logs/* -Rf
    echo "ALL LOGS ARE DELETED !!"
}

function clear_consensus {
cat << EOF
----------------------------------------------------------------------
|---------------         CLEAR CONSENSUS DATA       -----------------|
----------------------------------------------------------------------

EOF

    rm $buildFolder/data/*/local/consensus/ -Rf

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
   set -x
   eval "$sedConfig"

   ### compile source code
   rm -rf $BIN
   go build -o $BIN

   ### copy config
   rm -rf "$buildFolder/$BIN"
   cp -f "$BIN" "$buildFolder"
   ls $keyListFile
   set +x
}

function start_chain {
mkdir -p $buildFolder/$logFolder || echo
cat << EOF
----------------------------------------------------------------------
|------------------        STARTING CHAIN         -------------------|
----------------------------------------------------------------------
              >----        STARTING FULLNODE      ----<
             -------------------------------------------
EOF
    cd ${buildFolder}

    command="Profiling=$firstProfilingPort ./$BIN \
        --datadir data/full_node \
        --rpclisten $listenAddress:$firstRpcPort \
        --rpcwslisten $listenAddress:$firstWsPort \
        --discoverpeersaddress $discoverPeersAddress \
        --listen $listenAddress:$fullnodeListenPort \
        --externaladdress $listenAddress:$fullnodeListenPort \
        --norpcauth --backup\
        --relayshards all  \
        --txpoolmaxtx 100000 \
		--usecoindata --coindatapre=__coins__ --numindexerworkers=100 \
        --indexeraccesstoken=0c3d46946bbf99c8213dd7f6c640ed6433bdc056a5b68e7e80f5525311b0ca11 \
        --numindexerworkers=100 \
        --loglevel debug \
        2> $logFolder/full_node.error | cronolog $logFolder/full_node-%Y-%m-%d.log &"

    eval $command
    echo $command
    echo
    ((firstProfilingPort++))


cat << EOF
              >----        STARTING BEACONS       ----<
             -------------------------------------------
EOF
    for i in $(seq 0 $(($numOfBeacon - 1))); do
        key=$(keyListGet Beacon $keyType $i)
        command="Profiling=$firstProfilingPort ./$BIN \
            --datadir data/beacon_$i \
            --rpclisten $listenAddress:$((++firstRpcPort)) \
            --listen $listenAddress:$((++firstListenPort)) \
            --rpcwslisten $listenAddress:$((++firstWsPort)) \
            --$keyType $key \
            --discoverpeersaddress $discoverPeersAddress \
            --externaladdress $listenAddress:$((firstListenPort)) \
            --loglevel debug \
            --norpcauth \
            2> $logFolder/beacon_${i}.error | cronolog $logFolder/beacon_${i}-%Y-%m-%d.log &"

        eval $command
        echo $command
        echo
        ((firstProfilingPort++))

    done

cat << EOF
              >----        STARTING SHARDS        ----<
             -------------------------------------------
EOF
    for shard in $(seq 0 $(($activeShard - 1))); do
        echo " ### STARTING SHARDS $shard ###"
        shardKeys=($(keyListGet Shard.\"$shard\" miningkeys))

        if [[ $numOfFixNodeMultikeyEachShard -gt 0 ]]; then
            echo " # Starting multikey fix node shard $shard # "
            shard_mkey=$(echo "${shardKeys[@]:0:$numOfFixNodeMultikeyEachShard}" | tr -d "\"" | tr " " ,)
            command="Profiling=$firstProfilingPort ./$BIN \
            --datadir data/shard_${shard}m \
            --rpclisten $listenAddress:$((++firstRpcPort)) \
            --rpcwslisten $listenAddress:$((++firstWsPort)) \
            --discoverpeersaddress $discoverPeersAddress \
            --miningkeys ${shard_mkey%,} \
            --listen $listenAddress:$((++firstListenPort)) \
            --externaladdress $listenAddress:$((firstListenPort)) \
            --loglevel debug \
            --usecoindata --coindatapre=__coins__ \
            --numindexerworkers=100 \
            --norpcauth \
            2>$logFolder/shard_${shard}m.error | cronolog $logFolder/shard_${shard}m-%Y-%m-%d.log &"
            eval $command
            echo $command
            echo
            ((firstProfilingPort++))
        fi

        echo " # Starting single key fix nodes shard $shard # "
            for node in $(seq $numOfFixNodeMultikeyEachShard $(($numOfFixNode - 1))); do
                command="Profiling=$firstProfilingPort ./$BIN \
                --datadir data/shard_${shard}_$node \
                --rpclisten $listenAddress:$((++firstRpcPort)) \
                --rpcwslisten $listenAddress:$((++firstWsPort))\
                --discoverpeersaddress $discoverPeersAddress \
                --$keyType ${shardKeys[$node]} \
                --listen $listenAddress:$((++firstListenPort)) \
                --externaladdress $listenAddress:$((firstListenPort)) \
                --loglevel debug \
                --usecoindata --coindatapre=__coins__ \
                --numindexerworkers=100 \
                --norpcauth \
                2>$logFolder/shard_${shard}_${node}.error | cronolog $logFolder/shard_${shard}_${node}-%Y-%m-%d.log &"
                eval $command
                echo $command
                echo
                ((firstProfilingPort++))
            done
    done

cat << EOF
              >----        STARTING STAKERS       ----<
             -------------------------------------------
EOF
    numTotalStaker=$(echo $numOfStakerPreRun | cut -d ',' -f1)
    numMultikeyStaker=$(echo $numOfStakerPreRun | cut -d ',' -f2)
    numSiglekeyStaker=$((numTotalStaker-numMultikeyStaker))
    stakerKeys=($(keyListGet Staker $keyType))
    
    mKeys=$(echo "${stakerKeys[@]:0:$numMultikeyStaker}" | tr -d "\"" | tr " " ,)
    command="Profiling=$firstProfilingPort ./$BIN \
        --datadir data/mstaker \
        --rpclisten $listenAddress:$((++firstStakerRpcPort)) \
        --rpcwslisten $listenAddress:$((++firstWsPort))\
        --listen $listenAddress:$((++firstStakerListenPort)) \
        --$keyType $mKeys\
        --discoverpeersaddress $discoverPeersAddress \
        --externaladdress $listenAddress:$((firstStakerListenPort)) \
        --loglevel debug \
        --usecoindata --coindatapre=__coins__ \
        --numindexerworkers=100 \
        --norpcauth \
        2> $logFolder/mstaker.error | cronolog $logFolder/mstaker-%Y-%m-%d.log &"
    eval $command
    echo $command
    ((firstProfilingPort++))

    count=0
    while [[ $count -lt numSiglekeyStaker ]] ; do
        index=$((count+numMultikeyStaker))
        command="Profiling=$firstProfilingPort ./$BIN \
            --datadir data/staker_$index \
            --rpclisten $listenAddress:$((++firstStakerRpcPort)) \
            --rpcwslisten $listenAddress:$((++firstWsPort))\
            --listen $listenAddress:$((++firstStakerListenPort)) \
            --$keyType ${stakerKeys[$index]} \
            --discoverpeersaddress $discoverPeersAddress \
            --externaladdress $listenAddress:$((firstStakerListenPort)) \
            --loglevel debug \
            --usecoindata --coindatapre=__coins__ \
            --numindexerworkers=100 \
            --norpcauth \
            2> $logFolder/staker_${index}.error | cronolog $logFolder/staker_${index}-%Y-%m-%d.log &"
        eval $command
        echo $command
        ((firstProfilingPort++))
        ((count++))
    done


}

  ################ MAIN #################

ActionArr=(${Actions//,/ })
for element in "${ActionArr[@]}"; do
	case ${element,,} in
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
    	"rebuild"|"build")
        	build
        	;;
        "clearlogs")
        	clear_logs
        	;;
        "cleardata")
        	clear_data
        	;;
        "clearcons")
            clear_consensus
            ;;
        *)
        	echo "Do nothing"
        ;;
    esac
done

