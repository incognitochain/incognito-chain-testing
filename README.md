# incognito-chain-testing

- Use with Python 3.8 or 3.9 only, having some problems with Python 3.10 which not yet get resolved
- Install required modules
    $ pip3 install -r pip_requirement.txt
- pytest-allure-adaptor is obsoleted, remove it if already installed
    $ pip3 uninstall pytest-allure-adaptor 

# HOW TO RUN A TEST USING run.sh:
    ./run.sh {test bed} {test data} {path to test script or test suite} [specific test case name (optional)]
   - Test bed: locate under TestBeds/
   - Test data: locate under TestData/
   - Test script/suite: locate under TestCases
   
example: 
   
    ./run.sh Testnet account_sample 'TestCases/Transaction/test_TRX001*'
    CLEAR=1 ./run.sh Testnet account_sample 'TestCases/Transaction/test_TRX001*'  # delete all logs and report, then run test
    ./run.sh clear  # delete all logs and html report files then exit

#### NOTE: Environment variables when running test:
   - TOPUP: send some PRV to the test accounts in the "Test data"
   - CONVERT: convert all coin v1 if there's any in the "Test data"
   - SUBMIT: submit OTA key of "Test data" to fullnode

All those env vars acceptable value is 1/0 or empty, and they are set to 0 by default. Which mean by default, 
all accounts in "Test data" will not have any coin if there aren't some already, will not convert coin and won't
submit OTA keys to fullnode since all those actions needed to be executes only once for the same "Test Data".
So if the "Test data" is used the first time, you should exec:

    TOPUP=1 CONVERT=1 SUBMIT=1 ./run.sh [test bed] [test data]......


# Some tips when setting up chain
```
sudo apt update
sudo apt install openjdk-8-jdk openjdk-8-jre


golang 1.13.1
https://www.digitalocean.com/community/tutorials/how-to-install-go-on-ubuntu-18-04
sudo ln -s /usr/local/go/bin/go /usr/local/bin/go

```
