#!/usr/bin/env bash

############# DECLARE #############
function stop_highway() {
  kill $(cat pid_list) || echo
}

function clear_logs() {
  echo Clear logs: $clearLogs
  echo " !!! clear logs"
  rm logs/* -Rf || echo
}

function build() {
  cat <<EOF
----------------------------------------------------------------------
|-------------------        BUILD HIGHWAY       ---------------------|
----------------------------------------------------------------------

EOF

  go build -o highway
}

function start_highway() {
  cat <<EOF
----------------------------------------------------------------------
|-------------------        START HIGHWAY       ---------------------|
----------------------------------------------------------------------

EOF

  privateKeys=($privateKeys)
  keyLen=${#privateKeys[@]}

  declare -a pid_list

  mkdir -p logs || echo
  export BUILD_ID=dontKillMe
  export JENKINS_NODE_COOKIE=dontKillMe

  for i in $(seq 0 $(expr $keyLen - 1)); do
    key=${privateKeys[$i]}
    command=(./highway
      -admin_port $(expr $firstAdminPort + $i)
      -proxy_port $(expr $firstProxyPort + $i)
      -bootnode_port $(expr $firstBootnodePort + $i)
      --bootstrap \"$bootstrapAddr:$firstBootstrapPort\"
      -privateseed $key
      --index $i
      -support_shards all
      -host "$host"
      --loglevel debug
      --gdburl ${GDBURL}
      --version "0.1-local")

    ${command[*]} >>logs/highway0$i.log 2>&1 &

    printf "${command[*]} &\n\n"
    pid_list+=($!)
    sleep 1

  done
  echo ${pid_list[*]} >pid_list
}

############# MAIN #############
IFS=',' read -r -a array <<<"$Additional"
for element in "${array[@]}"; do
  case $element in
  "rebuild")
    build
    ;;
  "clearLogs")
    clear_logs
    ;;
  "clearData")
    echo "Clear chain's data, nothing for highway to do"
    ;;
  *)
    echo "Nothing in additional"
    ;;
  esac
done

case $Action in
"start")
  start_highway
  ;;
"restart")
  stop_highway
  sleep 1
  start_highway
  ;;
"stop")
  stop_highway
  ;;

*)
  echo Nothing
  ;;
esac

cat <<EOF
--------------------------------------------------------------------------------------
PID list: $(cat pid_list)
--------------------------------------------------------------------------------------
EOF
