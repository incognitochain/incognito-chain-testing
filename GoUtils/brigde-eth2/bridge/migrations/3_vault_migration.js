const Vault = artifacts.require("Vault");
const Proxy = artifacts.require("IncognitoProxy");
const TetherToken = artifacts.require("TetherToken");
const Test = artifacts.require("Test");

module.exports = function (deployer) {
  deployer.deploy(Vault, Proxy.address);
  deployer.deploy(TetherToken, 1000000, "a", "b", 6);
  deployer.deploy(Test);
};
