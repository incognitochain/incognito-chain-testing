package main

import (
	"context"
	"crypto/ecdsa"
	"encoding/json"
	"errors"
	"fmt"
	"math/big"

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

	"github.com/incognitochain/bridge-eth/bridge/kbntrade"
	"github.com/incognitochain/bridge-eth/bridge/uniswap"
)

const (
	ethWaitTn    = 5
	confirmWaitTn = 80
	incWaitTn     = 100
)


type TnIssuingETHRes struct {
	rpccaller.RPCBaseRes
	Result interface{} `json:"Result"`
}

type TnBurningForDepositToSCRes struct {
	rpccaller.RPCBaseRes
	Result interface{} `json:"Result"`
}

type TnBalanceIncAccount struct {
	Result interface{} `json:"Result"`
}

type TnTxhashInC struct {
	Result interface{} `json:"Result"`
}


// Define the suite, and absorb the built-in basic suite
// functionality from testify - including assertion methods.
type TnTradingTestSuite struct {
	suite.Suite
	IncBurningAddrStr string
	IncPrivKeyStr     string
	IncPaymentAddrStr string

	GeneratedPrivKeyForSC ecdsa.PrivateKey
	GeneratedPubKeyForSC  ecdsa.PublicKey

	IncEtherTokenIDStr string
	IncDAITokenIDStr   string
	IncSAITokenIDStr   string

	IncBridgeHost string
	IncRPCHost    string

	EtherAddressStr string
	DAIAddressStr   string
	SAIAddressStr   string

	ETHPrivKeyStr   string
	ETHOwnerAddrStr string

	ETHHost    string
	ETHPrivKey *ecdsa.PrivateKey
	ETHClient  *ethclient.Client

	VaultAddr common.Address

	UniswapTradeDeployedAddr common.Address
	UniswapRouteContractAddr common.Address

	KBNTradeDeployedAddr   common.Address
	KyberContractAddr      common.Address
	KyberTradeDeployedAddr common.Address

	MKRAddressStr string
	BATAddressStr string
	KNCAddressStr string
	CKNAddressStr string

	IncMKRTokenIDStr string
	IncBATTokenIDStr string
	IncKNCTokenIDStr string
	IncCKNTokenIDStr string

	WETHAddr             common.Address
	EtherAddressStrKyber string

	IncKBNTokenIDStr  string
	IncSALTTokenIDStr string
	IncOMGTokenIDStr  string
	IncSNTTokenIDStr  string
	IncPOLYTokenIDStr string
	IncZILTokenIDStr  string
	IncMRKTokenIDStr  string
	IncUSDCTokenIDStr string
	IncWBTCTokenIDStr string

	USDCAddressStr string
	WBTCAddressStr string
	KBNAddressStr  string
	SALTAddressStr string
	OMGAddressStr  string
	SNTAddressStr  string
	POLYAddressStr string
	ZILAddressStr  string
	WETHAddressStr string

	MRKAddressStr string

	DepositingEther float64
}

// Make sure that VariableThatShouldStartAtFive is set to five
// before each test
func (tradingSuite *TnTradingTestSuite) SetupSuite() {
	fmt.Println("Setting up the suite...")

	// 0x kovan env
	tradingSuite.IncBurningAddrStr = "12RxahVABnAVCGP3LGwCn8jkQxgw7z1x14wztHzn455TTVpi1wBq9YGwkRMQg3J4e657AbAnCvYCJSdA9czBUNuCKwGSRQt55Xwz8WA"
	tradingSuite.IncPrivKeyStr = "112t8rnX3VTd3MTWMpfbYP8HGY4ToAaLjrmUYzfjJBrAcb8iPLkNqvVDXWrLNiFV5yb2NBpR3FDZj3VW8GcLUwRdQ61hPMWP3YrREZAZ1UbH"
	tradingSuite.IncPaymentAddrStr = "12S6R8HfTyL74bggg47LX88RSvBPaMPBMEMoo6yx9WQ4EgLiYERXXcE2Mv2HrCsFuKhBsTfrYMeH82Bus5MHQGt3xHwoxX4v2qM5jRE"
	// tradingSuite.IncPrivKeyStr = "112t8rnhdyiruPke58LNeqwpzxn3cGQsfnS4dqec6P9HWPwNH7VKPgdXw9svDXp5djM4mQrMZnxwW7sjk5NLBkHXC3pJHBMsoqJi8sNUd47G"
	// tradingSuite.IncPaymentAddrStr = "12S4HcgzM2zQeq41Bh9w8Ce5YETiQitoTZmTjCHLvvbwmoy8S9Py66wBjCqTgziWPbMpWEWPA2jRabwDmTk2TYV4nAzBN3SwjYN4zfE"

	tradingSuite.ETHPrivKeyStr = "A5AE26C7154410DF235BC8669FFD27C0FC9D3068C21E469A4CC68165C68CD5CB" //testnet
	tradingSuite.ETHOwnerAddrStr = "cE40cE511A5D084017DBee7e3fF3e455ea32D85c"                       //testnet

	tradingSuite.WETHAddressStr = "0xd0a1e359811322d97991e03f863a0c30c2cf029c" // testnet
	tradingSuite.EtherAddressStrKyber = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

	tradingSuite.IncEtherTokenIDStr = "ffd8d42dc40a8d166ea4848baf8b5f6e9fe0e9c30d60062eb7d44a8df9e00854" //testnet
	tradingSuite.IncDAITokenIDStr = "c7545459764224a000a9b323850648acf271186238210ce474b505cd17cc93a0"
	tradingSuite.IncSAITokenIDStr = "1d74e5e225e1f09ae38c496d3102aef464dcbd04ad3ac071e6e44077b8a740c9"
	tradingSuite.IncBATTokenIDStr = "d1b4c73821edc76963fdeda2236fe89478249a1f7b952de2a7135c0bc0cbe6dc"
	tradingSuite.IncKNCTokenIDStr = "d6644f62d0ef0475335ae7bb6103f358979cbfcd2b85481e3bde2b82101a095c" //testnet
	tradingSuite.IncPOLYTokenIDStr = "d0379b8ccc25e4940d5b94ace07dcfa3656a20814279ddf2674f6d7180f65440"
	tradingSuite.IncOMGTokenIDStr = "27322fa7fce2c4d4d5a0022d595a0eec56d7735751a3ba8bc7f10b358ab938bc"
	tradingSuite.IncZILTokenIDStr = "3c115c066028bb682af410c594546b58026095ff149dc30c061749ee163d9051"
	tradingSuite.IncKBNTokenIDStr = "d6644f62d0ef0475335ae7bb6103f358979cbfcd2b85481e3bde2b82101a095c"
	tradingSuite.IncSALTTokenIDStr = "06ce44eae35daf57b9b8158ab95c0cddda9bac208fc380236a318ef40f3ac2ef"
	tradingSuite.IncSNTTokenIDStr = "414a6459526e827321cedb6e574d2ba2eb267c5735b0a65991602a405fb753b7"
	tradingSuite.IncUSDCTokenIDStr = "61e1efbf6be9decc46fdf8250cdae5be12bee501b65f774a58af4513b645f6a3"
	tradingSuite.IncWBTCTokenIDStr = "4fb87c00dbe3933ae73c4dc37a37db0bca9aa9f55a2776dbd59cca2b02e72fc4"
	tradingSuite.IncMRKTokenIDStr = "641e37731c151e8b93ed48f6044836edac1e21d518b11c491774ba10b89ca5e5"
	tradingSuite.IncCKNTokenIDStr = "f3c421e4d7520936f3916a878ab361ef3fd6a831e81063ca3e7b80ab4d15a84e" //tteestnet

	tradingSuite.USDCAddressStr = "0x75b0622cec14130172eae9cf166b92e5c112faff"
	tradingSuite.WBTCAddressStr = "0xA0A5aD2296b38Bd3e3Eb59AAEAF1589E8d9a29A9"
	tradingSuite.MRKAddressStr = "0xef13C0c8abcaf5767160018d268f9697aE4f5375"
	tradingSuite.ZILAddressStr = "0xAb74653cac23301066ABa8eba62b9Abd8a8c51d6"
	tradingSuite.POLYAddressStr = "0xd92266fd053161115163a7311067F0A4745070b5"
	tradingSuite.OMGAddressStr = "0xdB7ec4E4784118D9733710e46F7C83fE7889596a"
	tradingSuite.KBNAddressStr = "0xad67cB4d63C9da94AcA37fDF2761AaDF780ff4a2"
	tradingSuite.SALTAddressStr = "0x6fEE5727EE4CdCBD91f3A873ef2966dF31713A04"
	tradingSuite.SNTAddressStr = "0x4c99B04682fbF9020Fcb31677F8D8d66832d3322"
	tradingSuite.BATAddressStr = "0x9f8cfb61d3b2af62864408dd703f9c3beb55dff7" //BAT
	tradingSuite.KNCAddressStr = "0xad67cb4d63c9da94aca37fdf2761aadf780ff4a2" //KNC  testnet
	tradingSuite.CKNAddressStr = "0x1d59Ee76304338fAc3a0eA9AE06E618C760D6042" //CKN
	tradingSuite.EtherAddressStr = "0x0000000000000000000000000000000000000000"
	tradingSuite.DAIAddressStr = "0x4f96fe3b7a6cf9725f59d353f723c1bdb64ca6aa" // DAI
	tradingSuite.SAIAddressStr = "0xc4375b7de8af5a38a93548eb8453a498222c4ff2" //SAI

	tradingSuite.ETHHost = "https://kovan.infura.io/v3/93fe721349134964aa71071a713c5cef"

	// tradingSuite.IncBridgeHost = "http://51.83.36.184:20002" //testnet 1
	// tradingSuite.IncRPCHost = "http://51.83.36.184:20002"    //testnet 1

	// tradingSuite.IncBridgeHost = "http://51.79.76.116:20003"  	//beacon test
	// tradingSuite.IncRPCHost = "http://51.79.76.116:20003"		//beacon test

	tradingSuite.IncBridgeHost = "http://51.161.119.66:9334" // testnet 2
	tradingSuite.IncRPCHost = "http://51.161.119.66:9334"    // testnet 2

	
	// tradingSuite.UniswapRouteContractAddr = common.HexToAddress("0xf164fC0Ec4E93095b804a4795bBe1e041497b92a")
	// tradingSuite.KyberContractAddr = common.HexToAddress("0x692f391bCc85cefCe8C237C01e1f636BbD70EA4D")

	// tradingSuite.UniswapTradeDeployedAddr = common.HexToAddress("0x7783C8c5AEC5cBFEF7311b4F4F33302DA6624d69") //testnet 1
	tradingSuite.UniswapTradeDeployedAddr = common.HexToAddress("0x39017F874291D5d8Aaec9de07E04f5f8047B1C9d") //testnet 2

// tradingSuite.VaultAddr = common.HexToAddress("0xE0D5e7217c6C4bc475404b26d763fAD3F14D2b86") //testnet 1
tradingSuite.VaultAddr = common.HexToAddress("0x7c7e371D1e25771f2242833C1A354dCE846f3ec8") // testnet 2
	// tradingSuite.KyberTradeDeployedAddr = common.HexToAddress("0xDD71ba9f17172a23F3e70ed70FFB96Fb403e4527")      // testnet 1
	tradingSuite.KyberTradeDeployedAddr = common.HexToAddress("0x18c1C19b31b08407633776AB24B26Cfac137099d") // testnet 2

	// generate a new keys pair for SC
	tradingSuite.genKeysPairForSC()

	// connect to ethereum network
	tradingSuite.connectToETH()

	tradingSuite.DepositingEther = float64(0.001)
}

func (tradingSuite *TnTradingTestSuite) TearDownSuite() {
	fmt.Println("Tearing down the suite...")
	tradingSuite.ETHClient.Close()
}

func (tradingSuite *TnTradingTestSuite) SetupTest() {
	fmt.Println("Setting up the test...")
}

func (tradingSuite *TnTradingTestSuite) TearDownTest() {
	fmt.Println("Tearing down the test...")
}

func TestTnTradingTestSuite(t *testing.T) {
	fmt.Println("Starting entry point for test suite...")

	tradingSuite := new(TnTradingTestSuite)
	suite.Run(t, tradingSuite)

	fmt.Println("Finishing entry point for test suite...")
}

func (tradingSuite *TnTradingTestSuite) getBalanceOnETHNet(
	tokenAddr common.Address,
	ownerAddr common.Address,
) *big.Int {
	if tokenAddr.Hex() == tradingSuite.EtherAddressStr {
		balance, err := tradingSuite.ETHClient.BalanceAt(context.Background(), ownerAddr, nil)
		require.Equal(tradingSuite.T(), nil, err)
		return balance
	}
	// erc20 token
	instance, err := erc20.NewErc20(tokenAddr, tradingSuite.ETHClient)
	require.Equal(tradingSuite.T(), nil, err)

	balance, err := instance.BalanceOf(&bind.CallOpts{}, ownerAddr)
	require.Equal(tradingSuite.T(), nil, err)
	return balance
}

func (tradingSuite *TnTradingTestSuite) connectToETH() {
	privKeyHex := tradingSuite.ETHPrivKeyStr
	privKey, err := crypto.HexToECDSA(privKeyHex)
	require.Equal(tradingSuite.T(), nil, err)

	fmt.Printf("Sign Txs with address: %s\n", crypto.PubkeyToAddress(privKey.PublicKey).Hex())

	network := "development"
	fmt.Printf("Connecting to network %s\n", network)
	client, err := ethclient.Dial(tradingSuite.ETHHost)
	require.Equal(tradingSuite.T(), nil, err)

	tradingSuite.ETHClient = client
	tradingSuite.ETHPrivKey = privKey
}

func (tradingSuite *TnTradingTestSuite) depositETH(
	amt float64,
	incPaymentAddrStr string,
) common.Hash {
	c, err := vault.NewVault(tradingSuite.VaultAddr, tradingSuite.ETHClient)
	require.Equal(tradingSuite.T(), nil, err)

	auth := bind.NewKeyedTransactor(tradingSuite.ETHPrivKey)
	auth.GasPrice = big.NewInt(90000000000)
	// auth.Nonce = big.NewInt(0)
	auth.Value = big.NewInt(int64(amt * params.Ether))
	tx, err := c.Deposit(auth, incPaymentAddrStr)
	require.Equal(tradingSuite.T(), nil, err)
	txHash := tx.Hash()

	if err := wait(tradingSuite.ETHClient, txHash); err != nil {
		require.Equal(tradingSuite.T(), nil, err)
	}
	fmt.Printf("Deposited to proof, txHash : %x\n", txHash[:])
	require.Equal(tradingSuite.T(), tradingSuite.getStatusTxhash(txHash), uint64(1), "tx on ether network failed")
	return txHash

}

func (tradingSuite *TnTradingTestSuite) depositERC20ToBridge(
	amt *big.Int,
	tokenAddr common.Address,
	incPaymentAddrStr string,
) common.Hash {
	auth := bind.NewKeyedTransactor(tradingSuite.ETHPrivKey)
	c, err := vault.NewVault(tradingSuite.VaultAddr, tradingSuite.ETHClient)
	require.Equal(tradingSuite.T(), nil, err)

	erc20Token, _ := erc20.NewErc20(tokenAddr, tradingSuite.ETHClient)
	auth.GasPrice = big.NewInt(100000000000)
	// auth.GasLimit = 1000000
	tx2, apprErr := erc20Token.Approve(auth, tradingSuite.VaultAddr, amt)
	tx2Hash := tx2.Hash()
	fmt.Printf("Approve tx, txHash: %x\n", tx2Hash[:])
	require.Equal(tradingSuite.T(), nil, apprErr)
	time.Sleep(15 * time.Second)
	auth.GasPrice = big.NewInt(100000000000)
	// auth.GasLimit = 1000000
	fmt.Println("Starting deposit erc20 to vault contract")
	tx, err := c.DepositERC20(auth, tokenAddr, amt, incPaymentAddrStr)
	require.Equal(tradingSuite.T(), nil, err)
	fmt.Println("Finished deposit erc20 to vault contract")
	txHash := tx.Hash()

	if err := wait(tradingSuite.ETHClient, txHash); err != nil {
		require.Equal(tradingSuite.T(), nil, err)
	}
	fmt.Printf("deposited erc20 token to bridge, txHash: %x\n", txHash[:])
	require.Equal(tradingSuite.T(), tradingSuite.getStatusTxhash(txHash), uint64(1), "tx on ether network failed")
	return txHash
}

func (tradingSuite *TnTradingTestSuite) callIssuingETHReq(
	incTokenIDStr string,
	ethDepositProof []string,
	ethBlockHash string,
	ethTxIdx uint,
) (map[string]interface{}, error) {
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
	var res TnIssuingETHRes
	err := rpcClient.RPCCall(
		"",
		tradingSuite.IncRPCHost,
		"",
		"createandsendtxwithissuingethreq",
		params,
		&res,
	)
	if err != nil {
		return nil, err
	}

	response, _ := json.Marshal(res)
	fmt.Println("get response", string(response))

	if res.RPCError != nil {
		return nil, errors.New(res.RPCError.Message)
	}
	return res.Result.(map[string]interface{}), nil
}

func (tradingSuite *TnTradingTestSuite) callBurningPToken(
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
			tradingSuite.IncBurningAddrStr: amount.Uint64(),
			// tradingSuite.IncPaymentAddrStr: 5,
		},
		"RemoteAddress": remoteAddrStr,
		"Privacy":       true,
		"TokenFee":      0,
	}
	params := []interface{}{
		tradingSuite.IncPrivKeyStr,
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

func (tradingSuite *TnTradingTestSuite) submitBurnProofForDepositToSC(
	burningTxIDStr string,
) common.Hash {
	proof, err := getAndDecodeBurnProofV2(tradingSuite.IncBridgeHost, burningTxIDStr, "getburnprooffordeposittosc")
	require.Equal(tradingSuite.T(), nil, err)

	// Get contract instance
	c, err := vault.NewVault(tradingSuite.VaultAddr, tradingSuite.ETHClient)
	require.Equal(tradingSuite.T(), nil, err)

	// Burn
	auth := bind.NewKeyedTransactor(tradingSuite.ETHPrivKey)
	// auth.GasPrice = big.NewInt(1000000)
	// auth.GasLimit = 2000000
	auth.GasPrice = big.NewInt(100000000000)
	tx, err := SubmitBurnProof(c, auth, proof)
	require.Equal(tradingSuite.T(), nil, err)

	txHash := tx.Hash()
	if err := wait(tradingSuite.ETHClient, txHash); err != nil {
		require.Equal(tradingSuite.T(), nil, err)
	}
	fmt.Printf("burned, txHash: %x\n", txHash[:])
	require.Equal(tradingSuite.T(), tradingSuite.getStatusTxhash(txHash), uint64(1), "tx on ether network failed")
	return txHash
}

func (tradingSuite *TnTradingTestSuite) submitBurnProofForWithdrawal(
	burningTxIDStr string,
) common.Hash {
	proof, err := getAndDecodeBurnProofV2(tradingSuite.IncBridgeHost, burningTxIDStr, "getburnproof")
	require.Equal(tradingSuite.T(), nil, err)

	// Get contract instance
	c, err := vault.NewVault(tradingSuite.VaultAddr, tradingSuite.ETHClient)
	require.Equal(tradingSuite.T(), nil, err)

	// Burn
	auth := bind.NewKeyedTransactor(tradingSuite.ETHPrivKey)
	// auth.GasPrice = big.NewInt(1000000)
	// auth.GasLimit = 2000000
	auth.GasPrice = big.NewInt(120000000000)
	// auth.Nonce = big.NewInt(13)
	tx, err := Withdraw(c, auth, proof)
	require.Equal(tradingSuite.T(), nil, err)

	txHash := tx.Hash()
	if err := wait(tradingSuite.ETHClient, txHash); err != nil {
		require.Equal(tradingSuite.T(), nil, err)
	}
	fmt.Printf("burned, txHash: %x\n", txHash[:])
	require.Equal(tradingSuite.T(), tradingSuite.getStatusTxhash(txHash), uint64(1), "tx on ether network failed")
	return txHash
}

func (tradingSuite *TnTradingTestSuite) genKeysPairForSC() {
	incPriKeyBytes, _, err := base58.Base58Check{}.Decode(tradingSuite.IncPrivKeyStr)
	require.Equal(tradingSuite.T(), nil, err)

	tradingSuite.GeneratedPrivKeyForSC, tradingSuite.GeneratedPubKeyForSC = bridgesig.KeyGen(incPriKeyBytes)
}

func (tradingSuite *TnTradingTestSuite) getDepositedBalance(
	ethTokenAddrStr string,
	ownerAddrStr string,
) *big.Int {
	c, err := vault.NewVault(tradingSuite.VaultAddr, tradingSuite.ETHClient)
	require.Equal(tradingSuite.T(), nil, err)
	token := common.HexToAddress(ethTokenAddrStr)
	owner := common.HexToAddress(ownerAddrStr)
	bal, err := c.GetDepositedBalance(nil, token, owner)
	require.Equal(tradingSuite.T(), nil, err)
	//fmt.Printf("deposited balance on SC: %d\n", bal)
	return bal
}

func (tradingSuite *TnTradingTestSuite) requestWithdraw(
	withdrawalETHTokenIDStr string,
	amount *big.Int,
) common.Hash {
	c, err := vault.NewVault(tradingSuite.VaultAddr, tradingSuite.ETHClient)
	require.Equal(tradingSuite.T(), nil, err)
	auth := bind.NewKeyedTransactor(tradingSuite.ETHPrivKey)

	token := common.HexToAddress(withdrawalETHTokenIDStr)
	// amount := big.NewInt(0.1 * params.Ether)
	timestamp := []byte(randomizeTimestamp())
	tempData := append([]byte(tradingSuite.IncPaymentAddrStr), token[:]...)
	tempData1 := append(tempData, timestamp...)
	tempData2 := append(tempData1, common.LeftPadBytes(amount.Bytes(), 32)...)
	data := rawsha3(tempData2)
	signBytes, _ := crypto.Sign(data, &tradingSuite.GeneratedPrivKeyForSC)
	auth.GasPrice = big.NewInt(100000000000)
	// auth.Nonce = big.NewInt(3)
	//auth.GasLimit = 10000000
	// auth.GasLimit = 2000000

	tx, err := c.RequestWithdraw(auth, tradingSuite.IncPaymentAddrStr, token, amount, signBytes, timestamp)
	require.Equal(tradingSuite.T(), nil, err)

	txHash := tx.Hash()
	if err := wait(tradingSuite.ETHClient, txHash); err != nil {
		require.Equal(tradingSuite.T(), nil, err)
	}
	fmt.Printf("request withdrawal, txHash: %x\n", txHash[:])
	require.Equal(tradingSuite.T(), tradingSuite.getStatusTxhash(txHash), uint64(1), "tx on ether network failed")
	return txHash
}

func (tradingSuite *TnTradingTestSuite) getBalanceTokenIncAccount(
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

func (tradingSuite *TnTradingTestSuite) getBalancePrvIncAccount(
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

func (tradingSuite *TnTradingTestSuite) getFeePRVbyTxhashInC(
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

func (tradingSuite *TnTradingTestSuite) getGasFeeETHbyTxhash(txHash common.Hash) *big.Int {
	reciept, _ := getETHTransactionReceipt(tradingSuite.ETHHost, txHash)
	//fmt.Println("reciept gas fee : ", reciept.GasUsed)
	gasPrice := big.NewInt(50000000000)
	gasFee := big.NewInt(0).Div(big.NewInt(0).Mul(big.NewInt(int64(reciept.GasUsed)), gasPrice), big.NewInt(int64(1)))
	return gasFee

}

func (tradingSuite *TnTradingTestSuite) getStatusTxhash(txHash common.Hash) uint64 {
	tx, err := getETHTransactionReceipt(tradingSuite.ETHHost, txHash)
	require.Equal(tradingSuite.T(), nil, err)
	// fmt.Println(tx.Status) // 1 succcess 0 failed
	return tx.Status
}

func (tradingSuite *TnTradingTestSuite) getExpectedAmount(
	srcToken string,
	destToken string,
	srcQty *big.Int,
) *big.Int {
	if srcToken == tradingSuite.EtherAddressStr {
		srcToken = tradingSuite.WETHAddressStr
	}
	if destToken == tradingSuite.EtherAddressStr {
		destToken = tradingSuite.WETHAddressStr
	}
	c, err := uniswap.NewUniswapV2Trade(tradingSuite.UniswapTradeDeployedAddr, tradingSuite.ETHClient)
	require.Equal(tradingSuite.T(), nil, err)
	amounts, err := c.GetAmountsOut(nil, common.HexToAddress(srcToken), srcQty, common.HexToAddress(destToken))
	require.Equal(tradingSuite.T(), nil, err)
	require.Equal(tradingSuite.T(), 2, len(amounts))
	fmt.Printf("intput value: %d\n", amounts[0])
	fmt.Printf("output value: %d\n", amounts[1])
	return amounts[1]
}

func (tradingSuite *TnTradingTestSuite) executeWithUniswap(
	srcQty *big.Int,
	srcTokenIDStr string,
	destTokenIDStr string,
) {
	tradeAbi, _ := abi.JSON(strings.NewReader(uniswap.UniswapV2TradeABI))

	// Get contract instance
	c, err := vault.NewVault(tradingSuite.VaultAddr, tradingSuite.ETHClient)
	require.Equal(tradingSuite.T(), nil, err)
	auth := bind.NewKeyedTransactor(tradingSuite.ETHPrivKey)
	auth.GasPrice = big.NewInt(100000000000)
	// auth.GasLimit = 2000000
	srcToken := common.HexToAddress(srcTokenIDStr)
	destToken := common.HexToAddress(destTokenIDStr)
	expectOutputAmount := tradingSuite.getExpectedAmount(srcTokenIDStr, destTokenIDStr, srcQty)
	outputA := big.NewInt(0).Div((big.NewInt(0).Mul(expectOutputAmount, big.NewInt(80))), big.NewInt(100))
	input, _ := tradeAbi.Pack("trade", srcToken, srcQty, destToken, outputA)
	timestamp := []byte(randomizeTimestamp())
	tempData := append(tradingSuite.UniswapTradeDeployedAddr[:], input...)
	tempData1 := append(tempData, timestamp...)
	tempData2 := append(tempData1, common.LeftPadBytes(srcQty.Bytes(), 32)...)
	data := rawsha3(tempData2)
	signBytes, _ := crypto.Sign(data, &tradingSuite.GeneratedPrivKeyForSC)

	tx, err := c.Execute(
		auth,
		srcToken,
		srcQty,
		destToken,
		tradingSuite.UniswapTradeDeployedAddr,
		input,
		timestamp,
		signBytes,
	)
	require.Equal(tradingSuite.T(), nil, err)
	txHash := tx.Hash()
	if err := wait(tradingSuite.ETHClient, txHash); err != nil {
		require.Equal(tradingSuite.T(), nil, err)
	}
	fmt.Printf("Uniswap trade executed , txHash: %x\n", txHash[:])

	require.Equal(tradingSuite.T(), tradingSuite.getStatusTxhash(txHash), uint64(1), "tx on ether network failed")
}

func (tradingSuite *TnTradingTestSuite) getExpectedRate(
	srcToken string,
	destToken string,
	srcQty *big.Int,
) *big.Int {
	if srcToken == tradingSuite.EtherAddressStr {
		srcToken = tradingSuite.EtherAddressStrKyber
	}
	if destToken == tradingSuite.EtherAddressStr {
		destToken = tradingSuite.EtherAddressStrKyber
	}
	c, err := kbntrade.NewKBNTrade(tradingSuite.KyberTradeDeployedAddr, tradingSuite.ETHClient)
	require.Equal(tradingSuite.T(), nil, err)
	expectRate, slippageRate, err := c.GetConversionRates(nil, common.HexToAddress(srcToken), srcQty, common.HexToAddress(destToken))
	require.Equal(tradingSuite.T(), nil, err)
	fmt.Printf("slippageRate value: %d\n", slippageRate)
	fmt.Printf("expectRate value: %d\n", expectRate)
	return expectRate
}

func (tradingSuite *TnTradingTestSuite) executeWithKyber(
	srcQty *big.Int,
	srcTokenIDStr string,
	destTokenIDStr string,
) {
	tradeAbi, _ := abi.JSON(strings.NewReader(kbntrade.KBNTradeABI))

	// Get contract instance
	c, err := vault.NewVault(tradingSuite.VaultAddr, tradingSuite.ETHClient)
	require.Equal(tradingSuite.T(), nil, err)
	auth := bind.NewKeyedTransactor(tradingSuite.ETHPrivKey)
	auth.GasPrice = big.NewInt(50000000000)
	// auth.GasLimit = 2000000
	srcToken := common.HexToAddress(srcTokenIDStr)
	destToken := common.HexToAddress(destTokenIDStr)
	//auth.GasPrice = big.NewInt(50000000000)
	// auth.GasPrice = big.NewInt(9800000000)
	// auth.GasLimit = 2000000
	// auth.Nonce = big.NewInt(21)
	expectRate := tradingSuite.getExpectedRate(srcTokenIDStr, destTokenIDStr, srcQty)
	input, _ := tradeAbi.Pack("trade", srcToken, srcQty, destToken, expectRate)
	timestamp := []byte(randomizeTimestamp())
	tempData := append(tradingSuite.KyberTradeDeployedAddr[:], input...)
	tempData1 := append(tempData, timestamp...)
	tempData2 := append(tempData1, common.LeftPadBytes(srcQty.Bytes(), 32)...)
	data := rawsha3(tempData2)
	signBytes, _ := crypto.Sign(data, &tradingSuite.GeneratedPrivKeyForSC)

	tx, err := c.Execute(
		auth,
		srcToken,
		srcQty,
		destToken,
		tradingSuite.KyberTradeDeployedAddr,
		input,
		timestamp,
		signBytes,
	)
	require.Equal(tradingSuite.T(), nil, err)
	txHash := tx.Hash()
	if err := wait(tradingSuite.ETHClient, txHash); err != nil {
		require.Equal(tradingSuite.T(), nil, err)
	}
	fmt.Printf("Kyber trade executed , txHash: %x\n", txHash[:])

	require.Equal(tradingSuite.T(), tradingSuite.getStatusTxhash(txHash), uint64(1), "tx on ether network failed")
}

func (tradingSuite *TnTradingTestSuite) Test1DepositAndWithdrwaEther() {
//return
	fmt.Println("============ TEST 1 DEPOSIT AND WITHDRAW ETHER ===========")
	fmt.Println("------------ STEP 0: declaration & initialization --------------")
	tradeAmount := big.NewInt(int64(tradingSuite.DepositingEther * params.Ether))
	burningPETH := big.NewInt(0).Div(tradeAmount, big.NewInt(1000000000))

	pubKeyToAddrStr := crypto.PubkeyToAddress(tradingSuite.GeneratedPubKeyForSC).Hex()
	fmt.Println("GeneratedPubKeyForSC", pubKeyToAddrStr)

	// get info balance initialization
	balPrvInit, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance initialization : ", balPrvInit)

	balpEthInit, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncEtherTokenIDStr)
	fmt.Println("[INFO] pETH balance initialization : ", balpEthInit)

	balEthInit := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.EtherAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] ETH balance initialization : ", balEthInit)

	balEthScInit := tradingSuite.getDepositedBalance(
		tradingSuite.EtherAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] ETH balance initialization on SC : ", balEthScInit)

	fmt.Println("------------ STEP 1: porting ETH to pETH --------------")

	fmt.Println("amount ETH deposit : ", (big.NewInt(int64(tradingSuite.DepositingEther * params.Ether))))

	// Deposit to proof
	txHash := tradingSuite.depositETH(
		tradingSuite.DepositingEther,
		tradingSuite.IncPaymentAddrStr,
	)

	fmt.Println("gas Fee transaction :", tradingSuite.getGasFeeETHbyTxhash(txHash))
	// get ETH remain after depsit
	balEthAfDep := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.EtherAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] ETH balance remain after deposit : ", balEthAfDep)

	//	require.Equal(tradingSuite.T(), balEthAfDep, big.NewInt(0).Sub(big.NewInt(0).Sub(balEthInit, big.NewInt(int64(tradingSuite.DepositingEther*params.Ether))), tradingSuite.getGasFeeETHbyTxhash(txHash)), "balance ETH incorrect")

	// Proof
	_, ethBlockHash, ethTxIdx, ethDepositProof, err := getETHDepositProof(tradingSuite.ETHHost, txHash)
	require.Equal(tradingSuite.T(), nil, err)
	fmt.Println("depositProof ---- : ", ethBlockHash, ethTxIdx, ethDepositProof)

	fmt.Println("Waiting 90s for 15 blocks confirmation")
	time.Sleep(confirmWaitTn * time.Second)
	_, err = tradingSuite.callIssuingETHReq(
		tradingSuite.IncEtherTokenIDStr,
		ethDepositProof,
		ethBlockHash,
		ethTxIdx,
	)
	require.Equal(tradingSuite.T(), nil, err)

	time.Sleep(incWaitTn * time.Second)
	// check PRV and token balance after issuing
	balPrvAfIssS1, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance after issuing step 1: ", balPrvAfIssS1)
	//require.NotEqual(tradingSuite.T(), balPrvAfIssS1, (balPrvInit - tradingSuite.getFeePRVbyTxhashInC(issuuRes["TxID"].(string))), "Balance PRV remain incorrect after issuu step 1")

	balpEthAfIssS1, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncEtherTokenIDStr)
	fmt.Println("[INFO] pETH balance after issuing step 1 : ", balpEthAfIssS1)
	//require.Equal(tradingSuite.T(), big.NewInt(int64(balpEthAfIssS1-balpEthInit)), big.NewInt(0).Div(big.NewInt(int64(tradingSuite.DepositingEther*params.Ether)), big.NewInt(1000000000)), " balnce pToken issuu incorrect")

	fmt.Println("------------ STEP 2: burning pETH to deposit ETH to SC --------------")
	// make a burn tx to incognito chain as a result of deposit to SC
	burningRes, err := tradingSuite.callBurningPToken(
		tradingSuite.IncEtherTokenIDStr,
		burningPETH,
		pubKeyToAddrStr[2:],
		"createandsendburningfordeposittoscrequest",
	)
	require.Equal(tradingSuite.T(), nil, err)
	burningTxID, found := burningRes["TxID"]
	require.Equal(tradingSuite.T(), true, found)
	time.Sleep(incWaitTn * time.Second)

	// check PRV and token balance after burning
	balPrvAfBurnS2, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance after burning step 2: ", balPrvAfBurnS2)
	//require.NotEqual(tradingSuite.T(), balPrvAfBurnS2, (balPrvAfIssS1 - tradingSuite.getFeePRVbyTxhashInC(burningRes["TxID"].(string))), "Balance PRV remain incorrect after burn step 2")

	balpEthAfBurnS2, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncEtherTokenIDStr)
	fmt.Println("[INFO] pETH balance after burning step 2 : ", balpEthAfBurnS2)
	// TODO assert pETH balance issuing

	txHash2 := tradingSuite.submitBurnProofForDepositToSC(burningTxID.(string))
	time.Sleep(ethWaitTn * time.Second)

	fmt.Println("gas Fee transaction :", tradingSuite.getGasFeeETHbyTxhash(txHash2))
	// get ETH remain
	balEthAfDep2 := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.EtherAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] ETH balance remain  : ", balEthAfDep2)
	// TODO : assert ETH balance
	//require.Equal(tradingSuite.T(), balEthAfDep2, big.NewInt(0).Sub(balEthAfDep, tradingSuite.getGasFeeETHbyTxhash(txHash2)), "balance ETH incorrect")

	balEthScDepS2 := tradingSuite.getDepositedBalance(
		tradingSuite.EtherAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] ETH balance after deposit on SC at step 2: ", balEthScDepS2)
	// // TODO assert ETH balane on SC

	fmt.Println("------------ STEP 3: withdraw ETH to deposit pETH to Incognito  --------------")

	txHashByEmittingWithdrawalReq1 := tradingSuite.requestWithdraw(
		tradingSuite.EtherAddressStr,
		balEthScDepS2,
	)
	time.Sleep(ethWaitTn * time.Second)
	balDaiScDepS41 := tradingSuite.getDepositedBalance(
		tradingSuite.EtherAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] ETH balance on SC after withdraw at step 3 : ", balDaiScDepS41)
	// TODO assert DAI balane on SC

	_, ethBlockHash, ethTxIdx, ethDepositProof, err = getETHDepositProof(tradingSuite.ETHHost, txHashByEmittingWithdrawalReq1)
	require.Equal(tradingSuite.T(), nil, err)
	fmt.Println("depositProof by emitting withdarawal req: ", ethBlockHash, ethTxIdx, ethDepositProof)

	fmt.Println("Waiting 90s for 15 blocks confirmation")
	time.Sleep(confirmWaitTn * time.Second)

	_, err = tradingSuite.callIssuingETHReq(
		tradingSuite.IncEtherTokenIDStr,
		ethDepositProof,
		ethBlockHash,
		ethTxIdx,
	)
	require.Equal(tradingSuite.T(), nil, err)
	time.Sleep(incWaitTn * time.Second)

	balpDaiAfIssS41, _ := tradingSuite.getBalanceTokenIncAccount(
		tradingSuite.IncPrivKeyStr,
		tradingSuite.IncEtherTokenIDStr,
	)
	fmt.Println("[INFO] pETH balance after issuing step 3 : ", balpDaiAfIssS41)

	fmt.Println("------------ STEP 4: withdraw pETH to deposit ETH   --------------")

	withdrawingPETH := big.NewInt(0).Div(balEthScDepS2, big.NewInt(1000000000))

	burningRes, err = tradingSuite.callBurningPToken(
		tradingSuite.IncEtherTokenIDStr,
		withdrawingPETH,
		tradingSuite.ETHOwnerAddrStr,
		"createandsendburningrequest",
	)
	require.Equal(tradingSuite.T(), nil, err)
	burningTxID, found = burningRes["TxID"]
	require.Equal(tradingSuite.T(), true, found)
	time.Sleep(incWaitTn * time.Second)

	balpEthAfBurnS51, _ := tradingSuite.getBalanceTokenIncAccount(
		tradingSuite.IncPrivKeyStr,
		tradingSuite.IncEtherTokenIDStr,
	)
	fmt.Println("[INFO] pETH balance after burning step 4 : ", balpEthAfBurnS51)

	tradingSuite.submitBurnProofForWithdrawal(burningTxID.(string))

	time.Sleep(ethWaitTn * time.Second)
	balEthAfDep51 := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.EtherAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] ETH balance after withdraw  : ", balEthAfDep51)

}

func (tradingSuite *TnTradingTestSuite) Test2TradeEthForUSDC() {
return
	fmt.Println("============ TEST 2 TRADE ETHER FOR USDC WITH Uniswap AGGREGATOR ===========")
	fmt.Println("------------ STEP 0: declaration & initialization --------------")
	tradeAmount := big.NewInt(int64(tradingSuite.DepositingEther * params.Ether))
	burningPETH := big.NewInt(0).Div(tradeAmount, big.NewInt(1000000000))

	pubKeyToAddrStr := crypto.PubkeyToAddress(tradingSuite.GeneratedPubKeyForSC).Hex()

	// get info balance initialization
	balPrvInit, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance initialization : ", balPrvInit)

	balpEthInit, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncEtherTokenIDStr)
	fmt.Println("[INFO] pETH balance initialization : ", balpEthInit)

	balpUSDCInit, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncUSDCTokenIDStr)
	fmt.Println("[INFO] pUSDC balance initialization : ", balpUSDCInit)

	balEthInit := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.EtherAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] ETH balance initialization : ", balEthInit)

	balUSDCInit := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.USDCAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] USDC balance initialization : ", balUSDCInit)

	balEthScInit := tradingSuite.getDepositedBalance(
		tradingSuite.EtherAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] ETH balance initialization on SC : ", balEthScInit)

	balUSDCScInit := tradingSuite.getDepositedBalance(
		tradingSuite.USDCAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] USDC balance initialization on SC : ", balUSDCScInit)

	fmt.Println("------------ STEP 1: porting ETH to pETH --------------")
	txHash := tradingSuite.depositETH(
		tradingSuite.DepositingEther,
		tradingSuite.IncPaymentAddrStr,
	)
	time.Sleep(ethWaitTn * time.Second)
	_, ethBlockHash, ethTxIdx, ethDepositProof, err := getETHDepositProof(tradingSuite.ETHHost, txHash)
	require.Equal(tradingSuite.T(), nil, err)
	fmt.Println("depositProof ---- : ", ethBlockHash, ethTxIdx, ethDepositProof)

	// get ETH remain after depsit
	balEthAfDep := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.EtherAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] ETH balance remain after deposit : ", balEthAfDep)
	// TODO : assert ETH balance

	fmt.Println("Waiting 90s for 15 blocks confirmation")
	time.Sleep(confirmWaitTn * time.Second)
	_, err = tradingSuite.callIssuingETHReq(
		tradingSuite.IncEtherTokenIDStr,
		ethDepositProof,
		ethBlockHash,
		ethTxIdx,
	)
	require.Equal(tradingSuite.T(), nil, err)
	time.Sleep(incWaitTn * time.Second)
	// check PRV and token balance after issuing
	balPrvAfIssS1, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance after issuing step 1: ", balPrvAfIssS1)
	// TODO assert PRV balance remain
	balpEthAfIssS1, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncEtherTokenIDStr)
	fmt.Println("[INFO] pETH balance after issuing step 1 : ", balpEthAfIssS1)
	// TODO assert pETH balance issuing

	fmt.Println("------------ STEP 2: burning pETH to deposit ETH to SC --------------")
	// make a burn tx to incognito chain as a result of deposit to SC
	burningRes, err := tradingSuite.callBurningPToken(
		tradingSuite.IncEtherTokenIDStr,
		burningPETH,
		pubKeyToAddrStr[2:],
		"createandsendburningfordeposittoscrequest",
	)
	require.Equal(tradingSuite.T(), nil, err)
	burningTxID, found := burningRes["TxID"]
	require.Equal(tradingSuite.T(), true, found)
	time.Sleep(incWaitTn * time.Second)

	// check PRV and token balance after burning
	balPrvAfBurnS2, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance after burning step 2: ", balPrvAfBurnS2)
	// TODO assert PRV balance remain
	balpEthAfBurnS2, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncEtherTokenIDStr)
	fmt.Println("[INFO] pETH balance after burning step 2 : ", balpEthAfBurnS2)
	// TODO assert pETH balance issuing

	tradingSuite.submitBurnProofForDepositToSC(burningTxID.(string))

	time.Sleep(ethWaitTn * time.Second)
	balEthScDepS2 := tradingSuite.getDepositedBalance(
		tradingSuite.EtherAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] ETH balance after deposit on SC at step 2: ", balEthScDepS2)
	// TODO assert ETH balane on SC
	balUSDCScS2 := tradingSuite.getDepositedBalance(
		tradingSuite.USDCAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] USDC balance on SC at step 2 : ", balUSDCScS2)

	//require.Equal(tradingSuite.T(), big.NewInt(0).Mul(burningPETH, big.NewInt(1000000000)), deposited)
	fmt.Println("------------ step 3: execute trade ETH for USDC through uniswap aggregator --------------")
	tradingSuite.executeWithUniswap(
		tradeAmount,
		tradingSuite.EtherAddressStr,
		tradingSuite.USDCAddressStr,
	)
	time.Sleep(ethWaitTn * time.Second)
	balEthScTradeS3 := tradingSuite.getDepositedBalance(
		tradingSuite.EtherAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] ETH balance on SC after trade at step 3 : ", balEthScTradeS3)
	// TODO assert ETH balane on SC
	balUSDCScTradeS3 := tradingSuite.getDepositedBalance(
		tradingSuite.USDCAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] USDC balance on SC after trade at step 3 : ", balUSDCScTradeS3)
	// TODO assert USDC balane on SC

	fmt.Println("------------ STEP 4: withdraw USDC to deposit pUSDC to Incognito  --------------")

	txHashByEmittingWithdrawalReq1 := tradingSuite.requestWithdraw(
		tradingSuite.USDCAddressStr,
		balUSDCScTradeS3,
	)
	time.Sleep(ethWaitTn * time.Second)
	// txHashByEmittingWithdrawalReq1 := common.HexToHash("0xb299bf0c890cb8606b5f187014b63750bc94b12062fd3976e8c7f84fee58621a")
	balUSDCScDepS41 := tradingSuite.getDepositedBalance(
		tradingSuite.USDCAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] USDC balance on SC after withdraw at step 3 : ", balUSDCScDepS41)
	// TODO assert USDC balane on SC

	_, ethBlockHash, ethTxIdx, ethDepositProof, err = getETHDepositProof(tradingSuite.ETHHost, txHashByEmittingWithdrawalReq1)
	require.Equal(tradingSuite.T(), nil, err)
	fmt.Println("depositProof by emitting withdarawal req: ", ethBlockHash, ethTxIdx, ethDepositProof)

	fmt.Println("Waiting 90s for 15 blocks confirmation")
	time.Sleep(confirmWaitTn * time.Second)

	_, err = tradingSuite.callIssuingETHReq(
		tradingSuite.IncUSDCTokenIDStr,
		ethDepositProof,
		ethBlockHash,
		ethTxIdx,
	)
	require.Equal(tradingSuite.T(), nil, err)
	time.Sleep(incWaitTn * time.Second)

	balpUSDCAfIssS41, _ := tradingSuite.getBalanceTokenIncAccount(
		tradingSuite.IncPrivKeyStr,
		tradingSuite.IncUSDCTokenIDStr,
	)
	fmt.Println("[INFO] pUSDC balance after issuing step 3 : ", balpUSDCAfIssS41)

	fmt.Println("------------ STEP 5: withdraw pUSDC to deposit USDC   --------------")

	withdrawingPUSDC := balUSDCScTradeS3
	// withdrawingPUSDC := big.NewInt(int64(350770))
	burningRes, err = tradingSuite.callBurningPToken(
		tradingSuite.IncUSDCTokenIDStr,
		withdrawingPUSDC,
		tradingSuite.ETHOwnerAddrStr,
		"createandsendburningrequest",
	)
	require.Equal(tradingSuite.T(), nil, err)
	burningTxID, found = burningRes["TxID"]
	require.Equal(tradingSuite.T(), true, found)
	time.Sleep(incWaitTn * time.Second)

	balpUSDCAfBurnS51, _ := tradingSuite.getBalanceTokenIncAccount(
		tradingSuite.IncPrivKeyStr,
		tradingSuite.IncUSDCTokenIDStr,
	)
	fmt.Println("[INFO] pUSDC balance after burning step 4 : ", balpUSDCAfBurnS51)

	tradingSuite.submitBurnProofForWithdrawal(burningTxID.(string))

	time.Sleep(ethWaitTn * time.Second)
	balUSDCAfDep51 := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.USDCAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] USDC balance after withdraw  : ", balUSDCAfDep51)

}

func (tradingSuite *TnTradingTestSuite) Test3DepositAndWithdrwatokenUSDC() {
//return
	fmt.Println("============ TEST 3 DEPOSIT AND WITHDRAW ERC20 TOKEN (USDC) ===========")
	fmt.Println("------------ STEP 0: declaration & initialization --------------")

	pubKeyToAddrStr := crypto.PubkeyToAddress(tradingSuite.GeneratedPubKeyForSC).Hex()

	// get info balance initialization
	balPrvInit, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance initialization : ", balPrvInit)

	balEthInit := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.EtherAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] ETH balance initialization : ", balEthInit)

	balpUSDCInit, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncUSDCTokenIDStr)
	fmt.Println("[INFO] pUSDC balance initialization : ", balpUSDCInit)

	balUSDCInit := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.USDCAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] USDC balance initialization : ", balUSDCInit)

	balEthScInit := tradingSuite.getDepositedBalance(
		tradingSuite.USDCAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] USDC balance initialization on SC : ", balEthScInit)

	fmt.Println("------------ STEP 1: porting USDC to pUSDC --------------")

	fmt.Println("amount USDC deposit input : ", (big.NewInt(int64(1000))))
	deposit := big.NewInt(int64(1000))
	burningPETH := deposit
	// Deposit to proof
	txHash := tradingSuite.depositERC20ToBridge(
		deposit,
		common.HexToAddress(tradingSuite.USDCAddressStr),
		tradingSuite.IncPaymentAddrStr,
	)

	balUSDCAfDep := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.USDCAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] USDC balance remain after deposit : ", balUSDCAfDep)

	fmt.Println("gas Fee transaction :", tradingSuite.getGasFeeETHbyTxhash(txHash))
	// get ETH remain after depsit
	balEthAfDep := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.EtherAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] ETH balance remain after deposit : ", balEthAfDep)

	//require.Equal(tradingSuite.T(), balEthAfDep, big.NewInt(0).Sub(big.NewInt(0).Sub(balEthInit, big.NewInt(int64(tradingSuite.DepositingEther*params.Ether))), tradingSuite.getGasFeeETHbyTxhash(txHash)), "balance ETH incorrect")

	// Proof
	_, ethBlockHash, ethTxIdx, ethDepositProof, err := getETHDepositProof(tradingSuite.ETHHost, txHash)
	require.Equal(tradingSuite.T(), nil, err)
	fmt.Println("depositProof ---- : ", ethBlockHash, ethTxIdx, ethDepositProof)

	fmt.Println("Waiting 90s for 15 blocks confirmation")
	time.Sleep(confirmWaitTn * time.Second)

	_, err = tradingSuite.callIssuingETHReq(
		tradingSuite.IncUSDCTokenIDStr,
		ethDepositProof,
		ethBlockHash,
		ethTxIdx,
	)
	require.Equal(tradingSuite.T(), nil, err)

	time.Sleep(incWaitTn * time.Second)

	balpUSDCAfIssS1, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncUSDCTokenIDStr)
	fmt.Println("[INFO] pUSDC balance after issuing step 1 : ", balpUSDCAfIssS1)
	// check PRV and token balance after issuing
	balPrvAfIssS1, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance after issuing step 1: ", balPrvAfIssS1)

	fmt.Println("------------ STEP 2: burning pUSDC to deposit USDC to SC --------------")
	// make a burn tx to incognito chain as a result of deposit to SC
	burningRes, err := tradingSuite.callBurningPToken(
		tradingSuite.IncUSDCTokenIDStr,
		burningPETH,
		pubKeyToAddrStr[2:],
		"createandsendburningfordeposittoscrequest",
	)
	require.Equal(tradingSuite.T(), nil, err)
	burningTxID, found := burningRes["TxID"]
	require.Equal(tradingSuite.T(), true, found)
	time.Sleep(incWaitTn * time.Second)

	// check PRV and token balance after burning
	balPrvAfBurnS2, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance after burning step 2: ", balPrvAfBurnS2)

	balpUSDCAfBurnS2, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncUSDCTokenIDStr)
	fmt.Println("[INFO] pUSDC balance after burning step 2 : ", balpUSDCAfBurnS2)
	// TODO assert pETH balance issuing

	txHash2 := tradingSuite.submitBurnProofForDepositToSC(burningTxID.(string))
	time.Sleep(ethWaitTn * time.Second)
	fmt.Println("gas Fee transaction :", tradingSuite.getGasFeeETHbyTxhash(txHash2))
	// get ETH remain
	balEthAfDep2 := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.EtherAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] ETH balance remain  : ", balEthAfDep2)
	// TODO : assert ETH balance
	//require.Equal(tradingSuite.T(), balEthAfDep2, big.NewInt(0).Sub(balEthAfDep, tradingSuite.getGasFeeETHbyTxhash(txHash2)), "balance ETH incorrect")

	balUSDCScDepS2 := tradingSuite.getDepositedBalance(
		tradingSuite.USDCAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] USDC balance after deposit on SC at step 2: ", balUSDCScDepS2)
	// TODO assert ETH balane on SC

	fmt.Println("------------ STEP 3: withdraw USDC to deposit pUSDC to Incognito  --------------")

	txHashByEmittingWithdrawalReq1 := tradingSuite.requestWithdraw(
		tradingSuite.USDCAddressStr,
		balUSDCScDepS2,
	)
	time.Sleep(ethWaitTn * time.Second)
	balUSDCScDepS41 := tradingSuite.getDepositedBalance(
		tradingSuite.USDCAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] USDC balance on SC after withdraw at step 3 : ", balUSDCScDepS41)
	// TODO assert USDC balane on SC

	_, ethBlockHash, ethTxIdx, ethDepositProof, err = getETHDepositProof(tradingSuite.ETHHost, txHashByEmittingWithdrawalReq1)
	require.Equal(tradingSuite.T(), nil, err)
	fmt.Println("depositProof by emitting withdarawal req: ", ethBlockHash, ethTxIdx, ethDepositProof)

	fmt.Println("Waiting 90s for 15 blocks confirmation")
	time.Sleep(confirmWaitTn * time.Second)

	_, err = tradingSuite.callIssuingETHReq(
		tradingSuite.IncUSDCTokenIDStr,
		ethDepositProof,
		ethBlockHash,
		ethTxIdx,
	)
	require.Equal(tradingSuite.T(), nil, err)
	time.Sleep(incWaitTn * time.Second)

	balpUSDCAfIssS41, _ := tradingSuite.getBalanceTokenIncAccount(
		tradingSuite.IncPrivKeyStr,
		tradingSuite.IncUSDCTokenIDStr,
	)
	fmt.Println("[INFO] pUSDC balance after issuing step 3 : ", balpUSDCAfIssS41)

	fmt.Println("------------ STEP 4: withdraw pUSDC to deposit USDC   --------------")

	withdrawingPUSDC := big.NewInt(int64(balpUSDCAfIssS1))

	burningRes, err = tradingSuite.callBurningPToken(
		tradingSuite.IncUSDCTokenIDStr,
		withdrawingPUSDC,
		tradingSuite.ETHOwnerAddrStr,
		"createandsendburningrequest",
	)
	require.Equal(tradingSuite.T(), nil, err)
	burningTxID, found = burningRes["TxID"]
	require.Equal(tradingSuite.T(), true, found)
	time.Sleep(incWaitTn * time.Second)

	balpUSDCAfBurnS51, _ := tradingSuite.getBalanceTokenIncAccount(
		tradingSuite.IncPrivKeyStr,
		tradingSuite.IncUSDCTokenIDStr,
	)
	fmt.Println("[INFO] pUSDC balance after burning step 4 : ", balpUSDCAfBurnS51)

	tradingSuite.submitBurnProofForWithdrawal(burningTxID.(string))
	time.Sleep(ethWaitTn * time.Second)
	balUSDCAfDep51 := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.USDCAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] USDC balance after withdraw  : ", balUSDCAfDep51)

}

func (tradingSuite *TnTradingTestSuite) Test4TradeEthForKNCWithKyber() {
 return
	fmt.Println("============ TEST 4 TRADE ETHER FOR KNC WITH Kyber AGGREGATOR ===========")
	fmt.Println("------------ STEP 0: declaration & initialization --------------")
	tradeAmount := big.NewInt(int64(tradingSuite.DepositingEther * params.Ether))
	burningPETH := big.NewInt(0).Div(tradeAmount, big.NewInt(1000000000))

	pubKeyToAddrStr := crypto.PubkeyToAddress(tradingSuite.GeneratedPubKeyForSC).Hex()

	// get info balance initialization
	balPrvInit, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance initialization : ", balPrvInit)

	balpEthInit, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncEtherTokenIDStr)
	fmt.Println("[INFO] pETH balance initialization : ", balpEthInit)

	balpKNCInit, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncKNCTokenIDStr)
	fmt.Println("[INFO] pKNC balance initialization : ", balpKNCInit)

	balEthInit := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.EtherAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] ETH balance initialization : ", balEthInit)

	balKNCInit := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.KNCAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] KNC balance initialization : ", balKNCInit)

	balEthScInit := tradingSuite.getDepositedBalance(
		tradingSuite.EtherAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] ETH balance initialization on SC : ", balEthScInit)

	balKNCScInit := tradingSuite.getDepositedBalance(
		tradingSuite.KNCAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] KNC balance initialization on SC : ", balKNCScInit)

	fmt.Println("------------ STEP 1: porting ETH to pETH --------------")
	txHash := tradingSuite.depositETH(
		tradingSuite.DepositingEther,
		tradingSuite.IncPaymentAddrStr,
	)
	time.Sleep(ethWaitTn * time.Second)

	_, ethBlockHash, ethTxIdx, ethDepositProof, err := getETHDepositProof(tradingSuite.ETHHost, txHash)
	require.Equal(tradingSuite.T(), nil, err)
	fmt.Println("depositProof ---- : ", ethBlockHash, ethTxIdx, ethDepositProof)

	// get ETH remain after depsit
	balEthAfDep := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.EtherAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] ETH balance remain after deposit : ", balEthAfDep)
	// TODO : assert ETH balance

	fmt.Println("Waiting 90s for 15 blocks confirmation")
	time.Sleep(confirmWaitTn * time.Second)
	_, err = tradingSuite.callIssuingETHReq(
		tradingSuite.IncEtherTokenIDStr,
		ethDepositProof,
		ethBlockHash,
		ethTxIdx,
	)
	require.Equal(tradingSuite.T(), nil, err)
	time.Sleep(incWaitTn * time.Second)
	// check PRV and token balance after issuing
	balPrvAfIssS1, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance after issuing step 1: ", balPrvAfIssS1)
	// TODO assert PRV balance remain
	balpEthAfIssS1, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncEtherTokenIDStr)
	fmt.Println("[INFO] pETH balance after issuing step 1 : ", balpEthAfIssS1)
	// TODO assert pETH balance issuing

	fmt.Println("------------ STEP 2: burning pETH to deposit ETH to SC --------------")
	// make a burn tx to incognito chain as a result of deposit to SC
	burningRes, err := tradingSuite.callBurningPToken(
		tradingSuite.IncEtherTokenIDStr,
		burningPETH,
		pubKeyToAddrStr[2:],
		"createandsendburningfordeposittoscrequest",
	)
	require.Equal(tradingSuite.T(), nil, err)
	burningTxID, found := burningRes["TxID"]
	require.Equal(tradingSuite.T(), true, found)
	time.Sleep(incWaitTn * time.Second)

	// check PRV and token balance after burning
	balPrvAfBurnS2, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance after burning step 2: ", balPrvAfBurnS2)
	// TODO assert PRV balance remain
	balpEthAfBurnS2, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncEtherTokenIDStr)
	fmt.Println("[INFO] pETH balance after burning step 2 : ", balpEthAfBurnS2)
	// TODO assert pETH balance issuing

	tradingSuite.submitBurnProofForDepositToSC(burningTxID.(string))
	balEthScDepS2 := tradingSuite.getDepositedBalance(
		tradingSuite.EtherAddressStr,
		pubKeyToAddrStr,
	)
	time.Sleep(ethWaitTn * time.Second)
	fmt.Println("[INFO] ETH balance after deposit on SC at step 2: ", balEthScDepS2)
	// TODO assert ETH balane on SC
	balKNCScS2 := tradingSuite.getDepositedBalance(
		tradingSuite.KNCAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] KNC balance on SC at step 2 : ", balKNCScS2)

	//require.Equal(tradingSuite.T(), big.NewInt(0).Mul(burningPETH, big.NewInt(1000000000)), deposited)
	fmt.Println("------------ step 3: execute trade ETH for KNC through Kyber aggregator --------------")
	tradingSuite.executeWithKyber(
		tradeAmount,
		tradingSuite.EtherAddressStr,
		tradingSuite.KNCAddressStr,
	)
	time.Sleep(ethWaitTn * time.Second)

	balEthScTradeS3 := tradingSuite.getDepositedBalance(
		tradingSuite.EtherAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] ETH balance on SC after trade at step 3 : ", balEthScTradeS3)
	// TODO assert ETH balane on SC
	balKNCScTradeS3 := tradingSuite.getDepositedBalance(
		tradingSuite.KNCAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] KNC balance on SC after trade at step 3 : ", balKNCScTradeS3)
	// TODO assert KNC balane on SC
	require.NotEqual(tradingSuite.T(), balKNCScTradeS3, balKNCScS2, "trade failed")

	fmt.Println("------------ step 4: withdrawing KNC from SC to pKNC on Incognito --------------")
	txHashByEmittingWithdrawalReq := tradingSuite.requestWithdraw(
		tradingSuite.KNCAddressStr,
		balKNCScTradeS3,
	)
	time.Sleep(ethWaitTn * time.Second)

	balKNCScDepS4 := tradingSuite.getDepositedBalance(
		tradingSuite.KNCAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] KNC balance on SC after withdraw at step 4 : ", balKNCScDepS4)
	// TODO assert KNC balane on SC
	_, ethBlockHash, ethTxIdx, ethDepositProof, err = getETHDepositProof(tradingSuite.ETHHost, txHashByEmittingWithdrawalReq)
	require.Equal(tradingSuite.T(), nil, err)
	fmt.Println("depositProof by emitting withdarawal req: ", ethBlockHash, ethTxIdx, ethDepositProof)

	fmt.Println("Waiting 90s for 15 blocks confirmation")
	time.Sleep(confirmWaitTn * time.Second)
	_, err = tradingSuite.callIssuingETHReq(
		tradingSuite.IncKNCTokenIDStr,
		ethDepositProof,
		ethBlockHash,
		ethTxIdx,
	)
	require.Equal(tradingSuite.T(), nil, err)
	time.Sleep(incWaitTn * time.Second)

	balpEthAfIssS4, _ := tradingSuite.getBalanceTokenIncAccount(
		tradingSuite.IncPrivKeyStr,
		tradingSuite.IncKNCTokenIDStr,
	)
	fmt.Println("[INFO] pKNC balance after issuing step 4 : ", balpEthAfIssS4)

	balPrvAfIssS4, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance after issuing step 4: ", balPrvAfIssS4)
	// TODO assert PRV balance remain

	fmt.Println("------------ step 5: withdrawing pKNC from Incognito to KNC --------------")
	withdrawingPKNC := big.NewInt(0).Div(balKNCScTradeS3, big.NewInt(1000000000))
	burningRes, err = tradingSuite.callBurningPToken(
		tradingSuite.IncKNCTokenIDStr,
		withdrawingPKNC,
		tradingSuite.ETHOwnerAddrStr,
		"createandsendburningrequest",
	)

	require.Equal(tradingSuite.T(), nil, err)
	burningTxID, found = burningRes["TxID"]
	require.Equal(tradingSuite.T(), true, found)
	time.Sleep(incWaitTn * time.Second)

	tradingSuite.submitBurnProofForWithdrawal(burningTxID.(string))
	time.Sleep(ethWaitTn * time.Second)

	balKNC := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.KNCAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("KNC balance after trade: ", balKNC)

	// require.Equal(tradingSuite.T(), withdrawingPKNC.Uint64(), bal.Div(bal, big.NewInt(1000000000)).Uint64())

	balEth := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.EtherAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("ETH balance after trade: ", balEth)
}


