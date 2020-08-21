const Proxy = artifacts.require("IncognitoProxy");

module.exports = function(deployer) {
    let beacons = [
		"0xcb859a5fC20EEeCc4Cec191d8CCe5e31a2CC1dAF",
		"0x6294A3d1caE192f06dEe33152559531D447A076f",
		"0xA815f542096c8De2ECe5aB18d4cf9D2aBc5202EC",
		"0x4B895A89606aD73d2Fd7b887583858d6f2Cd229c",
		"0xdd0523326fD818a16783D392324003D1df163758",
		"0xf5b0A7D1270642e55a92A99D1AF9bb2B59982C71",
		"0xbEBE7795d8297c4A59542a81541878e2dBA95253",
		"0x894a0bEbb56cE3099A34f26b259D4038AE0E6088",
		"0x6D6abB339E215a92c190f045D88E8aF79A32Dd16",
		"0x81a3B54a6216585C6A262AAF2c4340Ac53F7c10c"
    ];
    let bridges = [
		"0xcb859a5fC20EEeCc4Cec191d8CCe5e31a2CC1dAF",
		"0x6294A3d1caE192f06dEe33152559531D447A076f",
		"0xA815f542096c8De2ECe5aB18d4cf9D2aBc5202EC",
		"0x4B895A89606aD73d2Fd7b887583858d6f2Cd229c",
		"0xdd0523326fD818a16783D392324003D1df163758",
		"0xf5b0A7D1270642e55a92A99D1AF9bb2B59982C71",
		"0xbEBE7795d8297c4A59542a81541878e2dBA95253",
		"0x894a0bEbb56cE3099A34f26b259D4038AE0E6088",
		"0x6D6abB339E215a92c190f045D88E8aF79A32Dd16",
		"0x81a3B54a6216585C6A262AAF2c4340Ac53F7c10c"
    ];
    deployer.deploy(Proxy, beacons, bridges);
};
