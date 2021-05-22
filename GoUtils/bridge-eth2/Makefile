all: beacon bridge burn erc20

beacon: build
	go test -run=TestSimulatedSwapBeacon

bridge: build
	go test -run=TestSimulatedSwapBridge

burn: build
	go test -run=TestSimulatedBurn

erc20: build
	go test -run=TestSimulatedErc20

build: bridge/incognito_proxy/incognito_proxy.go \
	bridge/vault/vault.go \
	bridge/vault/vaultHelper.go \
	bridge/pause/pause.go \
	erc20/fail/fail.go \
	erc20/dless/dless.go \
	bridge/kbntrade/kbn_trade.go \
	bridge/uniswap/uniswap_trade.go

.PHONY: all beacon bridge burn erc20 build

erc20/ERC20.go: erc20/ERC20.vy
	./gengo.sh erc20/ERC20.vy erc20

bridge/incognito_proxy/incognito_proxy.go: bridge/contracts/incognito_proxy.sol
	./gengo.sh bridge/contracts/incognito_proxy.sol bridge/incognito_proxy

bridge/vault/vault.go: bridge/contracts/vault.sol
	./gengo.sh bridge/contracts/vault.sol bridge/vault

bridge/vault/vaultHelper.go: bridge/contracts/vaultHelper.sol
	./gengo.sh bridge/contracts/vaultHelper.sol bridge/vault

bridge/kbntrade/kbn_trade.go: bridge/contracts/kbn_trade.sol
	./gengo.sh bridge/contracts/kbn_trade.sol bridge/kbntrade

bridge/uniswap/uniswap_trade.go: bridge/contracts/uniswap_trade.sol
	./gengo.sh bridge/contracts/uniswap_trade.sol bridge/uniswap

bridge/pause/pause.go: bridge/contracts/pause.sol
	./gengo.sh bridge/contracts/pause.sol bridge/pause

erc20/fail/fail.go: erc20/fail/fail.sol
	./gengo.sh erc20/fail/fail.sol erc20/fail

erc20/dless/dless.go: erc20/dless/dless.sol
	./gengo.sh erc20/dless/dless.sol erc20/dless

clean: 
	rm bridge/incognito_proxy/incognito_proxy.go bridge/vault/vault.go bridge/pause/pause.go erc20/fail/fail.go erc20/dless/dless.go bridge/kbntrade/kbn_trade.go bridge/uniswap/uniswap_trade.go
	