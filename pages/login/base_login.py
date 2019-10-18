"""
Created Oct 18 2018

@Author: Van.Vo
"""
import time
from selenium.webdriver.common.by import By

from Automation.libs.swlog import wait_time
from Automation.pages.base_page import BasePage
from selenium.common.exceptions import NoSuchElementException


class BaseLogin(BasePage):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

        # Locator for login
        self.login_email = "[data-test='input-email'] input"
        self.login_password = "[data-test='input-password'] input"
        self.login_show_password = "div[class*='show-password-icon']"
        self.login_remember_me = "[data-test='checkbox-remember-me']"
        self.login_forgot_password_btn = "[data-test='btn-forgot-password']"
        self.login_button = "[data-test='btn-login']"
        self.login_err_input_email = "[data-test='mess-input-email']"
        self.login_err_input_password = "[data-test='mess-input-password']"
        # Locator for reset password
        self.reset_password_input_email = "[data-test='input-email-forgot-password'] input"
        self.request_password_button = "[data-test='btn-send-password'] button"
        self.request_password_button_sent = "[data-test='btn-send-password'] div p"
        self.reset_pass_input_email_err = "[data-test='login_mess-input-email-forgot-password']"
        self.resend_mail = "[data-test='resend-mail']"
        self.login_succeed = "[data-test='menu-bar-user']"

        self.reset_new_password = "[data-test='input-newPassword'] input"
        self.reset_confirm_password = "[data-test='input-rePassword'] input"
        self.reset_btn = "[data-test='reset-password_btn-reset-password']"

    def input_login_email(self, email):
        """
        Input login email
        """
        self.input_text(self.login_email, email)

    def input_email_reset_password(self, email):
        """
        Input forgot email
        """
        self.input_text(self.reset_password_input_email, email)

    def input_login_password(self, password):
        """
        Input login password
        """
        self.input_text(self.login_password, password)

    def show_login_password(self):
        """
        Click show login password
        """
        self.click_element(self.login_show_password)

    def choose_remember_me(self):
        """
        Choose remember me
        """
        self.click_element(self.login_remember_me)

    def click_login_button(self):
        """
        Click login button
        """
        self.click_element(self.login_button)

    def click_forgot_password(self):
        """
        Click forgot password
        """
        self.click_element(self.login_forgot_password_btn)

    def get_err_msg_input_email(self):
        """
        Get error message when input invalid email
        """
        err_msg = self.get_text_if_present(self.login_err_input_email)
        return err_msg

    def get_err_msg_input_password(self):
        """
        Get error message when input invalid password
        """
        err_msg = self.get_text_if_present(self.login_err_input_password)
        return err_msg

    def is_login_button_enable(self):
        """
        Check if login button is enabled
        """
        result = self.wait_for_element_clickable(self.login_button,
                                                 By.CSS_SELECTOR, timeout=15)
        return result

    def is_request_new_pass_enable(self):
        """
        Check if request new password button is enabled
        """
        result = self.wait_for_element_clickable(self.request_password_button,
                                                 By.CSS_SELECTOR, timeout=15)
        return result

    def get_err_msg_input_email_reset_pass(self):
        """
        Get error message when input invalid email to reset password
        """
        err_msg = self.get_text_if_present(self.reset_pass_input_email_err)
        return err_msg

    def click_request_password_button(self):
        """
        Click reset password button
        """
        self.click_element(self.request_password_button)

    def log_in(self, email, password, click_login=True):
        """
        Login to freightknot
        """
        self.input_login_email(email)
        self.input_login_password(password)
        if click_login:
            self.click_login_button()
            wait_time(2)

    def request_new_password(self, email, click=True):
        """
        Reset password
        """
        # Input email
        self.input_email_reset_password(email)
        # Click reset password
        if click:
            self.click_request_password_button()

    def create_new_password(self):
        """
        Create new password
        """
        pass

    def verify_show_login_password(self, click_show=True):
        """
        Verify type of password field
        """
        result = self.get_login_password_attribute(click_show)
        if result == 'password':
            return True
        return False

    def get_login_password_attribute(self, click_show=True):
        """
        Get business password button
        """
        if click_show:
            self.show_login_password()
        _type = self.get_element_from_css(self.login_password).get_attribute('type')
        return _type

    def is_login_succeed(self):
        """
        check if login succeed
        """
        if self.waiting_for_element_visible(self.login_succeed, By.CSS_SELECTOR):
            return True
        return False

    def is_send_request_new_password(self):
        """
        check if request new password is sent
        """
        text = self.get_text_if_present(self.request_password_button_sent)
        if text == 'Request sent':
            return True
        return False

    def resend_activate_mail(self):
        """
        Resend activation email after login
        """
        self.click_element(self.resend_mail)

    def is_banner_resend_mail_present(self):
        """
        Check if banner resend activate mail is displayed
        """
        if self.waiting_for_element_loaded(self.resend_mail, By.CSS_SELECTOR):
            return True
        return False

    def reset_password(self, password):
        """
        Request new password
        """
        # Input new password
        self.input_text(self.reset_new_password, password)
        # Confirm new password
        self.input_text(self.reset_confirm_password, password)
        # Click reset password button
        self.click_element(self.reset_btn)
