package main

import (
	"bytes"
	"context"
	"crypto/ecdsa"
	"encoding/base64"
	// "encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"math/big"
	"math/rand"
	"net/http"
	"strconv"
	"strings"
	"time"
	"flag"

	"github.com/ethereum/go-ethereum"
	"github.com/incognitochain/bridge-eth/common/base58"
	"github.com/incognitochain/bridge-eth/consensus/signatureschemes/bridgesig"
	"github.com/incognitochain/portal3-eth/portal/portalv3"
	"github.com/stretchr/testify/suite"
	"golang.org/x/crypto/sha3"

	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/ethereum/go-ethereum/light"
	"github.com/ethereum/go-ethereum/params"
	"github.com/ethereum/go-ethereum/rlp"
	"github.com/ethereum/go-ethereum/trie"

	"github.com/incognitochain/bridge-eth/erc20"
	"github.com/incognitochain/bridge-eth/rpccaller"
	"github.com/stretchr/testify/require"
)

type CommonRes struct {
	rpccaller.RPCBaseRes
	Result interface{} `json:"Result"`
}

type IssuingETHRes struct {
	rpccaller.RPCBaseRes
	Result interface{} `json:"Result"`
}

type CustodianTopup struct {
	rpccaller.RPCBaseRes
	Result interface{} `json:"Result"`
}

type CustodianTopupPorting struct {
	rpccaller.RPCBaseRes
	Result interface{} `json:"Result"`
}

type BurningForDepositToSCRes struct {
	rpccaller.RPCBaseRes
	Result interface{} `json:"Result"`
}

type Receipt struct {
	Result *types.Receipt `json:"result"`
}

type NormalResult struct {
	Result interface{} `json:"result"`
}

type PortalV3Base struct {
	suite.Suite
	IncBurningAddrStr string
	IncPrivKeyStr     string
	IncPaymentAddrStr string

	GeneratedPrivKeyForSC ecdsa.PrivateKey
	GeneratedPubKeyForSC  ecdsa.PublicKey

	IncBridgeHost      string
	IncRPCHost         string
	IncEtherTokenIDStr string

	BnbAddStr string
	BtcAddStr string

	BnbRemoteAddStr string
	BtcRemoteAddStr string

	EtherAddressStr string
	ETHPrivKeyStr   string
	ETHOwnerAddrStr string

	ETHHost    string
	ETHPrivKey *ecdsa.PrivateKey
	ETHClient  *ethclient.Client

	Portalv3             common.Address
	KBNTradeDeployedAddr common.Address

	KyberContractAddr common.Address

	auth                  *bind.TransactOpts
	portalV3Inst          *portalv3.Portalv3

	USDTAddress common.Address
	USDCAddress common.Address
}

// Make sure that VariableThatShouldStartAtFive is set to five
// before each test
func main() {
	// network := flag.String("network", "http://51.83.36.184:20002", "network chain")
	amount := flag.Float64("amount", 0.0001, "amount ETH")
	// privKeyAcc := flag.String("privateKey","112t8rnsqDitXckbWMPo4wGbjwyPtYHywApPqfZVQNatrMzfDLERCmHTBPsHUZjhzFLxdVmQ6m6W5ppbK4PZCzWVjEBvi3a7SVrtVpd6GZSL","privateKey Incognito account deposit")
	paymentKeyAcc := flag.String("paymentKey", "12S3Xv2N9KvGZivRESKUQWv6obrghwykAUxqc85nTcZQ9AJMxnJe4Ct97BjAm5vFJ9bhhaHXDCmGfbXEqbS766DyeMLLeYksDM1FmSg", "paymentkey Incognito account deposit")

	flag.Parse()
	
	var pt PortalV3Base

	pt.IncBurningAddrStr = "12RxahVABnAVCGP3LGwCn8jkQxgw7z1x14wztHzn455TTVpi1wBq9YGwkRMQg3J4e657AbAnCvYCJSdA9czBUNuCKwGSRQt55Xwz8WA"
	pt.IncPrivKeyStr = "112t8rnsqDitXckbWMPo4wGbjwyPtYHywApPqfZVQNatrMzfDLERCmHTBPsHUZjhzFLxdVmQ6m6W5ppbK4PZCzWVjEBvi3a7SVrtVpd6GZSL"
	pt.IncPaymentAddrStr = *paymentKeyAcc

	pt.BnbAddStr = "6abd698ea7ddd1f98b1ecaaddab5db0453b8363ff092f0d8d7d4c6b1155fb693"
	pt.BtcAddStr = "ef5947f70ead81a76a53c7c8b7317dd5245510c665d3a13921dc9a581188728b"
	pt.BnbRemoteAddStr = "tbnb172pnrmd0409237jwlq5qjhw2s2r7lq6ukmaeke"
	pt.BtcRemoteAddStr = "mhpTRAPdmyB1PUvXR2yqaSBK8ZJhEQ8rEw"

	pt.EtherAddressStr = "0x0000000000000000000000000000000000000000"
	pt.IncEtherTokenIDStr = "ffd8d42dc40a8d166ea4848baf8b5f6e9fe0e9c30d60062eb7d44a8df9e00854"
	pt.ETHPrivKeyStr = "A5AE26C7154410DF235BC8669FFD27C0FC9D3068C21E469A4CC68165C68CD5CB"
	pt.ETHOwnerAddrStr = "cE40cE511A5D084017DBee7e3fF3e455ea32D85c"

	pt.ETHHost = "https://kovan.infura.io/v3/93fe721349134964aa71071a713c5cef"
	pt.IncBridgeHost = "http://51.79.76.38:8334"
	pt.IncRPCHost = "http://51.79.76.38:8334"

	ETHPrivKey, ETHClient, _ := ethInstance(pt.ETHPrivKeyStr, pt.ETHHost)

	pt.ETHClient = ETHClient
	pt.ETHPrivKey = ETHPrivKey
	pt.auth = bind.NewKeyedTransactor(ETHPrivKey)

	pt.Portalv3 = common.HexToAddress("0x6D53de7aFa363F779B5e125876319695dC97171E")
	pt.portalV3Inst, _ = portalv3.NewPortalv3(pt.Portalv3, pt.ETHClient)

	// pt.USDTAddress = common.HexToAddress("0x3a829f4b97660d970428cd370c4e41cbad62092b")
	// fmt.Printf("usdt address: %s\n", pt.USDTAddress.Hex())
	// pt.USDCAddress = common.HexToAddress("0x75b0622cec14130172eae9cf166b92e5c112faff")
	// fmt.Printf("usdc address: %s\n", pt.USDCAddress.Hex())

	// fmt.Println("------------ deposit ETH-------------")

	DepositingEther := float64(*amount)
	
	txHash := pt.depositETH(
		DepositingEther,
		pt.IncPaymentAddrStr,
	)
	time.Sleep(5 * time.Second)
	_, ethBlockHash, ethTxIdx, ethDepositProof, _ := getETHDepositProof(pt.ETHHost, txHash)
	// require.Equal(pt.T(), nil, err)
	fmt.Println("BlockHash : ", ethBlockHash)
	fmt.Println("TxIndex : ", ethTxIdx)
	fmt.Println("ProofStrs : ", ethDepositProof)

	// fmt.Println("------------  deposit USDT --------------")
	// txHash = pt.depositERC20ToBridge(
	// 	big.NewInt(0.01*1e6),
	// 	pt.USDTAddress,
	// 	pt.IncPaymentAddrStr,
	// )

	// _, ethBlockHash, ethTxIdx, ethDepositProof, _ = getETHDepositProof(pt.ETHHost, txHash)
	// // require.Equal(pg.T(), nil, err)
	// fmt.Println("depositProof usdt ---- : ", ethBlockHash, ethTxIdx, ethDepositProof)
}

func (portalV3Suite *PortalV3Base) getBalanceOnETHNet(
	tokenAddr common.Address,
	ownerAddr common.Address,
) *big.Int {
	if tokenAddr.Hex() == portalV3Suite.EtherAddressStr {
		balance, err := portalV3Suite.ETHClient.BalanceAt(context.Background(), ownerAddr, nil)
		require.Equal(portalV3Suite.T(), nil, err)
		return balance
	}
	// erc20 token
	instance, err := erc20.NewErc20(tokenAddr, portalV3Suite.ETHClient)
	require.Equal(portalV3Suite.T(), nil, err)

	balance, err := instance.BalanceOf(&bind.CallOpts{}, ownerAddr)
	require.Equal(portalV3Suite.T(), nil, err)
	return balance
}

func (portalV3Suite *PortalV3Base) connectToETH() {
	privKeyHex := portalV3Suite.ETHPrivKeyStr
	privKey, err := crypto.HexToECDSA(privKeyHex)
	require.Equal(portalV3Suite.T(), nil, err)

	fmt.Printf("Sign Txs with address: %s\n", crypto.PubkeyToAddress(privKey.PublicKey).Hex())

	network := "development"
	fmt.Printf("Connecting to network %s\n", network)
	client, err := ethclient.Dial(portalV3Suite.ETHHost)
	require.Equal(portalV3Suite.T(), nil, err)

	portalV3Suite.ETHClient = client
	portalV3Suite.ETHPrivKey = privKey
}

func (portalV3Suite *PortalV3Base) depositETH(
	amt float64,
	incPaymentAddrStr string,
) common.Hash {
	c, _ := portalv3.NewPortalv3(portalV3Suite.Portalv3, portalV3Suite.ETHClient)
	// require.Equal(portalV3Suite.T(), nil, err)

	auth := bind.NewKeyedTransactor(portalV3Suite.ETHPrivKey)
	auth.Value = big.NewInt(int64(amt * params.Ether))
	tx, _ := c.Deposit(auth, incPaymentAddrStr)
	// require.Equal(portalV3Suite.T(), nil, err)
	txHash := tx.Hash()

	if err := wait(portalV3Suite.ETHClient, txHash); err != nil {
		require.Equal(portalV3Suite.T(), nil, err)
	}
	fmt.Printf("deposited, txHash: %x\n", txHash[:])
	return txHash
}

func (portalV3Suite *PortalV3Base) depositERC20ToBridge(
	amt *big.Int,
	tokenAddr common.Address,
	incPaymentAddrStr string,
) common.Hash {
	auth := bind.NewKeyedTransactor(portalV3Suite.ETHPrivKey)
	c, _ := portalv3.NewPortalv3(portalV3Suite.Portalv3, portalV3Suite.ETHClient)
	// require.Equal(portalV3Suite.T(), nil, err)

	erc20Token, _ := erc20.NewErc20(tokenAddr, portalV3Suite.ETHClient)
	auth.GasPrice = big.NewInt(50000000000)
	tx2, _ := erc20Token.Approve(auth, portalV3Suite.Portalv3, amt)
	tx2Hash := tx2.Hash()
	fmt.Printf("Approve tx, txHash: %x\n", tx2Hash[:])
	// require.Equal(portalV3Suite.T(), nil, apprErr)
	time.Sleep(15 * time.Second)
	auth.GasPrice = big.NewInt(50000000000)
	tx, _ := c.DepositERC20(auth, tokenAddr, amt, incPaymentAddrStr)
	// require.NotEqual(portalV3Suite.T(), nil, err)
	txHash := tx.Hash()

	if err := wait(portalV3Suite.ETHClient, txHash); err != nil {
		require.Equal(portalV3Suite.T(), nil, err)
	}
	fmt.Printf("deposited erc20 token to bridge, txHash: %x\n", txHash[:])
	return txHash
}

func (portalV3Suite *PortalV3Base) callCustodianDeposit(
	ethDepositProof []string,
	ethBlockHash string,
	ethTxIdx uint,
) (map[string]interface{}, error) {
	rpcClient := rpccaller.NewRPCClient()
	remoteAddresses := map[string]interface{}{
		portalV3Suite.BnbAddStr: portalV3Suite.BnbRemoteAddStr,
		portalV3Suite.BtcAddStr: portalV3Suite.BtcRemoteAddStr,
	}
	meta := map[string]interface{}{
		"RemoteAddresses": remoteAddresses,
		"BlockHash":       ethBlockHash,
		"ProofStrs":       ethDepositProof,
		"TxIndex":         ethTxIdx,
	}
	paramsRPC := []interface{}{
		portalV3Suite.IncPrivKeyStr,
		nil,
		5,
		-1,
		meta,
	}
	var res IssuingETHRes
	err := rpcClient.RPCCall(
		"",
		portalV3Suite.IncRPCHost,
		"",
		"createandsendtxwithcustodiandepositv3",
		paramsRPC,
		&res,
	)
	if err != nil {
		return nil, err
	}

	response, _ := json.Marshal(res)
	fmt.Println("Custodian deposit get response", string(response))

	if res.RPCError != nil {
		return nil, errors.New(res.RPCError.Message)
	}
	return res.Result.(map[string]interface{}), nil
}

func (portalV3Suite *PortalV3Base) callCustodianTopup(
	ethDepositProof []string,
	ethBlockHash string,
	ethTxIdx uint,
	depositAmt *big.Int,
	freeCollateralAmount *big.Int,
	pToken string,
	collateralToken string,
) (map[string]interface{}, error) {
	rpcClient := rpccaller.NewRPCClient()
	meta := map[string]interface{}{
		"IncognitoAddress":     portalV3Suite.IncPaymentAddrStr,
		"DepositedAmount":      depositAmt.Uint64(),
		"FreeCollateralAmount": freeCollateralAmount.Uint64(),
		"PTokenId":             pToken,
		"CollateralTokenId":    collateralToken,
		"BlockHash":            ethBlockHash,
		"TxIndex":              ethTxIdx,
		"ProofStrs":            ethDepositProof,
	}
	paramsRPC := []interface{}{
		portalV3Suite.IncPrivKeyStr,
		nil,
		-1,
		0,
		meta,
	}
	var res CustodianTopup
	err := rpcClient.RPCCall(
		"",
		portalV3Suite.IncRPCHost,
		"",
		"createandsendcustodiantopupv3",
		paramsRPC,
		&res,
	)
	if err != nil {
		return nil, err
	}

	response, _ := json.Marshal(res)
	fmt.Println("Custodian TOPUP get response", string(response))

	if res.RPCError != nil {
		return nil, errors.New(res.RPCError.Message)
	}
	return res.Result.(map[string]interface{}), nil
}

func (portalV3Suite *PortalV3Base) callCustodianTopupPorting(
	ethDepositProof []string,
	ethBlockHash string,
	ethTxIdx uint,
	portingId string,
	depositAmt *big.Int,
	freeCollateralAmount *big.Int,
	pToken string,
	collateralToken string,
) (map[string]interface{}, error) {
	rpcClient := rpccaller.NewRPCClient()
	meta := map[string]interface{}{
		"PortingID":            portingId,
		"IncognitoAddress":     portalV3Suite.IncPaymentAddrStr,
		"DepositedAmount":      depositAmt.Uint64(),
		"FreeCollateralAmount": freeCollateralAmount.Uint64(),
		"PTokenId":             pToken,
		"CollateralTokenId":    collateralToken,
		"BlockHash":            ethBlockHash,
		"TxIndex":              ethTxIdx,
		"ProofStrs":            ethDepositProof,
	}
	paramsRPC := []interface{}{
		portalV3Suite.IncPrivKeyStr,
		nil,
		-1,
		0,
		meta,
	}
	var res CustodianTopupPorting
	err := rpcClient.RPCCall(
		"",
		portalV3Suite.IncRPCHost,
		"",
		"createandsendtopupwaitingportingv3",
		paramsRPC,
		&res,
	)
	if err != nil {
		return nil, err
	}

	response, _ := json.Marshal(res)
	fmt.Println("Custodian TOPUP PORTING get response", string(response))

	if res.RPCError != nil {
		return nil, errors.New(res.RPCError.Message)
	}
	return res.Result.(map[string]interface{}), nil
}

func (portalV3Suite *PortalV3Base) callCustodianWithdraw(
	CustodianPrivateKey string,
	CustodianIncAddress string,
	CustodianExtAddress string,
	ExternalTokenID string,
	AmountStr string,
) (map[string]interface{}, error) {
	rpcClient := rpccaller.NewRPCClient()
	meta := map[string]interface{}{
		"CustodianIncAddress": CustodianIncAddress,
		"CustodianExtAddress": CustodianExtAddress,
		"ExternalTokenID":     ExternalTokenID,
		"Amount":              AmountStr,
	}
	// fmt.Println("meta body :",meta )
	paramsRPC := []interface{}{
		CustodianPrivateKey,
		nil,
		5,
		-1,
		meta,
	}
	var res IssuingETHRes
	err := rpcClient.RPCCall(
		"",
		portalV3Suite.IncRPCHost,
		"",
		"createandsendtxwithcustodianwithdrawrequestv3",
		paramsRPC,
		&res,
	)
	if err != nil {
		return nil, err
	}

	response, _ := json.Marshal(res)
	fmt.Println("Custodian withdraw get response", string(response))

	if res.RPCError != nil {
		return nil, errors.New(res.RPCError.Message)
	}
	return res.Result.(map[string]interface{}), nil
}

func (portalV3Suite *PortalV3Base) callUnlockCollateralToken(
	incTokenIDStr string,
	amount *big.Int,
	remoteAddrStr string,
	burningMethod string,
) (map[string]interface{}, error) {
	rpcClient := rpccaller.NewRPCClient()
	meta := map[string]interface{}{
		"TokenID":     incTokenIDStr,
		"TokenTxType": 1,
		"TokenName":   "",
		"TokenSymbol": "",
		"TokenAmount": amount.Uint64(),
		"TokenReceivers": map[string]uint64{
			portalV3Suite.IncBurningAddrStr: amount.Uint64(),
		},
		"RemoteAddress": remoteAddrStr,
		"Privacy":       true,
		"TokenFee":      0,
	}
	paramsRPC := []interface{}{
		portalV3Suite.IncPrivKeyStr,
		nil,
		5,
		-1,
		meta,
		"",
		0,
	}
	var res BurningForDepositToSCRes
	err := rpcClient.RPCCall(
		"",
		portalV3Suite.IncRPCHost,
		"",
		burningMethod,
		paramsRPC,
		&res,
	)
	if err != nil {
		fmt.Println("calling burning ptokens err: ", err)
		return nil, err
	}
	bb, _ := json.Marshal(res)
	fmt.Println("calling burning ptokens res: ", string(bb))
	if res.RPCError != nil {
		return nil, errors.New(res.RPCError.Message)
	}
	return res.Result.(map[string]interface{}), nil
}

func (portalV3Suite *PortalV3Base) genKeysPairForSC() {
	incPriKeyBytes, _, err := base58.Base58Check{}.Decode(portalV3Suite.IncPrivKeyStr)
	fmt.Println(incPriKeyBytes)
	require.Equal(portalV3Suite.T(), nil, err)

	portalV3Suite.GeneratedPrivKeyForSC, portalV3Suite.GeneratedPubKeyForSC = bridgesig.KeyGen(incPriKeyBytes)
}

func randomizeTimestamp() string {
	randomTime := rand.Int63n(time.Now().Unix()-94608000) + 94608000
	randomNow := time.Unix(randomTime, 0)
	return randomNow.String()
}

func rlpHash(x interface{}) (h common.Hash) {
	hw := sha3.NewLegacyKeccak256()
	rlp.Encode(hw, x)
	hw.Sum(h[:0])
	return h
}

func wait(client *ethclient.Client, tx common.Hash) error {
	ctx := context.Background()
	for range time.Tick(10 * time.Second) {
		_, err := client.TransactionReceipt(ctx, tx)
		if err == nil {
			break
		} else if err == ethereum.NotFound {
			continue
		} else {
			return err
		}
	}
	return nil
}

func getETHDepositProof(
	url string,
	txHash common.Hash,
) (*big.Int, string, uint, []string, error) {
	// Get tx content
	txContent, err := getETHTransactionByHash(url, txHash)
	if err != nil {
		fmt.Println("Cannot get transaction by hash : ", err)
		return nil, "", 0, nil, err
	}
	blockHash := txContent["blockHash"].(string)
	if err != nil {
		return nil, "", 0, nil, err
	}
	txIndexStr, success := txContent["transactionIndex"].(string)
	if !success {
		return nil, "", 0, nil, errors.New("Cannot find transactionIndex field")
	}
	txIndex, err := strconv.ParseUint(txIndexStr[2:], 16, 64)
	if err != nil {
		return nil, "", 0, nil, err
	}

	// Get tx's block for constructing receipt trie
	blockNumString, success := txContent["blockNumber"].(string)
	if !success {
		return nil, "", 0, nil, errors.New("Cannot find blockNumber field")
	}
	blockNumber := new(big.Int)
	_, success = blockNumber.SetString(blockNumString[2:], 16)
	if !success {
		return nil, "", 0, nil, errors.New("Cannot convert blockNumber into integer")
	}
	blockHeader, err := getETHBlockByHash(url, blockHash)
	if err != nil {
		return nil, "", 0, nil, err
	}

	// Get all sibling Txs
	siblingTxs, success := blockHeader["transactions"].([]interface{})
	if !success {
		return nil, "", 0, nil, errors.New("Cannot find transactions field")
	}

	// Constructing the receipt trie (source: go-ethereum/core/types/derive_sha.go)
	keybuf := new(bytes.Buffer)
	receiptTrie := new(trie.Trie)
	for i, tx := range siblingTxs {
		siblingReceipt, err := getETHTransactionReceipt(url, common.HexToHash(tx.(string)))
		if err != nil {
			return nil, "", 0, nil, err
		}
		keybuf.Reset()
		rlp.Encode(keybuf, uint(i))
		encodedReceipt, err := rlp.EncodeToBytes(siblingReceipt)
		if err != nil {
			return nil, "", 0, nil, err
		}
		receiptTrie.Update(keybuf.Bytes(), encodedReceipt)
	}

	// Constructing the proof for the current receipt (source: go-ethereum/trie/proof.go)
	proof := light.NewNodeSet()
	keybuf.Reset()
	rlp.Encode(keybuf, uint(txIndex))
	err = receiptTrie.Prove(keybuf.Bytes(), 0, proof)
	if err != nil {
		return nil, "", 0, nil, err
	}

	nodeList := proof.NodeList()
	encNodeList := make([]string, 0)
	for _, node := range nodeList {
		str := base64.StdEncoding.EncodeToString(node)
		encNodeList = append(encNodeList, str)
	}

	return blockNumber, blockHash, uint(txIndex), encNodeList, nil
}

// getTransactionByHashToInterface returns the transaction as a map[string]interface{} type
func getETHTransactionByHash(
	url string,
	tx common.Hash,
) (map[string]interface{}, error) {
	rpcClient := rpccaller.NewRPCClient()
	inputParams := []interface{}{tx.String()}
	var res NormalResult
	err := rpcClient.RPCCall(
		"",
		url,
		"",
		"eth_getTransactionByHash",
		inputParams,
		&res,
	)
	if err != nil {
		return nil, err
	}
	if res.Result == nil {
		return nil, errors.New("eth tx by hash not found")
	}
	return res.Result.(map[string]interface{}), nil
}

func getETHBlockByHash(
	url string,
	blockHash string,
) (map[string]interface{}, error) {
	rpcClient := rpccaller.NewRPCClient()
	inputParams := []interface{}{blockHash, false}
	var res NormalResult
	err := rpcClient.RPCCall(
		"",
		url,
		"",
		"eth_getBlockByHash",
		inputParams,
		&res,
	)
	if err != nil {
		return nil, err
	}
	return res.Result.(map[string]interface{}), nil
}

func getETHTransactionReceipt(url string, txHash common.Hash) (*types.Receipt, error) {
	rpcClient := rpccaller.NewRPCClient()
	inputParams := []interface{}{txHash.String()}
	var res Receipt
	err := rpcClient.RPCCall(
		"",
		url,
		"",
		"eth_getTransactionReceipt",
		inputParams,
		&res,
	)
	if err != nil {
		return nil, err
	}
	return res.Result, nil
}

func getPortalCustodianDepositStatusv3(url string, txHash string) (map[string]interface{}, error) {
	rpcClient := rpccaller.NewRPCClient()
	transactionId := map[string]interface{}{"DepositTxID": txHash}
	inputParams := []interface{}{transactionId}
	var res CommonRes
	err := rpcClient.RPCCall(
		"",
		url,
		"",
		"getportalcustodiandepositstatusv3",
		inputParams,
		&res,
	)
	if err != nil || res.Result == nil {
		return nil, err
	}
	return res.Result.(map[string]interface{}), nil
}

func getCustodianTopupStatusV3(url string, txHash string) (map[string]interface{}, error) {
	rpcClient := rpccaller.NewRPCClient()
	transactionId := map[string]interface{}{"DepositTxID": txHash}
	inputParams := []interface{}{transactionId}
	var res CommonRes
	err := rpcClient.RPCCall(
		"",
		url,
		"",
		"getcustodiantopupstatusv3",
		inputParams,
		&res,
	)
	if err != nil || res.Result == nil {
		return nil, err
	}
	return res.Result.(map[string]interface{}), nil
}

func getCustodianTopupPortingStatusV3(url string, txHash string) (map[string]interface{}, error) {
	rpcClient := rpccaller.NewRPCClient()
	transactionId := map[string]interface{}{"DepositTxID": txHash}
	inputParams := []interface{}{transactionId}
	var res CommonRes
	err := rpcClient.RPCCall(
		"",
		url,
		"",
		"getcustodiantopupwaitingportingstatusv3",
		inputParams,
		&res,
	)
	if err != nil || res.Result == nil {
		return nil, err
	}
	return res.Result.(map[string]interface{}), nil
}

func getPortalCustodianWithdrawV3(url, txHash, rpcMethod string) (map[string]interface{}, error) {
	rpcClient := rpccaller.NewRPCClient()
	transactionId := map[string]interface{}{"TxId": txHash}
	inputParams := []interface{}{transactionId}
	var res CommonRes
	err := rpcClient.RPCCall(
		"",
		url,
		"",
		rpcMethod,
		inputParams,
		&res,
	)
	if err != nil || res.Result == nil {
		return nil, err
	}
	return res.Result.(map[string]interface{}), nil
}

func getPortalCustodianWithdrawProofv3(url, txHash, rpcMethod string, metadataType uint) (string, error) {
	if len(txHash) == 0 {
		txHash = "87c89c1c19cec3061eff9cfefdcc531d9456ac48de568b3974c5b0a88d5f3834"
	}
	payload := strings.NewReader(fmt.Sprintf("{\n    \"id\": 1,\n    \"jsonrpc\": \"1.0\",\n    \"method\": \"%s\",\n \"params\": [\n{\"TxID\":\t\"%s\", \"MetadataType\": \t%v}]\n}", rpcMethod, txHash, metadataType))
	req, _ := http.NewRequest("POST", url, payload)
	res, err := http.DefaultClient.Do(req)
	if err != nil {
		return "", err
	}

	defer res.Body.Close()
	body, err := ioutil.ReadAll(res.Body)
	if err != nil {
		return "", err
	}
	return string(body), nil
}

// func getAndDecodeProofV3(
// 	incBridgeHost string,
// 	txID string,
// 	rpcMethod string,
// 	metadataType uint,
// ) (*decodedProof, error) {
// 	body, err := getPortalCustodianWithdrawProofv3(incBridgeHost, txID, rpcMethod, metadataType)
// 	if err != nil {
// 		return nil, err
// 	}
// 	if len(body) < 1 {
// 		return nil, fmt.Errorf("portal withdraw proof to SC not found")
// 	}

// 	r := getProofResult{}
// 	err = json.Unmarshal([]byte(body), &r)
// 	if err != nil {
// 		return nil, err
// 	}
// 	return decodeProof(&r)
// }

// func decodeProof(r *getProofResult) (*decodedProof, error) {
// 	inst := decode(r.Result.Instruction)
// 	fmt.Printf("inst: %d %x\n", len(inst), inst)
// 	fmt.Printf("instHash (isWithdrawed, without height): %x\n", keccak256(inst))

// 	// Block heights
// 	fmt.Println(r.Result.BeaconHeight)
// 	beaconHeight := big.NewInt(0).SetBytes(decode(r.Result.BeaconHeight))
// 	fmt.Println(beaconHeight.String())
// 	beaconInstRoot := decode32(r.Result.BeaconInstRoot)
// 	beaconInstPath := make([][32]byte, len(r.Result.BeaconInstPath))
// 	beaconInstPathIsLeft := make([]bool, len(r.Result.BeaconInstPath))
// 	for i, path := range r.Result.BeaconInstPath {
// 		beaconInstPath[i] = decode32(path)
// 		beaconInstPathIsLeft[i] = r.Result.BeaconInstPathIsLeft[i]
// 	}
// 	// fmt.Printf("beaconInstRoot: %x\n", beaconInstRoot)

// 	beaconBlkData := toByte32(decode(r.Result.BeaconBlkData))
// 	fmt.Printf("data: %s %s\n", r.Result.BeaconBlkData, r.Result.BeaconInstRoot)
// 	fmt.Printf("expected beaconBlkHash: %x\n", keccak256(beaconBlkData[:], beaconInstRoot[:]))

// 	beaconSigVs, beaconSigRs, beaconSigSs, err := decodeSigs(r.Result.BeaconSigs)
// 	if err != nil {
// 		return nil, err
// 	}

// 	beaconSigIdxs := []*big.Int{}
// 	for _, sIdx := range r.Result.BeaconSigIdxs {
// 		beaconSigIdxs = append(beaconSigIdxs, big.NewInt(int64(sIdx)))
// 	}

// 	return &decodedProof{
// 		Instruction:     inst,
// 		Heights:         beaconHeight,
// 		InstPaths:       beaconInstPath,
// 		InstPathIsLefts: beaconInstPathIsLeft,
// 		InstRoots:       beaconInstRoot,
// 		BlkData:         beaconBlkData,
// 		SigIdxs:         beaconSigIdxs,
// 		SigVs:           beaconSigVs,
// 		SigRs:           beaconSigRs,
// 		SigSs:           beaconSigSs,
// 	}, nil
// }

// func decodeSigs(sigs []string) (
// 	sigVs []uint8,
// 	sigRs [][32]byte,
// 	sigSs [][32]byte,
// 	err error,
// ) {
// 	sigVs = make([]uint8, len(sigs))
// 	sigRs = make([][32]byte, len(sigs))
// 	sigSs = make([][32]byte, len(sigs))
// 	for i, sig := range sigs {
// 		v, r, s, e := bridgesig.DecodeECDSASig(decode(sig))
// 		if e != nil {
// 			err = e
// 			return
// 		}
// 		sigVs[i] = uint8(v)
// 		copy(sigRs[i][:], r)
// 		copy(sigSs[i][:], s)
// 	}
// 	return
// }

// func decode(s string) []byte {
// 	d, _ := hex.DecodeString(s)
// 	return d
// }

// func decode32(s string) [32]byte {
// 	return toByte32(decode(s))
// }

// func keccak256(b ...[]byte) [32]byte {
// 	h := crypto.Keccak256(b...)
// 	r := [32]byte{}
// 	copy(r[:], h)
// 	return r
// }


func ethInstance(ethPrivate string, ethEnpoint string) (*ecdsa.PrivateKey, *ethclient.Client, error) {
	privKey, err := crypto.HexToECDSA(ethPrivate)
	if err != nil {
		return nil, nil, err
	}
	fmt.Printf("Sign Txs with address: %s\n", crypto.PubkeyToAddress(privKey.PublicKey).Hex())

	network := "development"
	fmt.Printf("Connecting to network %s\n", network)
	client, err := ethclient.Dial(ethEnpoint)
	if err != nil {
		return nil, nil, err
	}
	return privKey, client, nil
}