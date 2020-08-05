package main

import (

	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"

	"github.com/btcsuite/btcd/txscript"
	"github.com/blockcypher/gobcy"
	relaying "github.com/incognitochain/incognito-chain/relaying/btc"
	
)

func getBlockCypherAPI(networkName string) gobcy.API {
	//explicitly
	bc := gobcy.API{}
	bc.Token = "029727206f7e4c8fb19301e4629c5793"
	bc.Coin = "btc"        //options: "btc","bcy","ltc","doge"
	bc.Chain = networkName //depending on coin: "main","test3","test"
	return bc
}

func main() {

	outAdd1Str := flag.String("outAdd1", "n4UtqQiW3qYjtiEUMscwPoBtUuYAK1AqKJ", "address output 1")
	amount1Int := flag.Int("amtAdd1", 1, "amount send for outAdd1")
	outAdd2Str := flag.String("outAdd2", "n4UtqQiW3qYjtiEUMscwPoBtUuYAK1AqKJ", "address output 2")
	amount2Int := flag.Int("amtAdd2", 1, "amount send for outAdd2")
	outAdd3Str := flag.String("outAdd3", "n4UtqQiW3qYjtiEUMscwPoBtUuYAK1AqKJ", "address output 3")
	amount3Int := flag.Int("amtAdd3", 1, "amount send for outAdd3")
	portingID := flag.String("portingId", "0000", "Porting ID")

	flag.Parse()

	// bc := gobcy.API{"029727206f7e4c8fb19301e4629c5793", "bcy", "test"}
	bc := getBlockCypherAPI("test3")

	inAddr := "miERaVjAsBriPmAEHSkfymRUo3xjaEoM2r"
	outAddr1 := *outAdd1Str
	amount1 := *amount1Int
	outAddr2 := *outAdd2Str
	amount2 := *amount2Int
	outAddr3 := *outAdd3Str
	amount3 := *amount3Int
	trans := gobcy.TX{}
	trans.Fees = int(5000)
	trans.Inputs = make([]gobcy.TXInput, 1)
	trans.Inputs[0].Addresses = make([]string, 1)
	trans.Inputs[0].Addresses[0] = inAddr

	trans.Outputs = make([]gobcy.TXOutput, 4)
	trans.Outputs[0].ScriptType = "null-data"
	script := []byte{
		txscript.OP_RETURN,
		0x10,
	}

	uniquePortingID := *portingID
	msg := relaying.HashAndEncodeBase58(uniquePortingID)
	fmt.Println("hashed msg: ", msg)
	script = append(script, []byte(msg)...)
	trans.Outputs[0].Script = hex.EncodeToString(script)

	trans.Outputs[1].Addresses = make([]string, 1)
	trans.Outputs[1].Addresses[0] = outAddr1
	trans.Outputs[1].Value = amount1

	trans.Outputs[2].Addresses = make([]string, 1)
	trans.Outputs[2].Addresses[0] = outAddr2
	trans.Outputs[2].Value = amount2

	trans.Outputs[3].Addresses = make([]string, 1)
	trans.Outputs[3].Addresses[0] = outAddr3
	trans.Outputs[3].Value = amount3

	skelTx, err := bc.NewTX(trans, false)
	if err != nil {
		fmt.Printf("Could not init btc tx by using cypher api - with err: %v", err)
		return
	}
	privateKeys := []string{"55998164c6783126036f3eeee1fcbbc6a9dfa9424ec4ad3a83e4674e52e37fd7"}
	
	numPri := len(privateKeys)
	numPriToSig :=len(skelTx.ToSign)
	if numPriToSig > numPri {
		for i := 0; i < numPriToSig - numPri; i++{
			privateKeys = append(privateKeys,"55998164c6783126036f3eeee1fcbbc6a9dfa9424ec4ad3a83e4674e52e37fd7")
		}
	}

	err = skelTx.Sign(privateKeys)
	if err != nil {
		fmt.Printf("Could not sign btc tx by using cypher api - with err: %v", err)
		return
	}
	
	tx, err := bc.SendTX(skelTx)
	if err != nil {
		fmt.Printf("Could not send btc tx by using cypher api - with err: %v", err)
		return
	}
	bb, _ := json.Marshal(tx)
	fmt.Println("Newly created tx: ", string(bb))
}
