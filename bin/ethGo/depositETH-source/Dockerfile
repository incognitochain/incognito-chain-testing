FROM golang:1.15

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y git supervisor 
RUN git clone --depth 1 --branch portalv3 https://github.com/incognitochain/incognito-chain
RUN git clone --depth 1 --branch testnet_bcfn_libp2p_20201018_02 https://github.com/incognitochain/incognito-highway && \
    cd incognito-highway && \
    go build -o highway
COPY supervisord.conf supervisord.conf
COPY run.sh run.sh
COPY blockchain.txt ./incognito-chain/blockchain/blockchain.go
COPY params.txt ./incognito-chain/blockchain/params.go
RUN chmod a+x run.sh
RUN mkdir /var/log/supervisord
RUN cd /go/incognito-chain && go build -o incognito

EXPOSE 9334 9338

ENTRYPOINT ["/go/run.sh"]
# CMD ["supervisord"]

