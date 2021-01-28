package main

import (
	"encoding/json"
	"fmt"
	"github.com/ethereum/go-ethereum/accounts/abi"
	"math/big"
	"strings"
	"testing"

	"github.com/pkg/errors"

	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/incognitochain/bridge-eth/common/base58"
	"github.com/incognitochain/portal3-eth/portal/delegator"
	"github.com/incognitochain/portal3-eth/portal/incognitoproxy"
	"github.com/incognitochain/portal3-eth/portal/portalv3"
	"github.com/stretchr/testify/require"
	"github.com/stretchr/testify/suite"
)

var BRI_CONSENSUS = "dsa"

type CommitteePublicKey struct {
	IncPubKey    []byte
	MiningPubKey map[string][]byte
}

func (pubKey *CommitteePublicKey) FromString(keyString string) error {
	keyBytes, ver, err := base58.Base58Check{}.Decode(keyString)
	if (ver != 0) || (err != nil) {
		return errors.New("Wrong input")
	}
	return json.Unmarshal(keyBytes, pubKey)
}

// // Define the suite, and absorb the built-in basic suite
// // functionality from testify - including assertion methods.
type TradingDeployTestSuite struct {
	*PortalV3BaseTestSuite
}

func NewTradingDeployTestSuite(tradingTestSuite *PortalV3BaseTestSuite) *TradingDeployTestSuite {
	return &TradingDeployTestSuite{
		PortalV3BaseTestSuite: tradingTestSuite,
	}
}

func (tradingDeploySuite *TradingDeployTestSuite) SetupSuite() {
	fmt.Println("Setting up the suite...")
}

func (tradingDeploySuite *TradingDeployTestSuite) TearDownSuite() {
	fmt.Println("Tearing down the suite...")
	tradingDeploySuite.ETHClient.Close()
}

func TestPortalV3DeployTestSuite(t *testing.T) {
	fmt.Println("Starting entry point...")
	tradingSuite := new(PortalV3BaseTestSuite)
	suite.Run(t, tradingSuite)

	tradingDeploySuite := NewTradingDeployTestSuite(tradingSuite)
	suite.Run(t, tradingDeploySuite)
	fmt.Println("Finishing entry point...")
}

func convertCommittees(
	beaconComms []string,
) ([]common.Address, error) {
	beaconOld := make([]common.Address, len(beaconComms))
	for i, pk := range beaconComms {
		cpk := &CommitteePublicKey{}
		cpk.FromString(pk)
		addr, err := convertPubkeyToAddress(*cpk)
		if err != nil {
			return nil, err
		}
		beaconOld[i] = addr
		fmt.Printf("beaconOld: %s\n", addr.Hex())
	}
	return beaconOld, nil
}

func (portalv3DeploySuite *TradingDeployTestSuite) TestDeployAllContracts() {
	admin := common.HexToAddress(Admin)
	fmt.Println("Admin address:", admin.Hex())
	// Genesis committee
	// for testnet & local env
	beaconComm, err := convertCommittees(testnetBeaconCommitteePubKeys)
	require.Equal(portalv3DeploySuite.T(), nil, err)
	// NOTE: uncomment this block to get mainnet committees when deploying to mainnet env
	/*
		beaconComm, bridgeComm, err := convertCommittees(
			mainnetBeaconCommitteePubKeys, mainnetBridgeCommitteePubKeys,
		)
	*/

	// Deploy incognito_proxy
	auth := bind.NewKeyedTransactor(portalv3DeploySuite.ETHPrivKey)
	auth.Value = big.NewInt(0)

	incAddr, tx, _, err := incognitoproxy.DeployIncognitoproxy(auth, portalv3DeploySuite.ETHClient, admin, beaconComm)
	require.Equal(portalv3DeploySuite.T(), nil, err)

	fmt.Println("deployed incognito_proxy")
	fmt.Printf("addr: %s\n", incAddr.Hex())

	// Wait until tx is confirmed
	err = wait(portalv3DeploySuite.ETHClient, tx.Hash())
	require.Equal(portalv3DeploySuite.T(), nil, err)

	portalv3Addr, tx, _, err := portalv3.DeployPortalv3(auth, portalv3DeploySuite.ETHClient)
	require.Equal(portalv3DeploySuite.T(), nil, err)

	fmt.Println("deployed portalv3")
	fmt.Printf("addr: %s\n", portalv3Addr.Hex())

	// Wait until tx is confirmed
	err = wait(portalv3DeploySuite.ETHClient, tx.Hash())
	require.Equal(portalv3DeploySuite.T(), nil, err)

	portalv3ABI, _ := abi.JSON(strings.NewReader(portalv3.Portalv3ABI))
	input, _ := portalv3ABI.Pack("initialize", incAddr)

	delegator, tx, _, err := delegator.DeployDelegator(auth, portalv3DeploySuite.ETHClient, portalv3Addr, admin, input)
	require.Equal(portalv3DeploySuite.T(), nil, err)
	// incAddr := common.HexToAddress(IncognitoProxyAddress)
	fmt.Println("deployed delegator")
	fmt.Printf("addr: %s\n", delegator.Hex())

	// Wait until tx is confirmed
	err = wait(portalv3DeploySuite.ETHClient, tx.Hash())
	require.Equal(portalv3DeploySuite.T(), nil, err)
}

func convertPubkeyToAddress(cKey CommitteePublicKey) (common.Address, error) {
	pk, err := crypto.DecompressPubkey(cKey.MiningPubKey[BRI_CONSENSUS])
	if err != nil {
		return common.Address{}, errors.Wrapf(err, "cKey: %+v", cKey)
	}
	address := crypto.PubkeyToAddress(*pk)
	return address, nil
}
