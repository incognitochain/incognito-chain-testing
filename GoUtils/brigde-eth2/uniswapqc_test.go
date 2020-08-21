package main

import (
	"fmt"
	"math/big"
	"strings"
	"testing"
	"time"

	"github.com/incognitochain/bridge-eth/bridge/uniswap"

	"github.com/incognitochain/bridge-eth/bridge/vault"
	"github.com/stretchr/testify/suite"

	"github.com/ethereum/go-ethereum/accounts/abi"
	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/params"

	"github.com/stretchr/testify/require"
)



// Define the suite, and absorb the built-in basic suite
// functionality from testify - including assertion methods.
type UniTradingTestSuite struct {
	*TradingTestSuite

	UniswapTradeDeployedAddr common.Address
	UniswapRouteContractAddr common.Address

	WETHAddr             common.Address
	EtherAddressStrKyber string

	IncKBNTokenIDStr  string
	IncSALTTokenIDStr string
	IncOMGTokenIDStr  string
	IncSNTTokenIDStr  string
	IncPOLYTokenIDStr string
	IncZILTokenIDStr  string
	IncMRKTokenIDStr 	string
	IncUSDCTokenIDStr 	string
	IncWBTCTokenIDStr 	string


	USDCAddressStr  string
	WBTCAddressStr  string
	KBNAddressStr  string
	SALTAddressStr string
	OMGAddressStr  string
	SNTAddressStr  string
	POLYAddressStr string
	ZILAddressStr  string
	WETHAddressStr	string

	MRKAddressStr string

	IncPrivKeyStrKb     string
	IncPaymentAddrStrKb string

	// token amounts for tests
	DepositingEther             float64
	OMGBalanceAfterStep1        *big.Int
	POLYBalanceAfterStep2       *big.Int
	KyberMultiTradeDeployedAddr common.Address
}

func NewUniTradingTestSuite(tradingTestSuite *TradingTestSuite) *UniTradingTestSuite {
	return &UniTradingTestSuite{
		TradingTestSuite: tradingTestSuite,
	}
}

// Make sure that VariableThatShouldStartAtFive is set to five
// before each test
func (tradingSuite *UniTradingTestSuite) SetupSuite() {
	fmt.Println("Setting up the suite...")
	// Kovan env
	tradingSuite.IncPrivKeyStrKb = "112t8ro4yu78UE82jpto12rp3Cd8Z2Mse7fcavSyXXP82oApE1cg9y8hWq69Z74fFHGJrQyHz54vU8Mv1kx5qZ54cRQJPkF5Cb7DhNqL5Tgt"
	tradingSuite.IncPaymentAddrStrKb = "12RyGbTyktYkXe7mNwmZeD4rktqxtHMe3Tsyf4XiZdKVGFssEHaF1ZUTpXZmpFACuDotVr7a6FEw8v6FTn8DEMqpHNxZ8fJW3KNN3i1"

	tradingSuite.WETHAddressStr = "0xd0a1e359811322d97991e03f863a0c30c2cf029c" 
	tradingSuite.EtherAddressStrKyber = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
	tradingSuite.IncPOLYTokenIDStr = "d0379b8ccc25e4940d5b94ace07dcfa3656a20814279ddf2674f6d7180f65440"
	tradingSuite.IncOMGTokenIDStr = "27322fa7fce2c4d4d5a0022d595a0eec56d7735751a3ba8bc7f10b358ab938bc"
	tradingSuite.IncZILTokenIDStr = "3c115c066028bb682af410c594546b58026095ff149dc30c061749ee163d9051"
	tradingSuite.IncKBNTokenIDStr = "d6644f62d0ef0475335ae7bb6103f358979cbfcd2b85481e3bde2b82101a095c"



	tradingSuite.IncSALTTokenIDStr = "06ce44eae35daf57b9b8158ab95c0cddda9bac208fc380236a318ef40f3ac2ef"
	tradingSuite.IncSNTTokenIDStr = "414a6459526e827321cedb6e574d2ba2eb267c5735b0a65991602a405fb753b7"

	tradingSuite.IncUSDCTokenIDStr = "61e1efbf6be9decc46fdf8250cdae5be12bee501b65f774a58af4513b645f6a3"
	tradingSuite.IncWBTCTokenIDStr = "4fb87c00dbe3933ae73c4dc37a37db0bca9aa9f55a2776dbd59cca2b02e72fc4"
	tradingSuite.IncMRKTokenIDStr = "641e37731c151e8b93ed48f6044836edac1e21d518b11c491774ba10b89ca5e5"

	tradingSuite.USDCAddressStr = "0x75b0622cec14130172eae9cf166b92e5c112faff"
	tradingSuite.WBTCAddressStr = "0xA0A5aD2296b38Bd3e3Eb59AAEAF1589E8d9a29A9"
	tradingSuite.MRKAddressStr = "0xef13C0c8abcaf5767160018d268f9697aE4f5375"

	tradingSuite.ZILAddressStr = "0xAb74653cac23301066ABa8eba62b9Abd8a8c51d6"
	tradingSuite.POLYAddressStr = "0xd92266fd053161115163a7311067F0A4745070b5"
	tradingSuite.OMGAddressStr = "0xdB7ec4E4784118D9733710e46F7C83fE7889596a"
	tradingSuite.KBNAddressStr = "0xad67cB4d63C9da94AcA37fDF2761AaDF780ff4a2" 
	

	tradingSuite.SALTAddressStr = "0x6fEE5727EE4CdCBD91f3A873ef2966dF31713A04"
	tradingSuite.SNTAddressStr = "0x4c99B04682fbF9020Fcb31677F8D8d66832d3322"

	// tradingSuite.UniswapTradeDeployedAddr = common.HexToAddress("0xfAAa26e153dE1d800F8d67FdE3C4391A435c1fEe")      //testnet 1
	tradingSuite.UniswapTradeDeployedAddr = common.HexToAddress("0xb5Ad297cAA230562003C3d789D8006e741AcBEE4")      //testnet 2
	
	
	tradingSuite.DepositingEther = float64(0.001)
	tradingSuite.UniswapRouteContractAddr = common.HexToAddress("0xf164fC0Ec4E93095b804a4795bBe1e041497b92a") // kovan
}

func (tradingSuite *UniTradingTestSuite) TearDownSuite() {
	fmt.Println("Tearing down the suite...")
	tradingSuite.ETHClient.Close()
}

func (tradingSuite *UniTradingTestSuite) SetupTest() {
	fmt.Println("Setting up the test...")
}

func (tradingSuite *UniTradingTestSuite) TearDownTest() {
	fmt.Println("Tearing down the test...")
}
func (tradingSuite *UniTradingTestSuite) getExpectedAmount(
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
	c, err := uniswap.NewUniswap(tradingSuite.UniswapTradeDeployedAddr, tradingSuite.ETHClient)
	require.Equal(tradingSuite.T(), nil, err)
	amounts, err := c.GetAmountsOut(nil, common.HexToAddress(srcToken), srcQty, common.HexToAddress(destToken))
	require.Equal(tradingSuite.T(), nil, err)
	require.Equal(tradingSuite.T(), 2, len(amounts))
	fmt.Printf("intput value: %d\n", amounts[0])
	fmt.Printf("output value: %d\n", amounts[1])
	return amounts[1]
}

// In order for 'go test' to run this suite, we need to create
// a normal test function and pass our suite to suite.Run
func TestUniTradingTestSuite(t *testing.T) {
	fmt.Println("Starting entry point for Kyber test suite...")

	tradingSuite := new(TradingTestSuite)
	suite.Run(t, tradingSuite)

	kyberTradingSuite := NewUniTradingTestSuite(tradingSuite)
	suite.Run(t, kyberTradingSuite)

	fmt.Println("Finishing entry point for 0x test suite...")
}


func (tradingSuite *UniTradingTestSuite) executeWithUniswap(
	srcQty *big.Int,
	srcTokenIDStr string,
	destTokenIDStr string,
) {
	tradeAbi, _ := abi.JSON(strings.NewReader(uniswap.UniswapABI))

	// Get contract instance
	c, err := vault.NewVault(tradingSuite.VaultAddr, tradingSuite.ETHClient)
	require.Equal(tradingSuite.T(), nil, err)
	auth := bind.NewKeyedTransactor(tradingSuite.ETHPrivKey)
	auth.GasPrice = big.NewInt(50000000000)
	// auth.GasLimit = 2000000
	srcToken := common.HexToAddress(srcTokenIDStr)
	destToken := common.HexToAddress(destTokenIDStr)
	expectOutputAmount := tradingSuite.getExpectedAmount(srcTokenIDStr, destTokenIDStr, srcQty)
	input, _ := tradeAbi.Pack("trade", srcToken, srcQty, destToken, expectOutputAmount)
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
}


func (tradingSuite *UniTradingTestSuite) Test1TradeEthForDAI() {
return
	fmt.Println("============ TEST 1 TRADE ETHER FOR DAI - MKR WITH Uniswap AGGREGATOR ===========")
	fmt.Println("------------ STEP 0: declaration & initialization --------------")
	tradeAmount := big.NewInt(int64(tradingSuite.DepositingEther * params.Ether))
	burningPETH := big.NewInt(0).Div(tradeAmount, big.NewInt(1000000000))

	pubKeyToAddrStr := crypto.PubkeyToAddress(tradingSuite.GeneratedPubKeyForSC).Hex()

	// get info balance initialization
	balPrvInit, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance initialization : ", balPrvInit)

	balpEthInit, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncEtherTokenIDStr)
	fmt.Println("[INFO] pETH balance initialization : ", balpEthInit)

	balpKNCInit, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncMRKTokenIDStr)
	fmt.Println("[INFO] pMRK balance initialization : ", balpKNCInit)

	balEthInit := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.EtherAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] ETH balance initialization : ", balEthInit)

	balZILInit := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.MRKAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] MRK balance initialization : ", balZILInit)

	balEthScInit := tradingSuite.getDepositedBalance(
		tradingSuite.EtherAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] ETH balance initialization on SC : ", balEthScInit)

	balZILScInit := tradingSuite.getDepositedBalance(
		tradingSuite.MRKAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] MRK balance initialization on SC : ", balZILScInit)

	balDaiInit := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.DAIAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] DAI balance initialization : ", balDaiInit)

	balpDaiInit, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncDAITokenIDStr)
	fmt.Println("[INFO] pDAI balance initialization : ", balpDaiInit)

	balDaiScInit := tradingSuite.getDepositedBalance(
		tradingSuite.DAIAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] DAI balance initialization on SC : ", balDaiScInit)

	fmt.Println("------------ STEP 1: porting ETH to pETH --------------")
	txHash := tradingSuite.depositETH(
		tradingSuite.DepositingEther,
		tradingSuite.IncPaymentAddrStr,
	)
	time.Sleep(15 * time.Second)
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
	time.Sleep(80 * time.Second)
	_, err = tradingSuite.callIssuingETHReq(
		tradingSuite.IncEtherTokenIDStr,
		ethDepositProof,
		ethBlockHash,
		ethTxIdx,
	)
	require.Equal(tradingSuite.T(), nil, err)
	time.Sleep(120 * time.Second)
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
	time.Sleep(120 * time.Second)

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
	fmt.Println("[INFO] ETH balance after deposit on SC at step 2: ", balEthScDepS2)
	// TODO assert ETH balane on SC
	balDAIScS2 := tradingSuite.getDepositedBalance(
		tradingSuite.DAIAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] DAI balance on SC at step 2 : ", balDAIScS2)

	//require.Equal(tradingSuite.T(), big.NewInt(0).Mul(burningPETH, big.NewInt(1000000000)), deposited)
	fmt.Println("------------ step 3: execute trade ETH for KNC through Uniswap aggregator --------------")
	tradingSuite.executeWithUniswap(
		tradeAmount,
		tradingSuite.EtherAddressStr,
		tradingSuite.DAIAddressStr,
	)
	balEthScTradeS3 := tradingSuite.getDepositedBalance(
		tradingSuite.EtherAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] ETH balance on SC after trade at step 3 : ", balEthScTradeS3)
	// TODO assert ETH balane on SC

	balDAIScTradeS3 := tradingSuite.getDepositedBalance(
		tradingSuite.DAIAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] DAI balance on SC after trade at step 3 : ", balDAIScTradeS3)

	balZILScTradeS3 := tradingSuite.getDepositedBalance(
		tradingSuite.MRKAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] MRK balance on SC after trade at step 3 : ", balZILScTradeS3)
	
	// require.NotEqual(tradingSuite.T(), balKNCScTradeS3, balKNCScS2, "trade failed")

	fmt.Println("------------ step 3.1: execute trade DAI for MRK through Uniswap aggregator --------------")
	
	tradingSuite.executeWithUniswap(
		balDAIScTradeS3,
		tradingSuite.DAIAddressStr,
		tradingSuite.MRKAddressStr,
	)

	balEthScTradeS31 := tradingSuite.getDepositedBalance(
		tradingSuite.EtherAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] ETH balance on SC after trade at step 31 : ", balEthScTradeS31)
	// TODO assert ETH balane on SC

	balDAIScTradeS31 := tradingSuite.getDepositedBalance(
		tradingSuite.DAIAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] DAI balance on SC after trade at step 31 : ", balDAIScTradeS31)

	balZILScTradeS31 := tradingSuite.getDepositedBalance(
		tradingSuite.MRKAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] MRK balance on SC after trade at step 31 : ", balZILScTradeS31)


	fmt.Println("------------ STEP 3.2: execute trade MRK for ETH through UNISWAP aggregator --------------")

	tradingSuite.executeWithUniswap(
		balZILScTradeS31,
		tradingSuite.MRKAddressStr,
		tradingSuite.EtherAddressStr,
	)

	balEthScTradeS32 := tradingSuite.getDepositedBalance(
		tradingSuite.EtherAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] ETH balance on SC after trade at step 32 : ", balEthScTradeS32)
	// TODO assert ETH balane on SC

	balDAIScTradeS32 := tradingSuite.getDepositedBalance(
		tradingSuite.DAIAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] DAI balance on SC after trade at step 32 : ", balDAIScTradeS32)

	balZILScTradeS32 := tradingSuite.getDepositedBalance(
		tradingSuite.MRKAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] MRK balance on SC after trade at step 32 : ", balZILScTradeS32)

	//require.NotEqual(tradingSuite.T(), balKNCScTradeS33, balKNCScTradeS3, "trade failed")


	fmt.Println("------------ step 4: withdrawing ETH from SC to pETH on Incognito --------------")
	txHashByEmittingWithdrawalReq := tradingSuite.requestWithdraw(
		tradingSuite.EtherAddressStr,
		balEthScTradeS32,
	)
	fmt.Println("gas Fee transaction :", tradingSuite.getGasFeeETHbyTxhash(txHashByEmittingWithdrawalReq))
	// get ETH remain
	balEthAfDep4 := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.EtherAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] ETH balance remain  : ", balEthAfDep4)
	//require.Equal(tradingSuite.T(), balEthAfDep4, big.NewInt(0).Sub(balEthScTradeS32, tradingSuite.getGasFeeETHbyTxhash(txHashByEmittingWithdrawalReq)), "balance ETH incorrect")

	balEthScDepS4 := tradingSuite.getDepositedBalance(
		tradingSuite.EtherAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] ETH balance on SC after withdraw at step 4 : ", balEthScDepS4)
	// TODO assert ETH balane on SC

	_, ethBlockHash, ethTxIdx, ethDepositProof, err = getETHDepositProof(tradingSuite.ETHHost, txHashByEmittingWithdrawalReq)
	require.Equal(tradingSuite.T(), nil, err)
	fmt.Println("depositProof by emitting withdarawal req: ", ethBlockHash, ethTxIdx, ethDepositProof)

	fmt.Println("Waiting 90s for 15 blocks confirmation")
	time.Sleep(120 * time.Second)

	_, err = tradingSuite.callIssuingETHReq(
		tradingSuite.IncEtherTokenIDStr,
		ethDepositProof,
		ethBlockHash,
		ethTxIdx,
	)
	require.Equal(tradingSuite.T(), nil, err)
	time.Sleep(140 * time.Second)

	balpEthAfIssS4, _ := tradingSuite.getBalanceTokenIncAccount(
		tradingSuite.IncPrivKeyStr,
		tradingSuite.IncEtherTokenIDStr,
	)
	fmt.Println("[INFO] pETH balance after issuing step 4 : ", balpEthAfIssS4)
	// TODO assert pETH balance issuing
	balPrvAfIssS4, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance after issuing step 4: ", balPrvAfIssS4)
	// TODO assert PRV balance remain

	fmt.Println("------------ step 5: withdrawing pETH from Incognito to ETH --------------")
	withdrawingPETH := big.NewInt(0).Div(balEthScTradeS32, big.NewInt(1000000000))
	burningRes, err = tradingSuite.callBurningPToken(
		tradingSuite.IncEtherTokenIDStr,
		withdrawingPETH,
		tradingSuite.ETHOwnerAddrStr,
		"createandsendburningrequest",
	)
	require.Equal(tradingSuite.T(), nil, err)
	burningTxID, found = burningRes["TxID"]
	require.Equal(tradingSuite.T(), true, found)
	time.Sleep(120 * time.Second)

	balpEthAfBurnS5, _ := tradingSuite.getBalanceTokenIncAccount(
		tradingSuite.IncPrivKeyStr,
		tradingSuite.IncEtherTokenIDStr,
	)
	fmt.Println("[INFO] pETH balance after burning step 5 : ", balpEthAfBurnS5)
	// TODO assert pETH balance issuing
	balPrvAfBrunS5, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance after burning step 5: ", balPrvAfBrunS5)
	// TODO assert PRV balance remain

	txHash5 := tradingSuite.submitBurnProofForWithdrawal(burningTxID.(string))
	fmt.Println("gas Fee transaction :", tradingSuite.getGasFeeETHbyTxhash(txHash5))
	// get ETH remain
	balEthAfDep5 := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.EtherAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] ETH balance remain  : ", balEthAfDep5)
	// require.Equal(tradingSuite.T(), balEthAfDep5, big.NewInt(0).Sub(balEthAfDep4, tradingSuite.getGasFeeETHbyTxhash(txHash5)), "balance ETH incorrect")

	balETH := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.EtherAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("ETH balance after trade : ", balETH)
	// require.Equal(tradingSuite.T(), withdrawingPETH.Uint64(), bal.Div(bal, big.NewInt(1000000000)).Uint64())



}

func (tradingSuite *UniTradingTestSuite) Test2TradeEthForUSDC() {
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
		time.Sleep(15 * time.Second)
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
		time.Sleep(80 * time.Second)
		_, err = tradingSuite.callIssuingETHReq(
			tradingSuite.IncEtherTokenIDStr,
			ethDepositProof,
			ethBlockHash,
			ethTxIdx,
		)
		require.Equal(tradingSuite.T(), nil, err)
		time.Sleep(120 * time.Second)
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
		time.Sleep(120 * time.Second)
	
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
		time.Sleep(100 * time.Second)
	
		_, err = tradingSuite.callIssuingETHReq(
			tradingSuite.IncUSDCTokenIDStr,
			ethDepositProof,
			ethBlockHash,
			ethTxIdx,
		)
		require.Equal(tradingSuite.T(), nil, err)
		time.Sleep(100 * time.Second)
	
		balpUSDCAfIssS41, _ := tradingSuite.getBalanceTokenIncAccount(
			tradingSuite.IncPrivKeyStr,
			tradingSuite.IncUSDCTokenIDStr,
		)
		fmt.Println("[INFO] pUSDC balance after issuing step 3 : ", balpUSDCAfIssS41)
	
		fmt.Println("------------ STEP 5: withdraw pUSDC to deposit USDC   --------------")
	
		withdrawingPUSDC := balUSDCScTradeS3
	
		burningRes, err = tradingSuite.callBurningPToken(
			tradingSuite.IncUSDCTokenIDStr,
			withdrawingPUSDC,
			tradingSuite.ETHOwnerAddrStr,
			"createandsendburningrequest",
		)
		require.Equal(tradingSuite.T(), nil, err)
		burningTxID, found = burningRes["TxID"]
		require.Equal(tradingSuite.T(), true, found)
		time.Sleep(120 * time.Second)
	
		balpUSDCAfBurnS51, _ := tradingSuite.getBalanceTokenIncAccount(
			tradingSuite.IncPrivKeyStr,
			tradingSuite.IncUSDCTokenIDStr,
		)
		fmt.Println("[INFO] pUSDC balance after burning step 4 : ", balpUSDCAfBurnS51)
	
		tradingSuite.submitBurnProofForWithdrawal(burningTxID.(string))
	
		balUSDCAfDep51 := tradingSuite.getBalanceOnETHNet(
			common.HexToAddress(tradingSuite.USDCAddressStr),
			common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
		)
		fmt.Println("[INFO] USDC balance after withdraw  : ", balUSDCAfDep51)
	
	}

func (tradingSuite *UniTradingTestSuite) Test3TradeEthForUSDCandWBTC() {
return
	fmt.Println("============ TEST 3 TRADE ETHER FOR USDC - WBTC   WITH Uniswap AGGREGATOR ===========")
	fmt.Println("------------ STEP 0: declaration & initialization --------------")

	pubKeyToAddrStr := crypto.PubkeyToAddress(tradingSuite.GeneratedPubKeyForSC).Hex()

	tradeAmount := big.NewInt(int64(tradingSuite.DepositingEther * params.Ether))
	burningPETH := big.NewInt(0).Div(tradeAmount, big.NewInt(1000000000))
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


	balpWBTCInit, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncWBTCTokenIDStr)
	fmt.Println("[INFO] pWBTC balance initialization : ", balpWBTCInit)

	balWBTCInit := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.WBTCAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] WBTC balance initialization : ", balWBTCInit)


	balWBTCScInit := tradingSuite.getDepositedBalance(
		tradingSuite.WBTCAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] WBTC balance initialization on SC : ", balWBTCScInit)


	fmt.Println("------------ STEP 1: porting ETH to pETH --------------")
	txHash := tradingSuite.depositETH(
		tradingSuite.DepositingEther,
		tradingSuite.IncPaymentAddrStr,
	)
	time.Sleep(15 * time.Second)
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
	time.Sleep(80 * time.Second)
	_, err = tradingSuite.callIssuingETHReq(
		tradingSuite.IncEtherTokenIDStr,
		ethDepositProof,
		ethBlockHash,
		ethTxIdx,
	)
	require.Equal(tradingSuite.T(), nil, err)
	time.Sleep(120 * time.Second)
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
	time.Sleep(120 * time.Second)

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

	balWBTCScTradeS3 := tradingSuite.getDepositedBalance(
		tradingSuite.WBTCAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] WBTC balance on SC after trade at step 3 : ", balWBTCScTradeS3)


	fmt.Println("------------ step 3.1: execute trade USDC for WBTC through uniswap aggregator --------------")
	tradingSuite.executeWithUniswap(
		balUSDCScTradeS3,
		tradingSuite.USDCAddressStr,
		tradingSuite.WBTCAddressStr,
	)
	balEthScTradeS31 := tradingSuite.getDepositedBalance(
		tradingSuite.EtherAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] ETH balance on SC after trade at step 3.1 : ", balEthScTradeS31)
	// TODO assert ETH balane on SC
	balUSDCScTradeS31 := tradingSuite.getDepositedBalance(
		tradingSuite.USDCAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] USDC balance on SC after trade at step 3.1 : ", balUSDCScTradeS31)
	// TODO assert USDC balane on SC

	balWBTCScTradeS31 := tradingSuite.getDepositedBalance(
		tradingSuite.WBTCAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] WBTC balance on SC after trade at step 3.1 : ", balWBTCScTradeS31)



	fmt.Println("------------ step 4: withdrawing WBTC from SC to pWBTC on Incognito --------------")
	txHashByEmittingWithdrawalReq := tradingSuite.requestWithdraw(
		tradingSuite.WBTCAddressStr,
		balWBTCScTradeS31,
	)
	time.Sleep(15 * time.Second)

	balWBTCScDepS4 := tradingSuite.getDepositedBalance(
		tradingSuite.WBTCAddressStr,
		pubKeyToAddrStr,
	)
	fmt.Println("[INFO] WBTC balance on SC after withdraw at step 4 : ", balWBTCScDepS4)
	// TODO assert WBTC balane on SC
	_, ethBlockHash, ethTxIdx, ethDepositProof, err = getETHDepositProof(tradingSuite.ETHHost, txHashByEmittingWithdrawalReq)
	require.Equal(tradingSuite.T(), nil, err)
	fmt.Println("depositProof by emitting withdarawal req: ", ethBlockHash, ethTxIdx, ethDepositProof)

	fmt.Println("Waiting 90s for 15 blocks confirmation")
	time.Sleep(80 * time.Second)
	_, err = tradingSuite.callIssuingETHReq(
		tradingSuite.IncWBTCTokenIDStr,
		ethDepositProof,
		ethBlockHash,
		ethTxIdx,
	)
	require.Equal(tradingSuite.T(), nil, err)
	time.Sleep(120 * time.Second)

	balpWBTCAfIssS4, _ := tradingSuite.getBalanceTokenIncAccount(
		tradingSuite.IncPrivKeyStr,
		tradingSuite.IncWBTCTokenIDStr,
	)
	fmt.Println("[INFO] pWBTC balance after issuing step 4 : ", balpWBTCAfIssS4)

	balPrvAfIssS4, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance after issuing step 4: ", balPrvAfIssS4)
	// TODO assert PRV balance remain

	fmt.Println("------------ step 5: withdrawing pWBTC from Incognito to WBTC --------------")
	withdrawingPWBTC := big.NewInt(int64(balpWBTCAfIssS4))
	burningRes, err = tradingSuite.callBurningPToken(
		tradingSuite.IncWBTCTokenIDStr,
		withdrawingPWBTC,
		tradingSuite.ETHOwnerAddrStr,
		"createandsendburningrequest",
	)
	require.Equal(tradingSuite.T(), nil, err)
	burningTxID, found = burningRes["TxID"]
	require.Equal(tradingSuite.T(), true, found)
	time.Sleep(120 * time.Second)

	tradingSuite.submitBurnProofForWithdrawal(burningTxID.(string))

	balWBTC := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.WBTCAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	// tradingSuite.USDCBalanceAfterStep1 = balWBTC
	fmt.Println("WBTC balance after trade: ", balWBTC)
	// require.Equal(tradingSuite.T(), withdrawingPUSDC.Uint64(), bal.Div(bal, big.NewInt(1000000000)).Uint64())
	balEth := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.EtherAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("ETH balance after trade: ", balEth)


}

func (tradingSuite *UniTradingTestSuite) Test4DepositAndWithdrwaERC20tokenUSDC() {
return
	fmt.Println("============ TEST 8 DEPOSIT AND WITHDRAW ERC20 TOKEN (USDC) ===========")
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
	time.Sleep(100 * time.Second)
	_, err = tradingSuite.callIssuingETHReq(
		tradingSuite.IncUSDCTokenIDStr,
		ethDepositProof,
		ethBlockHash,
		ethTxIdx,
	)
	require.Equal(tradingSuite.T(), nil, err)

	time.Sleep(120 * time.Second)

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
	time.Sleep(120 * time.Second)

	// check PRV and token balance after burning
	balPrvAfBurnS2, _ := tradingSuite.getBalancePrvIncAccount(tradingSuite.IncPrivKeyStr)
	fmt.Println("[INFO] PRV balance after burning step 2: ", balPrvAfBurnS2)

	balpUSDCAfBurnS2, _ := tradingSuite.getBalanceTokenIncAccount(tradingSuite.IncPrivKeyStr, tradingSuite.IncUSDCTokenIDStr)
	fmt.Println("[INFO] pUSDC balance after burning step 2 : ", balpUSDCAfBurnS2)
	// TODO assert pETH balance issuing

	txHash2 := tradingSuite.submitBurnProofForDepositToSC(burningTxID.(string))

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
	time.Sleep(100 * time.Second)

	_, err = tradingSuite.callIssuingETHReq(
		tradingSuite.IncUSDCTokenIDStr,
		ethDepositProof,
		ethBlockHash,
		ethTxIdx,
	)
	require.Equal(tradingSuite.T(), nil, err)
	time.Sleep(100 * time.Second)

	balpUSDCAfIssS41, _ := tradingSuite.getBalanceTokenIncAccount(
		tradingSuite.IncPrivKeyStr,
		tradingSuite.IncUSDCTokenIDStr,
	)
	fmt.Println("[INFO] pUSDC balance after issuing step 3 : ", balpUSDCAfIssS41)

	fmt.Println("------------ STEP 4: withdraw pUSDC to deposit USDC   --------------")

	withdrawingPUSDC := big.NewInt(int64(balpUSDCAfIssS41))

	burningRes, err = tradingSuite.callBurningPToken(
		tradingSuite.IncUSDCTokenIDStr,
		withdrawingPUSDC,
		tradingSuite.ETHOwnerAddrStr,
		"createandsendburningrequest",
	)
	require.Equal(tradingSuite.T(), nil, err)
	burningTxID, found = burningRes["TxID"]
	require.Equal(tradingSuite.T(), true, found)
	time.Sleep(120 * time.Second)

	balpUSDCAfBurnS51, _ := tradingSuite.getBalanceTokenIncAccount(
		tradingSuite.IncPrivKeyStr,
		tradingSuite.IncUSDCTokenIDStr,
	)
	fmt.Println("[INFO] pUSDC balance after burning step 4 : ", balpUSDCAfBurnS51)

	tradingSuite.submitBurnProofForWithdrawal(burningTxID.(string))

	balUSDCAfDep51 := tradingSuite.getBalanceOnETHNet(
		common.HexToAddress(tradingSuite.USDCAddressStr),
		common.HexToAddress(fmt.Sprintf("0x%s", tradingSuite.ETHOwnerAddrStr)),
	)
	fmt.Println("[INFO] USDC balance after withdraw  : ", balUSDCAfDep51)

}
