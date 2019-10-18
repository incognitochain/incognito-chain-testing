"""
Created 27 Sep 2018

@Author: Van.Vo
"""
from Automation.pages.base_page import BasePage


class MainMenu(BasePage):
    """
    Class for main menu.
    """
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.instant_quote_page = "[data-text='header_open-dialog-get-intant-quote']"
        self.sign_up_page = "[data-test='header_sign-up']"
        self.sign_in_page = "[data-test='header_sign-in']"

    def open_instant_quote_popup(self):
        """
        Open instant quote pop.
        """
        self.click_element(self.instant_quote_page)

    def open_sign_up_popup(self):
        """
        Open sign up popup.
        """
        self.click_element(self.sign_up_page)

    def open_login_popup(self):
        """
        Open login popup
        """
        self.click_element(self.sign_in_page)

