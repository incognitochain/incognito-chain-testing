pragma solidity 0.6.6;
pragma experimental ABIEncoderV2;

import "./IERC20.sol";
import "./pause.sol";

/**
 * Math operations with safety checks
 */
library SafeMath {
    function safeMul(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a * b;
        require(a == 0 || c / a == b);
        return c;
    }

    function safeDiv(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b > 0);
        uint256 c = a / b;
        require(a == b * c + a % b);
        return c;
    }

    function safeSub(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b <= a);
        return a - b;
    }

    function safeAdd(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a + b;
        require(c>=a && c>=b);
        return c;
    }
}


/**
 * @dev Interface of the contract capable of checking if an instruction is
 * confirmed over at Incognito Chain
 */
interface Incognito {
    function instructionApproved(
        bool,
        bytes32,
        uint,
        bytes32[] calldata,
        bool[] calldata,
        bytes32,
        bytes32,
        uint[] calldata,
        uint8[] calldata,
        bytes32[] calldata,
        bytes32[] calldata
    ) external view returns (bool);
}

contract PortalV3 is AdminPausable {

    using SafeMath for uint;
    address constant public ETH_TOKEN = 0x0000000000000000000000000000000000000000;
    address public delegator;
    Incognito public incognito;
    bool notEntered = true;
    bool isInitialized = false;
    mapping(uint8 => bool) public metadata;
    mapping(bytes32 => bool) public withdrawed;
    struct BurnInstData {
        uint8 meta; // type of the instruction
        uint8 shard; // ID of the Incognito shard containing the instruction, must be 1
        address[] tokens; // ETH address of the tokens contract (0x0 for ETH)
        address payable to; // ETH address of the receiver of the token
        uint[] amounts; // burned amounts (on Incognito)
        bytes32 itx; // Incognito's burning tx
    }

    event Deposit(address tokenID, string custodianIncAddress, uint amount);
    event Withdraw(address[] token, address to, uint[] amount);
    event Delegator(address);
    event IncognitoProxy(address);
    event MetaData(uint8, bool);

    /**
     * @dev Prevents a contract from calling itself, directly or indirectly.
     * Calling a `nonReentrant` function from another `nonReentrant`
     * function is not supported. It is possible to prevent this from happening
     * by making the `nonReentrant` function external, and make it call a
     * `private` function that does the actual work.
     */
    modifier nonReentrant() {
        // On the first call to nonReentrant, notEntered will be true
        require(notEntered, "can not reentrant to vault");

        // Any calls to nonReentrant after this point will fail
        notEntered = false;

        _;

        // By storing the original value once again, a refund is triggered (see
        // https://eips.ethereum.org/EIPS/eip-2200)
        notEntered = true;
    }

    /**
     * @dev Creates new Vault to hold assets for Incognito Chain
     * @param incognitoProxyAddress: contract containing Incognito's committees
     * After migrating all assets to a new Vault, we still need to refer
     * back to previous Vault to make sure old withdrawals aren't being reused
     */
    function initialize(address incognitoProxyAddress) external {
        require(!isInitialized);
        incognito = Incognito(incognitoProxyAddress);
        expire = now + 3 * 365 days;
        // init metadata type accepted
        metadata[170] = true; // custodian withdraw free collateral
        metadata[171] = true; // custodian liquidated
        metadata[172] = true; // custodian run away with public token
        isInitialized = true;
        notEntered = true;
    }

    function deposit(string calldata custodianIncAddress) isNotPaused nonReentrant  payable external {
        require(address(this).balance <= 10 ** 27, "max value reached");

        emit Deposit(ETH_TOKEN, custodianIncAddress, msg.value);
    }

    function depositERC20(address token, uint amount, string calldata custodianIncAddress) isNotPaused nonReentrant external {
        IERC20 erc20Interface = IERC20(token);
        uint8 decimals = getDecimals(address(token));
        uint tokenBalance = erc20Interface.balanceOf(address(this));
        uint beforeTransfer = tokenBalance;
        uint emitAmount = amount;
        if (decimals > 9) {
            emitAmount = emitAmount / (10 ** (uint(decimals) - 9));
            tokenBalance = tokenBalance / (10 ** (uint(decimals) - 9));
        }
        require(emitAmount <= 10 ** 18 && tokenBalance <= 10 ** 18 && emitAmount.safeAdd(tokenBalance) <= 10 ** 18, "max value reached");
        erc20Interface.transferFrom(msg.sender, address(this), amount);
        require(checkSuccess(), "transfer from got error");
        require(balanceOf(token).safeSub(beforeTransfer) == amount, "the input amount not equal to amount received");

        emit Deposit(token, custodianIncAddress, emitAmount);
    }

    /**
     * @dev Verifies that a burn instruction is valid
     * @notice All params except inst are the list of 2 elements corresponding to
     * the proof on beacon and bridge
     * @notice All params are the same as in `withdraw`
     */
    function verifyInst(
        bytes memory inst,
        uint heights,
        bytes32[] memory instPaths,
        bool[] memory instPathIsLefts,
        bytes32 instRoots,
        bytes32 blkData,
        uint[] memory sigIdxs,
        uint8[] memory sigVs,
        bytes32[] memory sigRs,
        bytes32[] memory sigSs
    ) view internal {
        // Each instruction can only by redeemed once
        bytes32 beaconInstHash = keccak256(abi.encodePacked(inst, heights));

        // Verify instruction on beacon
        require(incognito.instructionApproved(
                true, // Only check instruction on beacon
                beaconInstHash,
                heights,
                instPaths,
                instPathIsLefts,
                instRoots,
                blkData,
                sigIdxs,
                sigVs,
                sigRs,
                sigSs
            ), "invalid instruction data");
    }

    function withdrawLockedTokens(
        bytes memory inst,
        uint heights,
        bytes32[] memory instPaths,
        bool[] memory instPathIsLefts,
        bytes32 instRoots,
        bytes32 blkData,
        uint[] memory sigIdxs,
        uint8[] memory sigVs,
        bytes32[] memory sigRs,
        bytes32[] memory sigSs
    ) isNotPaused nonReentrant public {
        BurnInstData memory data = parseBurnInst(inst);
        require(metadata[data.meta], "metadata type is not allowed on portalv3"); // Check instruction type
        require(!withdrawed[data.itx], "withdraw transaction already used"); // Not withdrawed
        withdrawed[data.itx] = true;

        verifyInst(
            inst,
            heights,
            instPaths,
            instPathIsLefts,
            instRoots,
            blkData,
            sigIdxs,
            sigVs,
            sigRs,
            sigSs
        );

        // Send and notify
        for (uint8 i = 0; i < data.tokens.length; i++) {
            if (data.tokens[i] != ETH_TOKEN) {
                uint8 decimals = getDecimals(data.tokens[i]);
                if (decimals > 9) {
                    data.amounts[i] = data.amounts[i] * (10 ** (uint(decimals) - 9));
                }
                IERC20(data.tokens[i]).transfer(data.to, data.amounts[i]);
                require(checkSuccess(), "internal transaction error");
            } else {
                (bool success, ) =  data.to.call{value: data.amounts[i]}("");
                require(success, "internal transaction error");
            }
        }
        emit Withdraw(data.tokens, data.to, data.amounts);
    }

    /**
     * @dev Parses a burn instruction and returns the components
     * @param inst: the full instruction, containing both metadata and body
     */
    function parseBurnInst(bytes memory inst) public pure returns (BurnInstData memory) {
        require(inst.length >= 3, "Length of instruction must greater than 3");
        BurnInstData memory data;
        data.meta = uint8(inst[0]);
        data.shard = uint8(inst[1]);
        uint8 numOfToken = uint8(inst[2]);
        require(inst.length == 170 + 64 * numOfToken, "Invalid instruction");
        address[] memory tokens = new address[](numOfToken);
        address payable to;
        uint[] memory amounts = new uint[](numOfToken);
        bytes32 itx;
        assembly {
        //skip first 0x20 bytes (stored length of inst)
        // skip the next 0x6A bytes (stored incognito address)
            to := mload(add(inst, 0x8A)) // [138:170]
            itx := mload(add(inst, add(0xAA, mul(0x40, numOfToken)))) // [170+64*x:]
        }

        // load tokens and amounts into array
        for (uint8 i = 1; i <= numOfToken; i++) {
            assembly {
                mstore(add(tokens, mul(0x20,i)), mload(add(inst, add(0x6A, mul(i, 0x40)))))
                mstore(add(amounts, mul(0x20,i)), mload(add(inst, add(0x8A, mul(i, 0x40)))))
            }
        }

        data.tokens = tokens;
        data.to = to;
        data.amounts = amounts;
        data.itx = itx;
        return data;
    }

    /**
     * @dev Update incognito proxy address
     * @param _incognitoProxy: incognito proxy address
     */
    function updateIncognitoAddress(address _incognitoProxy) onlyAdmin isPaused external {
        incognito = Incognito(_incognitoProxy);

        IncognitoProxy(delegator);
    }

    /**
     * @dev Update meta data type
     * @param _meta: meta data type
     * @param _value: meta data value
     */
    function updateMetaData(uint8 _meta, bool _value) onlyAdmin external {
        metadata[_meta] = _value;

        MetaData(_meta, _value);
    }

    /**
    * @dev Check if transfer() and transferFrom() of ERC20 succeeded or not
    * This check is needed to fix https://github.com/ethereum/solidity/issues/4116
    * This function is copied from https://github.com/AdExNetwork/adex-protocol-eth/blob/master/contracts/libs/SafeERC20.sol
    */
    function checkSuccess() private pure returns (bool) {
        uint256 returnValue = 0;
        assembly {
        // check number of bytes returned from last function call
            switch returndatasize()

            // no bytes returned: assume success
            case 0x0 {
                returnValue := 1
            }

            // 32 bytes returned: check if non-zero
            case 0x20 {
            // copy 32 bytes into scratch space
                returndatacopy(0x0, 0x0, 0x20)

            // load those bytes into returnValue
                returnValue := mload(0x0)
            }

            // not sure what was returned: don't mark as success
            default { }
        }
        return returnValue != 0;
    }

    /**
     * @dev Get the decimals of an ERC20 token, return 0 if it isn't defined
     * We check the returndatasize to covert both cases that the token has
     * and doesn't have the function decimals()
     */
    function getDecimals(address token) public view returns (uint8) {
        IERC20 erc20 = IERC20(token);
        return uint8(erc20.decimals());
    }

    /**
     * @dev Get the amount of coin deposited to this smartcontract
     */
    function balanceOf(address token) public view returns (uint) {
        if (token == ETH_TOKEN) {
            return address(this).balance;
        }
        return IERC20(token).balanceOf(address(this));
    }
}