# incognito-chain-testing
incognito-chain testing

```
pip3 install -r pip_requirement.txt
source auto-env/bin/activate
pytest testcases/prv_transaction/test_sendPRV.py -s -v --no-print-logs

# HOW TO RUN A TEST
./run.sh {test bed} {test data} {path to test script or test suite} [specific test case name (optional)]

   - Test bed: locate under IncognitoChain/TestBeds/
   - Test data: locate under IncognitoChain/TestData/
   - Test script/suite: locate under IncognitoChain/TestCases

```

# Setup chain
```
sudo apt update
sudo apt install openjdk-8-jdk openjdk-8-jre


golang 1.13.1
https://www.digitalocean.com/community/tutorials/how-to-install-go-on-ubuntu-18-04
sudo ln -s /usr/local/go/bin/go /usr/local/bin/go

sudo apt remove --autoremove python3.8 python3.8-minimal
https://linuxize.com/post/how-to-install-python-3-7-on-ubuntu-18-04/
sudo rm /usr/bin/python3; sudo ln -s python3.7 /usr/bin/python3
https://linuxize.com/post/how-to-install-pip-on-ubuntu-18.04/

```
