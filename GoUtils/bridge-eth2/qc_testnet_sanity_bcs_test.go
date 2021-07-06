package main

import (
	"context"
	"crypto/ecdsa"
	"encoding/json"
	"errors"
	"fmt"
	"math/big"

	// "github.com/incognitochain/bridge-eth/bridge/incognito_proxy"

	// "math/rand"
	"strings"
	"testing"
	"time"

	"github.com/incognitochain/bridge-eth/bridge/vault"
	"github.com/incognitochain/bridge-eth/common/base58"
	"github.com/incognitochain/bridge-eth/consensus/signatureschemes/bridgesig"
	"github.com/stretchr/testify/suite"

	// "golang.org/x/crypto/sha3"

	"github.com/ethereum/go-ethereum/accounts/abi"
	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/ethereum/go-ethereum/params"

	// "github.com/ethereum/go-ethereum/rlp"

	"github.com/incognitochain/bridge-eth/erc20"
	"github.com/incognitochain/bridge-eth/rpccaller"
	"github.com/stretchr/testify/require"

)

const (
	BEP20WaitTn     = 12
	BSCWaiting = 100
	INCWating     = 100


)
type TnSubmitkey struct {
	rpccaller.RPCBaseRes
	Result interface{} `json:"Result"`
}

type Tnconvertcoinver1tover2 struct {
	rpccaller.RPCBaseRes
	Result interface{} `json:"Result"`
}

type TnIssuingBSCRes struct {
	rpccaller.RPCBaseRes
	Result interface{} `json:"Result"`
}

type TnBSCTestSuite struct {
	suite.Suite
	IncBurningAddrStr      string
	IncPrivKeyStr          string
	IncPaymentAddrStr      string
	IncPrivaKeyReceiverStr string
	IncPaymentReceiverStr  string

	GeneratedPrivKeyForSC ecdsa.PrivateKey
	GeneratedPubKeyForSC  ecdsa.PublicKey

	IncBNBTokenIDStr string

	IncBridgeHost string
	IncRPCHost    string

	BNBAddressStr string

	BEP20PrivKeyStr   string
	BEP20OwnerAddrStr string

	BinanceHost    string
	BEP20PrivKey *ecdsa.PrivateKey
	BEP20Client  *ethclient.Client

	VaultAddr      common.Address
	IncognitoProxy common.Address
	WETHAddr             common.Address

	IncETHTokenIDStr string
	IncFAKETokenIDStr string

	ETHAddressStr string
	FAKEAddressStr string
	WETHAddressStr string

	DepositingBNB float64
	DepositETH     float64

	auth *bind.TransactOpts
	v    *vault.Vault
}

// Make sure that VariableThatShouldStartAtFive is set to five
// before each test
func (tradingSuite *TnBSCTestSuite) SetupSuite() {
	fmt.Println("Setting up the suite...")

	tradingSuite.IncBurningAddrStr = "12RxahVABnAVCGP3LGwCn8jkQxgw7z1x14wztHzn455TTVpi1wBq9YGwkRMQg3J4e657AbAnCvYCJSdA9czBUNuCKwGSRQt55Xwz8WA"
	tradingSuite.IncPrivKeyStr = "112t8roafGgHL1rhAP9632Yef3sx5k8xgp8cwK4MCJsCL1UWcxXvpzg97N4dwvcD735iKf31Q2ZgrAvKfVjeSUEvnzKJyyJD3GqqSZdxN4or" // shard 0
	tradingSuite.IncPaymentAddrStr = "12S5Lrs1XeQLbqN4ySyKtjAjd2d7sBP2tjFijzmp6avrrkQCNFMpkXm3FPzj2Wcu2ZNqJEmh9JriVuRErVwhuQnLmWSaggobEWsBEci"
	tradingSuite.IncPrivaKeyReceiverStr = "112t8rnendREF3cg2vuRC248dFymXonwBC7TMmfppXEzz9wFziktHj8NhsGebcRmtquyg2zbytkecPMSHFBVcw4yJewv7E3J6cHgDzYiHoJj" // shard 4
	tradingSuite.IncPaymentReceiverStr = "12S4YzSA6hC12zuMF8L2rC7Tks1TtcfDUSWjcPeKeyT1ApV1KXqQnmtpCNEYbta88GrjhPiS6yFfuyfViDW5cmooqsZ5tvC8SRJZdCF"

	// tradingSuite.IncBurningAddrStr = "12RxahVABnAVCGP3LGwCn8jkQxgw7z1x14wztHzn455TTVpi1wBq9YGwkRMQg3J4e657AbAnCvYCJSdA9czBUNuCKwGSRQt55Xwz8WA"
	// tradingSuite.IncPrivKeyStr = "112t8roafGgHL1rhAP9632Yef3sx5k8xgp8cwK4MCJsCL1UWcxXvpzg97N4dwvcD735iKf31Q2ZgrAvKfVjeSUEvnzKJyyJD3GqqSZdxN4or" // shard 0
	// // tradingSuite.IncPaymentAddrStr = "12S5Lrs1XeQLbqN4ySyKtjAjd2d7sBP2tjFijzmp6avrrkQCNFMpkXm3FPzj2Wcu2ZNqJEmh9JriVuRErVwhuQnLmWSaggobEWsBEci"
	// tradingSuite.IncPaymentAddrStr = "12svfkP6w5UDJDSCwqH978PvqiqBxKmUnA9em9yAYWYJVRv7wuXY1qhhYpPAm4BDz2mLbFrRmdK3yRhnTqJCZXKHUmoi7NV83HCH2YFpctHNaDdkSiQshsjw2UFUuwdEvcidgaKmEvaNCaDU1Mr7"  // privacy v2
	// tradingSuite.IncPrivaKeyReceiverStr = "112t8roMtSrKYCL4eA4aXiQ8umGz78znHRTdMpzKAbSgL1Cj6JtbkS9i87jW1KFjbpN9fwM3PY7LNJq3QyawdHX61eTwN6beiiayMjN4yPwC" // shard 1
	// // tradingSuite.IncPaymentReceiverStr = "12S4oseu3scZJJuoLeGSEYZka1mmxHBNg7VbC1tQ67ZDjTUqzuRY4ABf4Bjop7uR22U1AxsLEheixfenpcc63tVG7E7QxF1zy5r1SXv"
	// tradingSuite.IncPaymentReceiverStr = "12suy7wB2qYzSdUYPrRu2Wys1ZccRDJVwoTY3TyqJjt5nNMUitutD73S5voK5dFmSRpQytiKHRiGs8CwJjx2ZZCjbSCkWSXDwMBpNpytGvKkE6Tg1MFFRNYqLkM5G1Q5a8BeAu9S8EuZQ3GLbQDx"  // privacy v2

	tradingSuite.BEP20PrivKeyStr = "d455f2de1aa18787ea5820afce2ae95b7405d11b9eb19d340f6f2d821047d437" //testnet
	tradingSuite.BEP20OwnerAddrStr = "Db418c263Dc4744079D7331Ddcf0c7C0488b25d1"                       //testnet

	tradingSuite.WETHAddressStr = "0xd0a1e359811322d97991e03f863a0c30c2cf029c" // testnet

	tradingSuite.IncBNBTokenIDStr = "e5032c083f0da67ca141331b6005e4a3740c50218f151a5e829e9d03227e33e2" //BNB
	tradingSuite.IncETHTokenIDStr = "a474ec7214b16ad6a6a355e732f2f511d8f2aa79cb4bd498ca46b05f3cfb0e53"
	tradingSuite.IncFAKETokenIDStr = "61e1efbf6be9decc46fdf8250cdae5be12bee501b65f774a58af4513b60000aa"


	tradingSuite.ETHAddressStr = "0xd66c6b4f0be8ce5b39d52e0fd1344c389929b378"
	tradingSuite.FAKEAddressStr = "0x3Ad292Fed6FbC5191C07DDfC739DB24F4b7d9a99"
	tradingSuite.BNBAddressStr = "0x0000000000000000000000000000000000000000"


	tradingSuite.BinanceHost = "https://data-seed-prebsc-2-s1.binance.org:8545/"

	tradingSuite.IncBridgeHost = "http://51.161.119.66:9334" //testnet 2
	tradingSuite.IncRPCHost = "http://51.161.119.66:9334"    //testnet 2


	tradingSuite.VaultAddr = common.HexToAddress("0x2f6F03F1b43Eab22f7952bd617A24AB46E970dF7")      // testnet 2

	// generate a new keys pair for SC
	tradingSuite.genKeysPairForSC()

	// connect to ethereum network
	tradingSuite.connectToETH()

	// tradingSuite.auth = bind.NewKeyedTransactor(tradingSuite.BEP20PrivKey)

	tradingSuite.DepositingBNB = float64(0.0015)
	tradingSuite.DepositETH = float64(0.0002)

	// tradingSuite.submitkeyPrivacyV2(tradingSuite.IncPrivKeyStr)
	// tradingSuite.createconvertcoinver1tover2transactionPrivacyV2(tradingSuite.IncPrivKeyStr)
	// tradingSuite.submitkeyPrivacyV2(tradingSuite.IncPrivaKeyReceiverStr)
}

func (tradingSuite *TnBSCTestSuite) TearDownSuite() {
	fmt.Println("Tearing down the suite...")
	tradingSuite.BEP20Client.Close()
}

func (tradingSuite *TnBSCTestSuite) SetupTest() {
	fmt.Println("Setting up the test...")
}

func (tradingSuite *TnBSCTestSuite) TearDownTest() {
	fmt.Println("Tearing down the test...")
}

func TestTnBSCTestSuite(t *testing.T) {
	fmt.Println("Starting entry point for test suite...")

	tradingSuite := new(TnBSCTestSuite)
	suite.Run(t, tradingSuite)

	fmt.Println("Finishing entry point for test suite...")
}

func (tradingSuite *TnBSCTestSuite) getBalanceOnBSC(
	tokenAddr common.Address,
	ownerAddr common.Address,
) *big.Int {
	if tokenAddr.Hex() == tradingSuite.BNBAddressStr {
		balance, err := tradingSuite.BEP20Client.BalanceAt(context.Background(), ownerAddr, nil)
		require.Equal(tradingSuite.T(), nil, err)
		return balance
	}
	// erc20 token
	instance, err := erc20.NewErc20(tokenAddr, tradingSuite.BEP20Client)
	require.Equal(tradingSuite.T(), nil, err)

	balance, err := instance.BalanceOf(&bind.CallOpts{}, ownerAddr)
	require.Equal(tradingSuite.T(), nil, err)
	return balance
}

func (tradingSuite *TnBSCTestSuite) connectToETH() {
	privKeyHex := tradingSuite.BEP20PrivKeyStr
	privKey, err := crypto.HexToECDSA(privKeyHex)
	require.Equal(tradingSuite.T(), nil, err)

	fmt.Printf("Sign Txs with address: %s\n", crypto.PubkeyToAddress(privKey.PublicKey).Hex())

	network := "BCS testnet"
	fmt.Printf("Connecting to network %s\n", network)
	client, err := ethclient.Dial(tradingSuite.BinanceHost)
	require.Equal(tradingSuite.T(), nil, err)

	tradingSuite.BEP20Client = client
	tradingSuite.BEP20PrivKey = privKey
}

func (tradingSuite *TnBSCTestSuite) depositBNB(
	amt float64,
	incPaymentAddrStr string,
) common.Hash {
	c, err := vault.NewVault(tradingSuite.VaultAddr, tradingSuite.BEP20Client)
	require.Equal(tradingSuite.T(), nil, err)

	auth := bind.NewKeyedTransactor(tradingSuite.BEP20PrivKey)
	// auth.GasPrice = big.NewInt(GasPriceTn)
	// auth.Nonce = big.NewInt(0)
	auth.Value = big.NewInt(int64(amt * params.Ether))
	tx, err := c.Deposit(auth, incPaymentAddrStr)
	require.Equal(tradingSuite.T(), nil, err)
	txHash := tx.Hash()

	if err := wait(tradingSuite.BEP20Client, txHash); err != nil {
		require.Equal(tradingSuite.T(), nil, err)
	}
	fmt.Printf("Deposited to proof, txHash : %x\n", txHash[:])
	require.Equal(tradingSuite.T(), tradingSuite.getStatusTxhash(txHash), uint64(1), "tx on BCS network failed")
	return txHash

}

func (tradingSuite *TnBSCTestSuite) depositERC20ToBridge(
	amt *big.Int,
	tokenAddr common.Address,
	incPaymentAddrStr string,
) common.Hash {
	auth := bind.NewKeyedTransactor(tradingSuite.BEP20PrivKey)
	c, err := vault.NewVault(tradingSuite.VaultAddr, tradingSuite.BEP20Client)
	require.Equal(tradingSuite.T(), nil, err)

	erc20Token, _ := erc20.NewErc20(tokenAddr, tradingSuite.BEP20Client)
	tx2, apprErr := erc20Token.Approve(auth, tradingSuite.VaultAddr, amt)
	tx2Hash := tx2.Hash()
	fmt.Printf("Approve tx, txHash: %x\n", tx2Hash[:])
	require.Equal(tradingSuite.T(), nil, apprErr)
	time.Sleep(15 * time.Second)
	// auth.GasPrice = big.NewInt(GasPriceTn)
	// auth.GasLimit = GasLimitTn
	fmt.Println("Starting deposit BEP20 to vault contract")
	tx, err := c.DepositERC20(auth, tokenAddr, amt, incPaymentAddrStr)
	require.Equal(tradingSuite.T(), nil, err)
	fmt.Println("Finished deposit BEP20 to vault contract")
	txHash := tx.Hash()

	if err := wait(tradingSuite.BEP20Client, txHash); err != nil {
		require.Equal(tradingSuite.T(), nil, err)
	}
	fmt.Printf("deposited BEP20 token to bridge, txHash: %x\n", txHash[:])
	require.Equal(tradingSuite.T(), tradingSuite.getStatusTxhash(txHash), uint64(1), "tx on BCS network failed")
	return txHash
}

func (tradingSuite *TnBSCTestSuite) callIssuingBSCReq(
	incTokenIDStr string,
	ethDepositProof []string,
	ethBlockHash string,
	ethTxIdx uint,
) (string, error) {
	rpcClient := rpccaller.NewRPCClient()
	meta := map[string]interface{}{
		"IncTokenID": incTokenIDStr,
		"BlockHash":  ethBlockHash,
		"ProofStrs":  ethDepositProof,
		"TxIndex":    ethTxIdx,
	}
	params := []interface{}{
		tradingSuite.IncPrivKeyStr,
		nil,
		5,
		-1,
		meta,
	}
	var res TnIssuingBSCRes
	err := rpcClient.RPCCall(
		"",
		tradingSuite.IncRPCHost,
		"",
		"createandsendtxwithissuingbscreq",
		params,
		&res,
	)
	if err != nil {
		return "error", err
	}

	response, _ := json.Marshal(res)
	fmt.Println("get response", string(response))

	if res.RPCError != nil {
		return "error", errors.New(res.RPCError.StackTrace)
	}
	return res.Result.(map[string]interface{})["TxID"].(string), nil
}

func (tradingSuite *TnBSCTestSuite) callBurningPToken(
	incTokenIDStr string,
	amount *big.Int,
	remoteAddrStr string,
	burningMethod string,
	IncPrivKeyStr string,
) (map[string]interface{}, error) {
	rpcClient := rpccaller.NewRPCClient()
	meta := map[string]interface{}{
		"TokenID":     incTokenIDStr,
		"TokenTxType": 1,
		"TokenName":   "",
		"TokenSymbol": "",
		"TokenAmount": amount.String(),
		"TokenReceivers": map[string]string{
			tradingSuite.IncBurningAddrStr: amount.String(),
			// tradingSuite.IncPaymentAddrStr: "5",
		},
		"RemoteAddress": remoteAddrStr,
		"Privacy":       true,
		"TokenFee":      "0",
	}
	params := []interface{}{
		IncPrivKeyStr,
		nil,
		5,
		-1,
		meta,
		"",
		0,
	}
	var res TnBurningForDepositToSCRes
	err := rpcClient.RPCCall(
		"",
		tradingSuite.IncRPCHost,
		"",
		burningMethod,
		params,
		&res,
	)
	if err != nil {
		fmt.Println("calling burning ptokens err : ", err)
		return nil, err
	}
	bb, _ := json.Marshal(res)
	fmt.Println("calling burning ptokens res : ", string(bb))
	if res.RPCError != nil {
		return nil, errors.New(res.RPCError.Message)
	}
	return res.Result.(map[string]interface{}), nil
}

func (tradingSuite *TnBSCTestSuite) sendPRV(
	IncPrivKeyStr string,
	amount *big.Int,
	IncPaymentAddr string,
) (map[string]interface{}, error) {
	rpcClient := rpccaller.NewRPCClient()
	meta := map[string]interface{}{
		IncPaymentAddr: amount.Uint64(),
	}
	params := []interface{}{
		IncPrivKeyStr,
		meta,
		1,
		0,
	}
	var res IncTransaction
	err := rpcClient.RPCCall(
		"",
		tradingSuite.IncRPCHost,
		"",
		"createandsendtransaction",
		params,
		&res,
	)
	if err != nil {
		fmt.Println("send PRV err: ", err)
		return nil, err
	}
	bb, _ := json.Marshal(res)
	fmt.Println("tranfer PRV res: ", string(bb))
	if res.RPCError != nil {
		return nil, errors.New(res.RPCError.Message)
	}
	return res.Result.(map[string]interface{}), nil
}


func (tradingSuite *TnBSCTestSuite) submitBurnProofForWithdrawal(
	burningTxIDStr string,
) common.Hash {
	proof, err := getAndDecodeBurnProofV2(tradingSuite.IncBridgeHost, burningTxIDStr, "getbscburnproof")
	require.Equal(tradingSuite.T(), nil, err)

	// Get contract instance
	c, err := vault.NewVault(tradingSuite.VaultAddr, tradingSuite.BEP20Client)
	require.Equal(tradingSuite.T(), nil, err)

	// Burn
	auth := bind.NewKeyedTransactor(tradingSuite.BEP20PrivKey)
	// auth.GasLimit = GasLimitTn
	// auth.GasPrice = big.NewInt(GasPriceTn)
	// auth.Nonce = big.NewInt(13)
	tx, err := Withdraw(c, auth, proof)
	require.Equal(tradingSuite.T(), nil, err)

	txHash := tx.Hash()
	if err := wait(tradingSuite.BEP20Client, txHash); err != nil {
		require.Equal(tradingSuite.T(), nil, err)
	}
	fmt.Printf("burned, txHash: %x\n", txHash[:])
	require.Equal(tradingSuite.T(), tradingSuite.getStatusTxhash(txHash), uint64(1), "tx on BSC network failed")
	return txHash
}

func (tradingSuite *TnBSCTestSuite) genKeysPairForSC() {
	incPriKeyBytes, _, err := base58.Base58Check{}.Decode(tradingSuite.IncPrivKeyStr)
	require.Equal(tradingSuite.T(), nil, err)

	tradingSuite.GeneratedPrivKeyForSC, tradingSuite.GeneratedPubKeyForSC = bridgesig.KeyGen(incPriKeyBytes)
}

func (tradingSuite *TnBSCTestSuite) getDepositedBalance(
	ethTokenAddrStr string,
	ownerAddrStr string,
) *big.Int {
	c, err := vault.NewVault(tradingSuite.VaultAddr, tradingSuite.BEP20Client)
	require.Equal(tradingSuite.T(), nil, err)
	token := common.HexToAddress(ethTokenAddrStr)
	owner := common.HexToAddress(ownerAddrStr)
	bal, err := c.GetDepositedBalance(nil, token, owner)
	require.Equal(tradingSuite.T(), nil, err)
	//fmt.Printf("deposited balance on SC: %d\n", bal)
	return bal
}

func (tradingSuite *TnBSCTestSuite) requestWithdraw(
	withdrawalETHTokenIDStr string,
	amount *big.Int,
) common.Hash {
	c, err := vault.NewVault(tradingSuite.VaultAddr, tradingSuite.BEP20Client)
	require.Equal(tradingSuite.T(), nil, err)
	auth := bind.NewKeyedTransactor(tradingSuite.BEP20PrivKey)

	token := common.HexToAddress(withdrawalETHTokenIDStr)
	// amount := big.NewInt(0.1 * params.Ether)
	timestamp := []byte(randomizeTimestamp())
	vaultAbi, _ := abi.JSON(strings.NewReader(vault.VaultHelperABI))
	psData := vault.VaultHelperPreSignData{
		Prefix:    REQ_WITHDRAW_PREFIX,
		Token:     token,
		Timestamp: timestamp,
		Amount:    amount,
	}
	tempData, _ := vaultAbi.Pack("_buildSignRequestWithdraw", psData, tradingSuite.IncPaymentAddrStr)
	data := rawsha3(tempData[4:])
	signBytes, _ := crypto.Sign(data, &tradingSuite.GeneratedPrivKeyForSC)
	// auth.GasPrice = big.NewInt(GasPriceTn)
	// auth.GasLimit = GasLimitTn
	tx, err := c.RequestWithdraw(auth, tradingSuite.IncPaymentAddrStr, token, amount, signBytes, timestamp)
	require.Equal(tradingSuite.T(), nil, err)

	txHash := tx.Hash()
	if err := wait(tradingSuite.BEP20Client, txHash); err != nil {
		require.Equal(tradingSuite.T(), nil, err)
	}
	fmt.Printf("request withdrawal, txHash: %x\n", txHash[:])
	return txHash
}

func (tradingSuite *TnBSCTestSuite) getBalanceTokenIncAccount(
	IncPrivKeyStr string,
	ethTokenAddrStr string,
) (uint64, error) {
	rpcClient := rpccaller.NewRPCClient()
	params := []interface{}{
		IncPrivKeyStr,
		ethTokenAddrStr,
	}
	var res TnBalanceIncAccount
	err := rpcClient.RPCCall(
		"",
		tradingSuite.IncRPCHost,
		"",
		"getbalanceprivacycustomtoken",
		params,
		&res,
	)
	if err != nil {
		return 0, err
	}
	//fmt.Println(res.Result)
	return uint64(res.Result.(float64)), nil
}

func (tradingSuite *TnBSCTestSuite) getBalancePrvIncAccount(
	IncPrivKeyStr string,
) (uint64, error) {
	rpcClient := rpccaller.NewRPCClient()
	params := []interface{}{
		IncPrivKeyStr,
	}
	var res TnBalanceIncAccount
	err := rpcClient.RPCCall(
		"",
		tradingSuite.IncRPCHost,
		"",
		"getbalancebyprivatekey",
		params,
		&res,
	)
	if err != nil {
		return 0, err
	}
	//fmt.Println(res.Result)
	return uint64(res.Result.(float64)), nil
}

func (tradingSuite *TnBSCTestSuite) submitkeyPrivacyV2(
	IncPrivKeyStr string,
) (map[string]interface{}, error) {
	rpcClient := rpccaller.NewRPCClient()
	params := []interface{}{
		IncPrivKeyStr,
	}
	var res TnSubmitkey
	err := rpcClient.RPCCall(
		"",
		tradingSuite.IncRPCHost,
		"",
		"submitkey",
		params,
		&res,
	)
	if err != nil {
		return nil, errors.New(res.RPCError.Message)
	}
	//fmt.Println(res.Result)
	return res.Result.(map[string]interface{}), nil
}

func (tradingSuite *TnBSCTestSuite) createconvertcoinver1tover2transactionPrivacyV2(
	IncPrivKeyStr string,
) (map[string]interface{}, error) {
	rpcClient := rpccaller.NewRPCClient()
	params := []interface{}{
		IncPrivKeyStr,
		-1,
	}
	var res Tnconvertcoinver1tover2
	err := rpcClient.RPCCall(
		"",
		tradingSuite.IncRPCHost,
		"",
		"createconvertcoinver1tover2transaction",
		params,
		&res,
	)
	if err != nil {
		return nil, errors.New(res.RPCError.Message)
	}
	//fmt.Println(res.Result)
	return res.Result.(map[string]interface{}), nil
}


func (tradingSuite *TnBSCTestSuite) getFeePRVbyTxhashInC(
	txhash string,
) uint64 {
	rpcClient := rpccaller.NewRPCClient()
	params := []interface{}{
		txhash,
	}
	var res TnTxhashInC
	err := rpcClient.RPCCall(
		"",
		tradingSuite.IncRPCHost,
		"",
		"gettransactionbyhash",
		params,
		&res,
	)
	if err != nil {
		return 0
	}
	return uint64(res.Result.(map[string]interface{})["Fee"].(float64))
}

func (tradingSuite *TnBSCTestSuite) getGasFeeETHbyTxhash(txHash common.Hash) *big.Int {
	reciept, _ := getETHTransactionReceipt(tradingSuite.BinanceHost, txHash)
	//fmt.Println("reciept gas fee : ", reciept.GasUsed)
	gasPrice := big.NewInt(50000000000)
	gasFee := big.NewInt(0).Div(big.NewInt(0).Mul(big.NewInt(int64(reciept.GasUsed)), gasPrice), big.NewInt(int64(1)))
	return gasFee
}

func (tradingSuite *TnBSCTestSuite) getStatusTxhash(txHash common.Hash) uint64 {
	tx, err := getETHTransactionReceipt(tradingSuite.BinanceHost, txHash)
	require.Equal(tradingSuite.T(), nil, err)
	// fmt.Println(tx.Status) // 1 succcess 0 failed
	return tx.Status
}


func (tradingSuite *TnBSCTestSuite) getStatusBridgeRq(txhash string) int {
	rpcClient := rpccaller.NewRPCClient()
	meta := map[string]interface{}{
		"TxReqID": txhash,
	}
	params := []interface{}{
		meta,
	}
	var res StatusBridgeRq
	err := rpcClient.RPCCall(
		"",
		tradingSuite.IncRPCHost,
		"",
		"getbridgereqwithstatus",
		params,
		&res,
	)
	if err != nil {
		return 0
	}
	return int(res.Result.(float64))
}

func (tradingSuite *TnBSCTestSuite) Test1DepositAndWithdrwaBNB() {
	// return
	fmt.Println("============ TEST 1 DEPOSIT AND WITHDRAW BNB ===========")
	fmt.Println("------------ STEP 0: declaration & initialization --------------")

	pubKeyToAddrStr := crypto.PubkeyToAddress(tradingSuite.GeneratedPubKeyForSC).Hex()
	fmt.Println("GeneratedPubKeyForSC", pubKeyToAddrStr)

	// get info balance initialization
	balPrvInit, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance initialization : ", balPrvInit)

	balpBNBInit, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncBNBTokenIDStr)
	fmt.Println("[INFO] pBNB balance initialization : ", balpBNBInit)

	balBNBInit := tradingSuite.getBalanceOnBSC(
		common.HexToAddress(tradingSuite.BNBAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.BEP20OwnerAddrStr)),
	)
	fmt.Println("[INFO] BNB balance initialization : ", balBNBInit)

	fmt.Println("------------ STEP 1: porting BNB to pBNB --------------")

	fmt.Println("amount BNB deposit : ", (big.NewInt(int64(tradingSuite.DepositingBNB * params.Ether))))

	// Deposit to proof
	txHash := tradingSuite.depositBNB(
		tradingSuite.DepositingBNB,
		tradingSuite.IncPaymentAddrStr,
	)

	fmt.Println("gas Fee transaction :", tradingSuite.getGasFeeETHbyTxhash(txHash))
	// get ETH remain after depsit
	balBNBAfDep := tradingSuite.getBalanceOnBSC(
		common.HexToAddress(tradingSuite.BNBAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.BEP20OwnerAddrStr)),
	)
	fmt.Println("[INFO] BNB balance remain after deposit : ", balBNBAfDep)

	//	require.Equal(tradingSuite.T(), balBNBAfDep, big.NewInt(0).Sub(big.NewInt(0).Sub(balBNBInit, big.NewInt(int64(tradingSuite.DepositingBNB*params.Ether))), tradingSuite.getGasFeeETHbyTxhash(txHash)), "balance ETH incorrect")

	// Proof
	_, ethBlockHash, ethTxIdx, ethDepositProof, err := getETHDepositProof(tradingSuite.BinanceHost, txHash)
	require.Equal(tradingSuite.T(), nil, err)
	fmt.Println("depositProof ---- : ", ethBlockHash, ethTxIdx, ethDepositProof)

	fmt.Println("Waiting 90s for 15 blocks confirmation")
	time.Sleep(BSCWaiting * time.Second)
	txhashInC, err := tradingSuite.callIssuingBSCReq(
		tradingSuite.IncBNBTokenIDStr,
		ethDepositProof,
		ethBlockHash,
		ethTxIdx,
	)
	require.Equal(tradingSuite.T(), nil, err)

	time.Sleep(INCWating * time.Second)
	require.Equal(tradingSuite.T(), 2, tradingSuite.getStatusBridgeRq(txhashInC), "Mint transaction rejected")
	// // check PRV and token balance after issuing
	balPrvAfIssS1, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance after issuing step 1: ", balPrvAfIssS1)
	//require.NotEqual(tradingSuite.T(), balPrvAfIssS1, (balPrvInit - tradingSuite.getFeePRVbyTxhashInC(issuuRes["TxID"].(string))), "Balance PRV remain incorrect after issuu step 1")

	balpBNBS1, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncBNBTokenIDStr)
	fmt.Println("[INFO] pBNB balance after issuing step 1 : ", balpBNBS1)
	require.Equal(tradingSuite.T(), big.NewInt(0).Div(big.NewInt(int64(tradingSuite.DepositingBNB*params.Ether)), big.NewInt(1000000000)).Cmp(big.NewInt(int64(balpBNBS1-balpBNBInit))) ==0 , true, " balance pToken minted incorrect")

	
	fmt.Println("------------ STEP 2: withdraw pBNB to deposit BNB   --------------")

	withdrawingpBNB := big.NewInt(int64(balpBNBS1))
	burningRes, err := tradingSuite.callBurningPToken(
		tradingSuite.IncBNBTokenIDStr,
		withdrawingpBNB,
		tradingSuite.BEP20OwnerAddrStr,
		"createandsendburningbscrequest",
		tradingSuite.IncPrivKeyStr,
	)
	require.Equal(tradingSuite.T(), nil, err)
	burningTxID, found := burningRes["TxID"]
	require.Equal(tradingSuite.T(), true, found)
	time.Sleep(INCWating * time.Second)

	balpBNBAfBurnS2, _ := tradingSuite.getBalanceTokenIncAccount(
		tradingSuite.IncPrivKeyStr,
		tradingSuite.IncBNBTokenIDStr,
	)
	fmt.Println("[INFO] pBNB balance after burning step 2 : ", balpBNBAfBurnS2)

	require.Equal(tradingSuite.T(), big.NewInt(0).Sub(big.NewInt(int64(balpBNBS1)), withdrawingpBNB).Cmp(big.NewInt(int64(balpBNBAfBurnS2))) == 0, true, "balance pToken burn incorrect" )

	tradingSuite.submitBurnProofForWithdrawal(burningTxID.(string))

	time.Sleep(BEP20WaitTn * time.Second)
	balBNBAfDep2 := tradingSuite.getBalanceOnBSC(
		common.HexToAddress(tradingSuite.BNBAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.BEP20OwnerAddrStr)),
	)
	fmt.Println("[INFO] BNB balance after withdraw  : ", balBNBAfDep2)
}

func (tradingSuite *TnBSCTestSuite) Test2DepositAndWithdrwaBNBCrossShard() {
	// return
	fmt.Println("============ TEST 2 DEPOSIT AND WITHDRAW BNB Cross Shard ===========")
	fmt.Println("------------ STEP 0: declaration & initialization --------------")

	tradingSuite.sendPRV(tradingSuite.IncPrivKeyStr, big.NewInt(10000), tradingSuite.IncPaymentReceiverStr)

	pubKeyToAddrStr := crypto.PubkeyToAddress(tradingSuite.GeneratedPubKeyForSC).Hex()
	fmt.Println("GeneratedPubKeyForSC", pubKeyToAddrStr)

	// get info balance initialization
	balPrvInit, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance submiter initialization : ", balPrvInit)

	balpBNBInit, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncBNBTokenIDStr)
	fmt.Println("[INFO] pBNB balance submiter initialization : ", balpBNBInit)

	balPrvInitX, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivaKeyReceiverStr)
	fmt.Println("[INFO] PRV balance Xshard initialization : ", balPrvInitX)

	balpBNBInitX, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivaKeyReceiverStr, tradingSuite.IncBNBTokenIDStr)
	fmt.Println("[INFO] pBNB balance Xshard initialization : ", balpBNBInitX)

	balBNBInit := tradingSuite.getBalanceOnBSC(
		common.HexToAddress(tradingSuite.BNBAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.BEP20OwnerAddrStr)),
	)
	fmt.Println("[INFO] BNB balance initialization : ", balBNBInit)

	fmt.Println("------------ STEP 1: porting BNB to pBNB --------------")

	fmt.Println("amount BNB deposit : ", (big.NewInt(int64(tradingSuite.DepositingBNB * params.Ether))))

	// Deposit to proof
	txHash := tradingSuite.depositBNB(
		tradingSuite.DepositingBNB,
		tradingSuite.IncPaymentReceiverStr,
	)

	fmt.Println("gas Fee transaction :", tradingSuite.getGasFeeETHbyTxhash(txHash))
	// get ETH remain after depsit
	balBNBAfDep := tradingSuite.getBalanceOnBSC(
		common.HexToAddress(tradingSuite.BNBAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.BEP20OwnerAddrStr)),
	)

	fmt.Println("[INFO] BNB balance remain after deposit : ", balBNBAfDep)

	// Proof
	_, ethBlockHash, ethTxIdx, ethDepositProof, err := getETHDepositProof(tradingSuite.BinanceHost, txHash)
	require.Equal(tradingSuite.T(), nil, err)
	fmt.Println("depositProof ---- : ", ethBlockHash, ethTxIdx, ethDepositProof)

	fmt.Println("Waiting 90s for 15 blocks confirmation")
	time.Sleep(BSCWaiting * time.Second)
	txhashInC, err := tradingSuite.callIssuingBSCReq(
		tradingSuite.IncBNBTokenIDStr,
		ethDepositProof,
		ethBlockHash,
		ethTxIdx,
	)
	require.Equal(tradingSuite.T(), nil, err)

	time.Sleep(INCWating * time.Second)
	require.Equal(tradingSuite.T(), 2, tradingSuite.getStatusBridgeRq(txhashInC), "Mint transaction rejected")

	// check PRV and token balance after issuing
	balPrvAfIssS1, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivaKeyReceiverStr)
	fmt.Println("[INFO] PRV balance Xshard after issuing step 1: ", balPrvAfIssS1)
	//require.NotEqual(tradingSuite.T(), balPrvAfIssS1, (balPrvInit - tradingSuite.getFeePRVbyTxhashInC(issuuRes["TxID"].(string))), "Balance PRV remain incorrect after minted step 1")

	balpBNBS1, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivaKeyReceiverStr, tradingSuite.IncBNBTokenIDStr)
	fmt.Println("[INFO] pBNB balance Xshard after issuing step 1 : ", balpBNBS1)

	balPrvAfIssS1S, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance submiter after issuing step 1: ", balPrvAfIssS1S)
	balpBNBAfS1, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncBNBTokenIDStr)
	fmt.Println("[INFO] pBNB balance submiter after issuing step 1 : ", balpBNBAfS1)

	require.Equal(tradingSuite.T(),true, big.NewInt(0).Div(big.NewInt(int64(tradingSuite.DepositingBNB*params.Ether)), big.NewInt(1000000000)).Cmp(big.NewInt(int64(balpBNBS1-balpBNBInitX))) == 0, " balance pToken minted incorrect")

	fmt.Println("------------ STEP 2: burning pBNB to deposit BNB  --------------")
	// make a burn tx to incognito chain as a result of deposit
	withdrawingpBNB := big.NewInt(int64(balpBNBS1))
	burningRes, err := tradingSuite.callBurningPToken(
		tradingSuite.IncBNBTokenIDStr,
		withdrawingpBNB,
		pubKeyToAddrStr[2:],
		"createandsendburningbscrequest",
		tradingSuite.IncPrivaKeyReceiverStr,
	)
	require.Equal(tradingSuite.T(), nil, err)
	burningTxID, found := burningRes["TxID"]
	require.Equal(tradingSuite.T(), true, found)
	time.Sleep(INCWating * time.Second)

	// check PRV and token balance after burning
	balPrvAfBurnS2a, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivaKeyReceiverStr)
	fmt.Println("[INFO] PRV balance Xshard after burning step 2: ", balPrvAfBurnS2a)

	balpBNBAfBurnS2a, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivaKeyReceiverStr, tradingSuite.IncBNBTokenIDStr)
	fmt.Println("[INFO] pBNB balance Xshard after burning step 2 : ", balpBNBAfBurnS2a)
	
		// assert pBNB balance burning
	require.Equal(tradingSuite.T(), big.NewInt(0).Sub(big.NewInt(int64(balpBNBS1)), withdrawingpBNB).Cmp(big.NewInt(int64(balpBNBAfBurnS2a))) == 0, true, "balance pToken burn incorrect" )

	balPrvAfBurnS2, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance submiter after burning step 2: ", balPrvAfBurnS2)
	//require.NotEqual(tradingSuite.T(), balPrvAfBurnS2, (balPrvAfIssS1 - tradingSuite.getFeePRVbyTxhashInC(burningRes["TxID"].(string))), "Balance PRV remain incorrect after burn step 2")

	balpBNBAfBurnS2, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncBNBTokenIDStr)
	fmt.Println("[INFO] pBNB balance submiter after burning step 2 : ", balpBNBAfBurnS2)
	require.Equal(tradingSuite.T(), balpBNBAfBurnS2, balpBNBInit)

	txHash2 := tradingSuite.submitBurnProofForWithdrawal(burningTxID.(string))
	// txHash2 := tradingSuite.submitBurnProofForDepositToSC("173279b5d9645a833bac9c55bc9199f2ab144a5a4f49673b2c1075402fb52e0c")
	time.Sleep(BEP20WaitTn * time.Second)

	fmt.Println("gas Fee transaction :", tradingSuite.getGasFeeETHbyTxhash(txHash2))
	// get BNB remain
	balBNBAfDep2 := tradingSuite.getBalanceOnBSC(
		common.HexToAddress(tradingSuite.BNBAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.BEP20OwnerAddrStr)),
	)
	fmt.Println("[INFO] BNB balance remain  : ", balBNBAfDep2)

}

func (tradingSuite *TnBSCTestSuite) Test3DepositAndWithdrwatokenETH() {
		// return
		fmt.Println("============ TEST 3 DEPOSIT AND WITHDRAW BEP20 TOKEN (Binance ETH) ===========")
		fmt.Println("------------ STEP 0: declaration & initialization --------------")
		// pubKeyToAddrStr := crypto.PubkeyToAddress(tradingSuite.GeneratedPubKeyForSC).Hex()
	
		// get info balance initialization
		balPrvInit, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
		fmt.Println("[INFO] PRV balance initialization : ", balPrvInit)
	
		balBNBInit := tradingSuite.getBalanceOnBSC(
			common.HexToAddress(tradingSuite.BNBAddressStr),
			common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.BEP20OwnerAddrStr)),
		)
		fmt.Println("[INFO] BNB balance initialization : ", balBNBInit)
	
		balpETHInit, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncETHTokenIDStr)
		fmt.Println("[INFO] pETH balance initialization : ", balpETHInit)
	
		balETHInit := tradingSuite.getBalanceOnBSC(
			common.HexToAddress(tradingSuite.ETHAddressStr),
			common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.BEP20OwnerAddrStr)),
		)
		fmt.Println("[INFO] ETH balance initialization : ", balETHInit)
	
		fmt.Println("------------ STEP 1: porting ETH to pETH --------------")
		depositAmt := big.NewInt(int64(tradingSuite.DepositETH * params.Ether))
		fmt.Println("amount ETH deposit input : ", depositAmt)
	
		// Deposit to proof
		txHash := tradingSuite.depositERC20ToBridge(
			depositAmt,
			common.HexToAddress(tradingSuite.ETHAddressStr),
			tradingSuite.IncPaymentAddrStr,
		)
		
		balETHAfDep := tradingSuite.getBalanceOnBSC(
			common.HexToAddress(tradingSuite.ETHAddressStr),
			common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.BEP20OwnerAddrStr)),
		)
		fmt.Println("[INFO] ETH balance remain after deposit : ", balETHAfDep)
	
		_, ethBlockHash, ethTxIdx, ethDepositProof, err := getETHDepositProof(tradingSuite.BinanceHost, txHash)
		require.Equal(tradingSuite.T(), nil, err)
		fmt.Println("depositProof ---- : ", ethBlockHash, ethTxIdx, ethDepositProof)
	
		fmt.Println("Waiting 90s for 15 blocks confirmation")
		time.Sleep(BSCWaiting * time.Second)
	
		txhashInC, err := tradingSuite.callIssuingBSCReq(
			tradingSuite.IncETHTokenIDStr,
			ethDepositProof,
			ethBlockHash,
			ethTxIdx,
		)
		require.Equal(tradingSuite.T(), nil, err)
	
		time.Sleep(INCWating * time.Second)
		require.Equal(tradingSuite.T(), 2, tradingSuite.getStatusBridgeRq(txhashInC), "Mint transaction rejected")
	
		// check PRV and token balance after issuing
		balpETHAfIssS1, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncETHTokenIDStr)
		fmt.Println("[INFO] pETH balance after issuing step 1 : ", balpETHAfIssS1)
	
		require.Equal(tradingSuite.T(), big.NewInt(int64(balpETHAfIssS1-balpETHInit)).Cmp(big.NewInt(0).Div(depositAmt,big.NewInt(int64(1000000000)))) == 0,true, " balance pToken minted incorrect")
	
		balPrvAfIssS1, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
		fmt.Println("[INFO] PRV balance after issuing step 1: ", balPrvAfIssS1)
	
		
		fmt.Println("------------ STEP 2: withdraw pETH to deposit ETH   --------------")
		amountWithdraw := big.NewInt(int64(balpETHAfIssS1))

		burningRes, err := tradingSuite.callBurningPToken(
			tradingSuite.IncETHTokenIDStr,
			amountWithdraw,
			tradingSuite.BEP20OwnerAddrStr,
			"createandsendburningbscrequest",
			tradingSuite.IncPrivKeyStr,
		)
		require.Equal(tradingSuite.T(), nil, err)
		burningTxID, found := burningRes["TxID"]
		require.Equal(tradingSuite.T(), true, found)
		time.Sleep(INCWating * time.Second)
	
		balpETHAfBurnS2, _ := tradingSuite.getBalanceTokenIncAccount(
			tradingSuite.IncPrivKeyStr,
			tradingSuite.IncETHTokenIDStr,
		)
		fmt.Println("[INFO] pETH balance after burning step 4 : ", balpETHAfBurnS2)
		require.Equal(tradingSuite.T(), true ,big.NewInt(int64(balpETHAfBurnS2)).Cmp(big.NewInt(0).Sub(big.NewInt(int64(balpETHAfIssS1)), amountWithdraw)) == 0, " balance pToken burning incorrect")
	
		tradingSuite.submitBurnProofForWithdrawal(burningTxID.(string))
		time.Sleep(BEP20WaitTn * time.Second)
		balETHAfWrS2 := tradingSuite.getBalanceOnBSC(
			common.HexToAddress(tradingSuite.ETHAddressStr),
			common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.BEP20OwnerAddrStr)),
		)
		fmt.Println("[INFO] ETH balance after withdraw  : ", balETHAfWrS2)
		require.Equal(tradingSuite.T(),true ,big.NewInt(0).Sub(balETHAfWrS2,balETHAfDep).Cmp(big.NewInt(0).Mul(amountWithdraw,big.NewInt(int64(1000000000)))) == 0, "Token withdraw incorrect" )		
}

func (tradingSuite *TnBSCTestSuite) Test4DepositAndWithdrwatokenFAKE() {
	// return
	fmt.Println("============ TEST 4 DEPOSIT AND WITHDRAW BEP20 TOKEN (PRV FAKE) ===========")
	fmt.Println("------------ STEP 0: declaration & initialization --------------")
	// pubKeyToAddrStr := crypto.PubkeyToAddress(tradingSuite.GeneratedPubKeyForSC).Hex()

	// get info balance initialization
	balPrvInit, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance initialization : ", balPrvInit)

	balBNBInit := tradingSuite.getBalanceOnBSC(
		common.HexToAddress(tradingSuite.BNBAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.BEP20OwnerAddrStr)),
	)
	fmt.Println("[INFO] ETH balance initialization : ", balBNBInit)

	balpFAKEInit, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncFAKETokenIDStr)
	fmt.Println("[INFO] pFAKE balance initialization : ", balpFAKEInit)

	balFAKEInit := tradingSuite.getBalanceOnBSC(
		common.HexToAddress(tradingSuite.FAKEAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.BEP20OwnerAddrStr)),
	)
	fmt.Println("[INFO] FAKE balance initialization : ", balFAKEInit)

	fmt.Println("------------ STEP 1: porting FakePRV to ptoken --------------")
	depositAmt := big.NewInt(int64(tradingSuite.DepositETH * 1000000000))
	fmt.Println("amount FakePRV deposit input : ", depositAmt)

	// Deposit to proof
	txHash := tradingSuite.depositERC20ToBridge(
		depositAmt,
		common.HexToAddress(tradingSuite.FAKEAddressStr),
		tradingSuite.IncPaymentAddrStr,
	)

	balFAKEAfDep := tradingSuite.getBalanceOnBSC(
		common.HexToAddress(tradingSuite.FAKEAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.BEP20OwnerAddrStr)),
	)
	fmt.Println("[INFO] FakePRV balance remain after deposit : ", balFAKEAfDep)

	_, ethBlockHash, ethTxIdx, ethDepositProof, err := getETHDepositProof(tradingSuite.BinanceHost, txHash)
	require.Equal(tradingSuite.T(), nil, err)
	fmt.Println("depositProof ---- : ", ethBlockHash, ethTxIdx, ethDepositProof)

	fmt.Println("Waiting 90s for 15 blocks confirmation")
	time.Sleep(BSCWaiting * time.Second)

	txhashInC, err := tradingSuite.callIssuingBSCReq(
		tradingSuite.IncFAKETokenIDStr,
		ethDepositProof,
		ethBlockHash,
		ethTxIdx,
	)
	require.Equal(tradingSuite.T(), nil, err)

	time.Sleep(INCWating * time.Second)
	require.Equal(tradingSuite.T(), 2, tradingSuite.getStatusBridgeRq(txhashInC), "Mint transaction rejected")

	balpFAKEAfIssS1, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncFAKETokenIDStr)
	fmt.Println("[INFO] pFakePRV balance after issuing step 1 : ", balpFAKEAfIssS1)

	require.Equal(tradingSuite.T(), big.NewInt(int64(balpFAKEAfIssS1-balpFAKEInit)).Cmp(depositAmt) == 0,true, " balance pToken minted incorrect")

	// check PRV and token balance after issuing
	balPrvAfIssS1, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance after issuing step 1: ", balPrvAfIssS1)

	
	fmt.Println("------------ STEP 2: withdraw pFakePRV to deposit FakePRV   --------------")
	amountWithdraw := big.NewInt(int64(balpFAKEAfIssS1))

	burningRes, err := tradingSuite.callBurningPToken(
		tradingSuite.IncFAKETokenIDStr,
		amountWithdraw,
		tradingSuite.BEP20OwnerAddrStr,
		"createandsendburningbscrequest",
		tradingSuite.IncPrivKeyStr,
	)
	require.Equal(tradingSuite.T(), nil, err)
	burningTxID, found := burningRes["TxID"]
	require.Equal(tradingSuite.T(), true, found)
	time.Sleep(INCWating * time.Second)

	balpFAKEAfBurnS51, _ := tradingSuite.getBalanceTokenIncAccount(
		tradingSuite.IncPrivKeyStr,
		tradingSuite.IncFAKETokenIDStr,
	)
	fmt.Println("[INFO] pFakePRV balance after burning step 4 : ", balpFAKEAfBurnS51)
	require.Equal(tradingSuite.T(), big.NewInt(int64(balpFAKEAfBurnS51)).Cmp(big.NewInt(0).Sub(big.NewInt(int64(balpFAKEAfIssS1)), amountWithdraw)) == 0, true, " balance pToken burning incorrect")

	tradingSuite.submitBurnProofForWithdrawal(burningTxID.(string))
	time.Sleep(BEP20WaitTn * time.Second)
	balFAKEAfWrS2 := tradingSuite.getBalanceOnBSC(
		common.HexToAddress(tradingSuite.FAKEAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.BEP20OwnerAddrStr)),
	)
	fmt.Println("[INFO] FakePRV balance after withdraw  : ", balFAKEAfWrS2)
	require.Equal(tradingSuite.T(),true ,big.NewInt(0).Sub(balFAKEAfWrS2,balFAKEAfDep).Cmp(amountWithdraw) == 0, "Token withdraw incorrect" )
}


