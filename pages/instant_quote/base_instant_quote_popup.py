"""
Created Sep 27 2018

@Author: Van.Vo
"""
import time
from Automation.libs.swlog import INFO
from selenium.webdriver.common.by import By
from Automation.pages.base_page import BasePage


class BaseInstantQuotePopup(BasePage):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.SLEEP_TIME = 3
        self.height = "input[data-test='get-instant-quote_input-height']"
        self.weight = "input[data-test='get-instant-quote_input-weight']"
        self.length = "input[data-test='get-instant-quote_input-length']"
        self.width = "input[data-test='get-instant-quote_input-width']"
        self.quantity = "input[data-test='get-instant-quote_input-quantity']"
        self.mail = "input[data-test='get-instant-quote_input-email']"
        self.btn_clear = "[data-test='get-instant-quote_btn-clear']"
        self.btn_back = "button[data-test='get-instant-quote_btn-clear-in-result']"
        self.btn_calculate = "button[data-test='get-instant-quote_btn-caculate']"
        self.measurement_dropdown = "div[data-test='get-instant-quote_select-measurement']"
        self.instant_quote_sign_up = "[data-test='get-instant-quote_btn-sign-up']"

    def input_height(self, height):
        """
        This method use to input height
        Args:
            height(number): height
        """
        self.input_text(self.height, height)

    def input_width(self, width):
        """
        This method use to input width
        Args:
            width(number): width
        """
        self.input_text(self.width, width)

    def input_weight(self, weight):
        """
        This method use to input weight
        Args:
            weight(number): weight
        """
        self.input_text(self.weight, weight)

    def input_length(self, length):
        """
        This method use to input length
        Args:
            length(number): length
        """
        self.input_text(self.length, length)

    def input_quantity(self, quantity):
        """
        This method use to input quantity
        Args:
            quantity(number): quantity
        """
        self.input_text(self.quantity, quantity)

    def input_mail(self, mail):
        """
        This method use to input mail
        Args:
            mail(str): email address
        """
        self.input_text(self.mail, mail)

    def click_clear(self):
        """
        This method use to click clear button
        """
        self.click_element(self.btn_clear)

    def click_back(self):
        """
        This method use to click back button
        """
        self.click_element(self.btn_back)

    def click_calculate(self):
        """
        This method use to click calculate button
        """
        element = self.get_element(self.btn_calculate, 'css')
        if self.is_visible(element):
            self.click_element(self.btn_calculate)
        else:
            INFO("Calculate button is disable")

    def select_measurement_unit(self, unit):
        """
        Select the measurement option (m-kg/inch-lb).
        Args:
        measurement(str): One of 'm-kg', 'inch-lb',.

        """
        INFO('Select unit from measurement dropdown')
        if self.waiting_for_element_visible(self.measurement_dropdown,
                                            By.CSS_SELECTOR):
            time.sleep(self.SLEEP_TIME)
            self.click_element(self.measurement_dropdown)
            self.click_element(unit)

    def check_invalid_input_length(self):
        """
        Check if input invalid length
        """
        error_input = self.get_element_from_css(self.length).get_attribute('class')
        if 'input-error' in error_input:
            return True
        return False

    def check_invalid_input_width(self):
        """
        Check if input invalid width
        """
        error_input = self.get_element_from_css(self.width).get_attribute('class')
        if 'input-error' in error_input:
            return True
        return False

    def check_invalid_input_height(self):
        """
        Check if input invalid height
        """
        error_input = self.get_element_from_css(self.height).get_attribute('class')
        if 'input-error' in error_input:
            return True
        return False

    def check_invalid_input_weight(self):
        """
        Check if input invalid weight
        """
        error_input = self.get_element_from_css(self.weight).get_attribute('class')
        if 'input-error' in error_input:
            return True
        return False

    def check_invalid_input_quantity(self):
        """
        Check if input invalid quantity
        """
        error_input = self.get_element_from_css(self.quantity).get_attribute('class')
        if 'input-error' in error_input:
            return True
        return False

    def sign_up_after_get_instant_quote(self):
        """
        Click sign-up to get better price
        """
        self.click_element(self.instant_quote_sign_up)
