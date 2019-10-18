"""
Created Oct 9 2018

@Author: Van.Vo
"""
# pylint: disable = too-many-instance-attributes

from Automation.pages.base_page import BasePage
from selenium.webdriver.common.by import By


class BaseSignUp(BasePage):
    """
    Base sign up page.
    """

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.reg_business = "[data-test='register_select-business']"
        self.reg_client = "[data-test='register_select-client']"
        self.company_name = "[data-test='input-companyName'] input"
        self.business_uen = "[data-test='input-businessUEN'] input"
        self.business_name = "[data-test='business-input-name'] input"
        self.business_phone = "[data-test='business-input-phone'] input"
        self.business_email = "[data-test='business-input-email'] input"
        self.business_password = "[data-test='business-input-password'] input"

        self.client_name = "[data-test='client-input-name'] input"
        self.client_phone = "[data-test='client-input-phone'] input"
        self.client_email = "[data-test='client-input-email'] input"
        self.client_password = "[data-test='client-input-password'] input"

        self.btn_create_account = "[data-test='register_btn-register']"
        self.register_success = "[data-test='register_success']"
        self.activate_success = "[data-test='active-account_success']"
        self.close_register = "div[class*='close-icon']"
        self.show_password_icon = "div[class*='show-password-icon']"
        self.continue_login = "[data-test='register_btn-continue-login']"

    def choose_signup_as_business(self):
        """
        Choose sign up as business.
        """
        self.click_element(self.reg_business)

    def choose_signup_as_client(self):
        """
        Choose sign up as business.
        """
        self.click_element(self.reg_client)

    def input_company_name(self, company_name):
        """
        Input company name.
        """
        self.input_text(self.company_name, company_name)

    def input_company_uen(self, business_uen):
        """
        Input company name.
        """
        self.input_text(self.business_uen, business_uen)

    def input_business_name(self, business_name):
        """
        Input business name.
        """
        self.input_text(self.business_name, business_name)

    def input_business_phone(self, business_phone):
        """
        Input business phone.
        """
        self.input_text(self.business_phone, business_phone)

    def input_business_email(self, business_email):
        """
        Input business email.
        """
        self.input_text(self.business_email, business_email)

    def input_business_password(self, business_password):
        """
        Input business password.
        """
        self.input_text(self.business_password, business_password)

    def show_business_password(self):
        """
        Show business password
        """
        self.click_element(self.show_password_icon)

    def click_create_account(self):
        """
        Click create account button.
        """
        self.click_element(self.btn_create_account)

    def input_client_email(self, client_email):
        """
        Input client email.
        """
        self.input_text(self.client_email, client_email)

    def input_client_name(self, client_name):
        """
        Input client name.
        """
        self.input_text(self.client_name, client_name)

    def input_client_phone(self, client_phone):
        """
        Input client phone.
        """
        self.input_text(self.client_phone, client_phone)

    def input_client_password(self, client_password):
        """
        Input client password.
        """
        self.input_text(self.client_password, client_password)

    def show_client_password(self):
        """
        Show client password
        """
        self.click_element(self.show_password_icon)

    def get_business_password_attribute(self, click_show=True):
        """
        Get business password button
        """
        if click_show:
            self.show_business_password()
        _type = self.get_element_from_css(self.business_password).get_attribute('type')
        return _type

    def get_client_password_attribute(self, click_show=True):
        """
        Get business password button
        """
        if click_show:
            self.show_client_password()
        _type = self.get_element_from_css(self.client_password).get_attribute('type')
        return _type

    def is_create_account_button_enable(self):
        """
        Check if create account button is enabled
        """
        result = self.wait_for_element_clickable(self.btn_create_account,
                                                 By.CSS_SELECTOR, timeout=15)
        return result

    def is_register_success(self):
        """
        Check if register success
        """
        result = self.waiting_for_element_visible(self.register_success,
                                                  By.CSS_SELECTOR, timeout=30)
        return result

    def is_activation_success(self):
        """
        Check if account is activated successfully
        """
        self.switch_to_window(self.driver.window_handles[1])
        result = self.waiting_for_element_visible(self.activate_success,
                                                  By.CSS_SELECTOR, timeout=30)
        return result

    def close_register_popup(self):
        """
        Close register popup
        """
        self.click_element(self.close_register)

    def get_business_email_from_input_field(self):
        """
        Get input v email from input text field
        """
        email = self.get_element_from_css(self.business_email).get_attribute('value')
        return email

    def get_client_email_from_input_field(self):
        """
        Get input client email from input text field
        """
        email = self.get_element_from_css(self.client_email).get_attribute('value')
        return email

    def continue_login_after_sign_up(self):
        """
        Click continue login after sign up
        """
        self.click_element(self.continue_login)