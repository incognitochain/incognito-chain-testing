"""
Created Oct 23 2018

@Author: Van Vo
"""
from Automation.libs.swlog import DEBUG, wait_time
from Automation.pages.base_page import BasePage


class MailChecking(BasePage):
    """
    Class check mail at wwww.mailinator.com
    """
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.email = "[id='inboxfield']"
        self.go_btn = "button[class^='btn']"

    def go_to_inbox(self, email):
        """
        Go to inbox mailinator
        """
        self.input_text(self.email, email)
        self.click_go()

    def click_go(self):
        self.click_element(self.go_btn)

    def click_on_coming_mail(self, text):
        """
        Click inbox mail
        """
        xpath = "//*[text()[contains(., '%s')]]" % text
        links = [b for b in self.driver.find_elements_by_xpath(xpath) if b.is_displayed()]
        if links:
            links[0].click()
        else:
            message = "No visible link with text %s found" % text
            DEBUG(message)

    def click_activate_account(self):
        """
        Click Activate Account
        """
        self.driver.switch_to.frame("msg_body")
        xpath = "//a[text()[contains(., 'Activate Account')]]"
        button_active = self.driver.find_element_by_xpath(xpath)
        if button_active:
            button_active.click()
        else:
            message = "No visible link with text found"
            DEBUG(message)
        self.driver.switch_to.default_content()

    def click_reset_password(self):
        """
        Click reset password
        """
        self.driver.switch_to.frame("msg_body")
        xpath = "//a[text()[contains(., 'Reset Password')]]"
        button_active = self.driver.find_element_by_xpath(xpath)
        if button_active:
            button_active.click()
        else:
            message = "No visible link with text found"
            DEBUG(message)
        self.driver.switch_to.default_content()

    def count_number_mail_in_inbox(self, email):
        """
        Count the number mail in inbox
        """
        xpath = "//*[text()[contains(., '%s')]]" % email
        mails = [b for b in self.driver.find_elements_by_xpath(xpath) if b.is_displayed()]
        return len(mails)

    def activate_account(self, text):
        """
        Activate account
        """
        self.click_on_coming_mail(text)
        self.click_activate_account()

    def reset_password(self, text):
        """
        Activate account
        """
        self.click_on_coming_mail(text)
        self.click_reset_password()
