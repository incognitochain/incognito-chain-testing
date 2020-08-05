package main

import (
	"encoding/json"
	"flag"
	"fmt"

	"github.com/blockcypher/gobcy"
)

func main() {

	txhash := flag.String("txhash", "4b2b1496a6ebc1ac2e20d6dce3b7bb0927c3c8dee69178913474e605829cfb33", "tx BTC")
	flag.Parse()
	
	bc := gobcy.API{"029727206f7e4c8fb19301e4629c5793", "btc", "test3"}
	cypherTx, err := bc.GetTX(*txhash, nil)
	if err != nil {
		txs, _ := bc.GetUnTX()
		txA, _ := json.Marshal(txs)
		fmt.Printf("Tx: %s\n", string(txA))
	} else {
		txB, _ := json.Marshal(cypherTx)
		fmt.Printf("Tx: %s\n", string(txB))
	}
	




}
