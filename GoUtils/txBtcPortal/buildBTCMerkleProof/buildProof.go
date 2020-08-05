package main

import (
	"encoding/base64"
	"encoding/json"
	"flag"
	"fmt"

	"github.com/btcsuite/btcd/chaincfg/chainhash"

)


func main() {

	tx := flag.String("txhash", "4478038c54fe1ea19668afc5f088861152cb35559f90ee39024b393a21a612cb", "transacion hash BTC")
	blockHeight := flag.Int("blockHeight", 1, "block height of txhash")

	flag.Parse()

	bc := getBlockCypherAPI("test3")
	txID := *tx
	msgTx := buildMsgTxFromCypher(txID, "test3")

	cypherBlock, err := bc.GetBlock(
		*blockHeight,
		"",
		map[string]string{
			"txstart": "0",
			"limit":   "500",
		},
	)
	cypherBlock2, err := bc.GetBlock(
		*blockHeight,
		"",
		map[string]string{
			"txstart": "500",
			"limit":   "1000",
		},
	)
	if err != nil {
		fmt.Printf("Could not get cypher block by height with err: %v", err)
		return
	}

	//txIDs := cypherBlock.TXids
	txIDs := append(cypherBlock.TXids, cypherBlock2.TXids...)
	txHashes := make([]*chainhash.Hash, len(txIDs))
	for i := 0; i < len(txIDs); i++ {
		txHashes[i], _ = chainhash.NewHashFromStr(txIDs[i])
	}

	txHash := msgTx.TxHash()
	blkHash, _ := chainhash.NewHashFromStr(cypherBlock.Hash)
	merkleProofs := buildMerkleProof(txHashes, &txHash)
	btcProof := BTCProof{
		MerkleProofs: merkleProofs,
		BTCTx:        msgTx,
		BlockHash:    blkHash,
	}
	btcProofBytes, _ := json.Marshal(btcProof)
	btcProofStr := base64.StdEncoding.EncodeToString(btcProofBytes)
	fmt.Println("btcProofStr: ", btcProofStr)

	// verify btc proof
	decodedProof, err := ParseBTCProofFromB64EncodeStr(btcProofStr)
	if err != nil {
		fmt.Printf("Could not parse btc proof from base64 string with err: %v", err)
		return
	}
	merkleRoot, _ := chainhash.NewHashFromStr(cypherBlock.MerkleRoot)
	isValid := verify(merkleRoot, decodedProof.MerkleProofs, &txHash)
	if !isValid {
		fmt.Printf("Failed to verify merkle proofs")
	}

}
