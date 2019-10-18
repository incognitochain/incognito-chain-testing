"""
Created Oct 11 2018

@Author: Khanh Le
"""
# pylint: disable = too-many-public-methods
import unittest
import pytest
# from ddt import ddt, data
from Automation.libs.swlog import STEP, assert_true, wait_time, DEBUG
from Automation.libs.node_handler import ssh2pc
# from Automation.pages.sign_up.base_sign_up import BaseSignUp
# from Automation.util.utils import Utils
# from Automation.util.mail_checking import MailChecking
# from Automation.pages.menu.main_menu import MainMenu
# from Automation.pages.login.base_login import BaseLogin
# from Automation.pages.user_profile.base_user_profile import BaseUserProfile
# from Automation.workflow.sign_up import SignUp
import requests, json, time

class test_sendPRV(unittest.TestCase):
    """
    Test case: Send PRV
    """

    test_data = {
        'address1_privatekey': "112t8rnXzp9Z1PTU5YQ78p5SsVUJiiTZweNmcV4hxJQ1EYobH5tB9mow4TrkiGFXtQXnadaMaLFbtGFT8UoxN3SkiNHkYkWUseyv98QCCuK9",
        'address2_payment': "1Uv4VVdevEpxhjreX3KkfwfWgPKUCAVU9PF7P5YdNuD52VhMVAT64oFkZLqweGk8xFermK6AbvoCemebGJvumFbQM7iGWXKaS14UiHcmR",
        'prv_amount': 10000000000,
        'address2_privatekey': "112t8rnXrD5kGq7KouCgfhy4QrDYkG9woiizUdr8LEj1jDxwM3fbKoVDijXKTBuXnn4rwmvGP8Ud1CYYdKepvDAehPvndENuAehaweBqY1BX",
        '_WRONG_PASSWORD': "wrong@password",
        '_NEW_PASSWORD': "new$%password",
        '_PHONE_NUMBER': "88888888",
        '_SUBJECT_ACTIVE_MAIL': 'FreightKnot Account activation',
        '_SUBJECT_RESET_PASS': 'FreightKnot Account reset password',
        'MAIL_SERVER': 'https://www.mailinator.com',
        'test_invalid_email': ["testemail.com", "test@mailcom"],
        'test_valid_email': ["test@email.com", "test@mail.com.sg"],
        'test_invalid_password': ["1", "12345", "@#$%F", "     "],
        'test_valid_password': ["123456", "ASDfZXCV1999", "123@$%^ Zxcv^", "tEsT_Pass-Word"]
    }

    def send_trx(self, sender_privatekey, receiver_paymentaddress, amount_prv):
        url = "http://vps162:9354"
        headers = {'Content-Type': 'application/json'}  
        data = {"jsonrpc":"1.0","method":"createandsendtransaction", "params":[sender_privatekey, {receiver_paymentaddress: amount_prv}, -1, 0], "id":1}
        response = requests.post(url, data=json.dumps(data), headers=headers)   
        # print(response.text)                
        aa = json.loads(response.text)
        
        if aa['Error']== None:
            # print (aa['Result']['TxID'])
            # print (aa['Result']['ShardID'])
            return aa['Result']['TxID']
        else:
            print (aa['Error']['Message'])
            return aa['Error']['Message']
            
    def subscribe_trx(self):
        pass


    def get_balance(self, address_privatekey):
        url = "http://vps162:9354"
        headers = {'Content-Type': 'application/json'}  
        data = {"jsonrpc":"1.0","method":"getbalancebyprivatekey", "params":[address_privatekey], "id":1}
        response = requests.post(url, data=json.dumps(data), headers=headers)   
        aa = json.loads(response.text)
        
        if aa['Error']== None:
            return aa['Result']
        else:
            print (aa['Error']['Message'])
            return aa['Error']['Message']

    @pytest.mark.run
    def est_sendPRV_privacy(self):
        """
        Verify send PRV to another address
        """

        STEP("1. get address2 balance")
        step1_result = self.get_balance(self.test_data["address2_privatekey"])
        assert step1_result != "Invalid parameters"
        STEP("2. init prv for address1")
        step2_result = self.send_trx(self.test_data["address1_privatekey"],self.test_data["address2_payment"], self.test_data["prv_amount"])
        assert step2_result != 'Can not create tx'
        STEP("3. send from address1 to address2")
        print("cccccccccccccccc")
        STEP("4. check address1 balance")
        print("sleep 20")
        time.sleep(20)
        STEP("5. check address2 balance")
        step5_result = self.get_balance(self.test_data["address1_privatekey"])
        assert step5_result == step1_result + self.test_data["prv_amount"]
        

    @pytest.mark.run
    def test_sendPRV_noprivacy(self):
        """
        Verify that a banner message is changed after click send activate mail
        """

        staking49 = ssh2pc("35.227.101.26","david","na")
        print(staking49.startDocker("staking49"))
        staking49.logout()