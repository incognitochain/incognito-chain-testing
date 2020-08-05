package main

import (
	"fmt"
	"flag"

	"github.com/incognitochain/incognito-chain/incognitokey"

	"github.com/incognitochain/incognito-chain/common"
	"github.com/incognitochain/incognito-chain/common/base58"
	"github.com/incognitochain/incognito-chain/wallet"
)

func main() {

	privateKeyString := flag.String("privatekey", "112t8rnnxuVr3YqWE5ejUT7QTjKmfpXnxbqjS8oWP1T42rfPAqoc58j1N5nF8HjB9AXdeum4RfYNziuQyhDqaVhFBXD2KMFxApAzrhz61qFX", "Private Key ")

	flag.Parse()

	// generate inc key
	privateKey := *privateKeyString
	keyWallet, err := wallet.Base58CheckDeserialize(privateKey)
	if err != nil {
		fmt.Printf("err: %v", err)
		return
	}
	err = keyWallet.KeySet.InitFromPrivateKeyByte(keyWallet.KeySet.PrivateKey)
	if err != nil {
		fmt.Printf("err: %v", err)
		return
	}

	// calculate private seed
	privateSeedBytes := common.HashB(common.HashB(keyWallet.KeySet.PrivateKey))
	committeePubKey, err := incognitokey.NewCommitteeKeyFromSeed(privateSeedBytes, keyWallet.KeySet.PaymentAddress.Pk)
	if err != nil {
		fmt.Printf("err: %v", err)
		return
	}
	committeeKeyStr, err := committeePubKey.ToBase58()
	if err != nil {
		fmt.Printf("err: %v", err)
		return
	}

	// print result
	privateKeyStr := keyWallet.Base58CheckSerialize(wallet.PriKeyType)
	paymentAddrStr := keyWallet.Base58CheckSerialize(wallet.PaymentAddressType)
	readOnlyKeyStr := keyWallet.Base58CheckSerialize(wallet.ReadonlyKeyType)
	publicKey := base58.Base58Check{}.Encode(keyWallet.KeySet.PaymentAddress.Pk, 0x00)

	privateSeedStr := base58.Base58Check{}.Encode(privateSeedBytes, common.Base58Version)
	miningKey, _ := committeePubKey.GetMiningKey(common.BlsConsensus)
	miningKeyStr := base58.Base58Check{}.Encode(miningKey, common.Base58Version)

	shardID := common.GetShardIDFromLastByte(keyWallet.KeySet.PaymentAddress.Pk[len(keyWallet.KeySet.PaymentAddress.Pk) - 1])

	fmt.Println("Incognito Private Key: ", privateKeyStr)
	fmt.Println("Incognito Public Key: ", publicKey)
	fmt.Println("Incognito Payment Address: ", paymentAddrStr)
	fmt.Println("Incognito Viewing Key (ReadOnlykey): ", readOnlyKeyStr)
	fmt.Println("ShardID of Incognito account: ", shardID)

	fmt.Println("Private Seed (Validatorkey):         ", privateSeedStr)
	fmt.Println("BLS public key:       ", committeePubKey.GetMiningKeyBase58(common.BlsConsensus))
	fmt.Println("Bridge public key:    ", committeePubKey.GetMiningKeyBase58(common.BridgeConsensus))
	fmt.Println("Mining Public Key (BLS+DSA): ", miningKeyStr)
	fmt.Println("Committee Public Key: ", committeeKeyStr)

}
