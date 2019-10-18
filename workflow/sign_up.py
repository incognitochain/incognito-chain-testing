"""
Created Oct 10 2018

@Author: Van.Vo
"""
# pylint: disable = too-many-arguments
from Automation.libs.swlog import wait_time
from Automation.pages.sign_up.base_sign_up import BaseSignUp


class SignUp(BaseSignUp):
    """
    Workflow for sign up page.
    """

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        # Locator input error for business signup
        self.company_name_input_err = "[data-test='register_company-name-error']"
        self.uen_input_err = "[data-test='register_business-uen-error']"
        self.business_name_input_err = "[data-test='register_business-name-error']"
        self.business_phone_input_err = "[data-test='register_business-phone-error']"
        self.business_email_input_err = "[data-test='register_business-email-error']"
        self.business_pass_input_err = "[data-test='register_business-password-error']"
        self.business_exist_email_err = "[data-test='register_business-email-error']"
        # Locator input error for client signup
        self.client_name_input_err = "[data-test='register_client-name-error']"
        self.client_name_input_err = "[data-test='register_client-name-error']"
        self.client_phone_input_err = "[data-test='register_client-phone-error']"
        self.client_email_input_err = "[data-test='register_client-email-error']"
        self.client_pass_input_err = "[data-test='register_client-password-error']"
        self.client_exist_email_err = "[data-test='register_client-email-error']"

    def get_signup_title(self):
        """
        Get sign up title
        """
        title = self.driver.title
        return title

    def signup_as_business(self, company, uen, business_name,
                           phone, email, password, create=True):
        """
        Sign up as business account
        """
        # Choose signup as business button
        self.choose_signup_as_business()
        # Input company name
        self.input_company_name(company)
        # Input company uen
        self.input_company_uen(uen)
        # Input business name
        self.input_business_name(business_name)
        # Input business phone
        self.input_business_phone(phone)
        # Input business mail
        self.input_business_email(email)
        # Input business password
        self.input_business_password(password)
        # Click create account
        if create:
            wait_time(2)
            self.click_create_account()

    def signup_as_client(self, client_name, phone, email,
                         password, create=True):
        """
        Sign up as business account
        """
        # Choose signup as business button
        self.choose_signup_as_client()
        # Input client name
        self.input_client_name(client_name)
        # Input client phone
        self.input_client_phone(phone)
        # Input client mail
        self.input_client_email(email)
        # Input client password
        self.input_client_password(password)
        # Click create account
        if create:
            wait_time(2)
            self.click_create_account()

    def verify_show_business_password(self, click_show=True):
        """
        Verify type of password field
        """
        result = self.get_business_password_attribute(click_show)
        if result == 'password':
            return True
        return False

    def verify_show_client_password(self, click_show=True):
        """
        Verify type of password field
        """
        result = self.get_client_password_attribute(click_show)
        if result == 'password':
            return True
        return False

    def get_company_name_input_err_msg(self):
        """
        Get error message when input invalid company name
        """
        err_msg = self.get_text_if_present(self.company_name_input_err)
        return err_msg

    def get_uen_input_err_msg(self):
        """
        Get error message when input invalid uen
        """
        err_msg = self.get_text_if_present(self.uen_input_err)
        return err_msg

    def get_business_name_input_err_msg(self):
        """
        Get error message when input invalid business name
        """
        err_msg = self.get_text_if_present(self.business_name_input_err)
        return err_msg

    def get_business_phone_input_err_msg(self):
        """
        Get error message when input invalid business phone
        """
        err_msg = self.get_text_if_present(self.business_phone_input_err)
        return err_msg

    def get_business_email_input_err_msg(self):
        """
        Get error message when input invalid business email
        """
        err_msg = self.get_text_if_present(self.business_email_input_err)
        return err_msg

    def get_business_pass_input_err_msg(self):
        """
        Get error message when input invalid business password
        """
        err_msg = self.get_text_if_present(self.business_pass_input_err)
        return err_msg

    def get_client_name_input_err_msg(self):
        """
        Get error message when input invalid client name
        """
        err_msg = self.get_text_if_present(self.client_name_input_err)
        return err_msg

    def get_client_phone_input_err_msg(self):
        """
        Get error message when input invalid client phone
        """
        err_msg = self.get_text_if_present(self.client_phone_input_err)
        return err_msg

    def get_client_email_input_err_msg(self):
        """
        Get error message when input invalid client email
        """
        err_msg = self.get_text_if_present(self.client_email_input_err)
        return err_msg

    def get_client_pass_input_err_msg(self):
        """
        Get error message when input invalid  client password
        """
        err_msg = self.get_text_if_present(self.client_pass_input_err)
        return err_msg

    def get_business_email_exist_error(self):
        """
        Get error message when email exist
        """
        err_msg = self.get_text_if_present(self.business_exist_email_err)
        return err_msg

    def get_client_email_exist_error(self):
        """
        Get error message when email exist
        """
        err_msg = self.get_text_if_present(self.client_exist_email_err)
        return err_msg
