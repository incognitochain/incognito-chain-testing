package main

import (
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"

	"github.com/blockcypher/gobcy"
	"github.com/btcsuite/btcd/txscript"
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

	userAddStr := flag.String("userAdd", "n4UtqQiW3qYjtiEUMscwPoBtUuYAK1AqKJ", "address BTC of user")
	amountInt := flag.Int("amt", 1, "amount send for user")
	custIncAddStr := flag.String("custIncAdd", "12S5Lrs1XeQLbqN4ySyKtjAjd2d7sBP2tjFijzmp6avrrkQCNFMpkXm3FPzj2Wcu2ZNqJEmh9JriVuRErVwhuQnLmWSaggobEWsBEci", "incognito custodian address")
	redeemID := flag.String("redeemId", "0000", "Redeem ID")

	flag.Parse()

	// bc := gobcy.API{"029727206f7e4c8fb19301e4629c5793", "bcy", "test"}
	bc := getBlockCypherAPI("test3")

	inAddr := "miERaVjAsBriPmAEHSkfymRUo3xjaEoM2r"
	outAddr := *userAddStr
	amount := *amountInt

	trans := gobcy.TX{}
	trans.Fees = int(5000)
	trans.Inputs = make([]gobcy.TXInput, 1)
	trans.Inputs[0].Addresses = make([]string, 1)
	trans.Inputs[0].Addresses[0] = inAddr

	trans.Outputs = make([]gobcy.TXOutput, 2)
	trans.Outputs[0].ScriptType = "null-data"
	script := []byte{
		txscript.OP_RETURN,
		0x10,
	}

	rawMsg := fmt.Sprintf("%s%s", *redeemID, *custIncAddStr)
	msg := relaying.HashAndEncodeBase58(rawMsg)
	fmt.Println("hashed msg: ", msg)
	script = append(script, []byte(msg)...)
	trans.Outputs[0].Script = hex.EncodeToString(script)

	trans.Outputs[1].Addresses = make([]string, 1)
	trans.Outputs[1].Addresses[0] = outAddr
	trans.Outputs[1].Value = amount

	skelTx, err := bc.NewTX(trans, false)
	if err != nil {
		fmt.Printf("Could not init btc tx by using cypher api - with err: %v", err)
		return
	}
	privateKeys := []string{"55998164c6783126036f3eeee1fcbbc6a9dfa9424ec4ad3a83e4674e52e37fd7"}

	numPri := len(privateKeys)
	numPriToSig := len(skelTx.ToSign)
	if numPriToSig > numPri {
		for i := 0; i < numPriToSig-numPri; i++ {
			privateKeys = append(privateKeys, "55998164c6783126036f3eeee1fcbbc6a9dfa9424ec4ad3a83e4674e52e37fd7")
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
