# incognito-chain-testing

```
- Install required modules
    $ pip3 install -r pip_requirement.txt
- pytest-allure-adaptor is obsoleted, remove it if already installed
    $ pip3 uninstall pytest-allure-adaptor 


# HOW TO RUN A TEST
1. Using run.sh script
    ./run.sh {test bed} {test data} {path to test script or test suite} [specific test case name (optional)]

   - Test bed: locate under TestBeds/
   - Test data: locate under TestData/
   - Test script/suite: locate under TestCases
   - example: 
        ./run.sh Testnet account_sample TestCases/Transaction/test_TRX001*

2. using pytest command directly: (use for old framework, not recommend for new framework
    pytest testcases/prv_transaction/test_sendPRV.py -s -v --no-print-logs

```

# Setup chain
```
sudo apt update
sudo apt install openjdk-8-jdk openjdk-8-jre


golang 1.13.1
https://www.digitalocean.com/community/tutorials/how-to-install-go-on-ubuntu-18-04
sudo ln -s /usr/local/go/bin/go /usr/local/bin/go

```
