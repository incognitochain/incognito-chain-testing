"""
Created Oct 2 2018

@Author: Van.Vo
"""
from Automation.pages.instant_quote.base_instant_quote_popup import \
    BaseInstantQuotePopup
from Automation.pages.base_page import BasePage
from Automation.libs.swlog import INFO, wait_time


class InstantQuotePopup(BaseInstantQuotePopup):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.WAIT_TIME =3
        self.base = BasePage(self.driver)
        self.title = "div[class='title']"
        self.result_price = "[data-test='get-instant-quote_results-price']"
        self.result_msg = "[data-test='get-instant-quote_results-mess']"
        self.msg_invalid_mail = "[data-test='get-instant-quote_input-email-mess']"

    def get_instant_quote_title(self):
        """
        Get Instant quote title
        """
        element = self.base.get_element_from_css(self.title)
        return element.text

    def get_instant_quote(self, unit, length, width,
                          height, weight, quantity, email,
                          click_cal=True):
        """
        This method use to calculate instant quote
        """
        instant_quote_pop = BaseInstantQuotePopup(self.driver)
        INFO("Choose unit for measurement.")
        instant_quote_pop.select_measurement_unit(unit)
        INFO("Input length.")
        instant_quote_pop.input_length(length)
        INFO("Input width.")
        instant_quote_pop.input_width(width)
        INFO("Input height.")
        instant_quote_pop.input_height(height)
        INFO("Input weight.")
        instant_quote_pop.input_weight(weight)
        INFO("Input quantity.")
        instant_quote_pop.input_quantity(quantity)
        INFO("Input email.")
        instant_quote_pop.input_mail(email)
        if click_cal:
            INFO("Click Calculate.")
            instant_quote_pop.click_calculate()
        wait_time(self.WAIT_TIME)

    @staticmethod
    def calculate_estimated_price(length, width, height, quantity):
        """
        Calculate estimated price.
        """
        INFO("Calculate estimated price.")
        cbm = length*width*height
        estimated_price = round(cbm*quantity*160, 2)
        return str(estimated_price)

    def get_instant_quote_results_price(self):
        """
        Get instant quote result price.
        """
        element = self.base.get_element_from_css(self.result_price)
        result_text = element.text
        result_price = result_text.replace("$", "")
        return result_price.strip()

    def get_instant_quote_results_message(self):
        """
        Get instant quote result message.
        """
        element = self.base.get_element_from_css(self.result_msg)
        return element.text

    def is_calculate_button_enable(self):
        """
        Check if calculate button is enabled
        """
        element = self.base.get_element_from_css(self.btn_calculate)
        if not element:
            return False
        return element.is_enabled()

    def is_clear_button_enable(self):
        """
        Check if clear button is enable
        """
        element = self.base.get_element_from_css(self.btn_clear).get_attribute('class')
        if 'disabled' in element:
            return False
        return True

    def clear_instant_quote_field(self, field):
        """
        Clear dimension value.
        """
        if field == 'length':
            ele = self.base.get_element_from_css(self.length)
            ele.clear()
        elif field == 'height':
            ele = self.base.get_element_from_css(self.height)
            ele.clear()
        elif field == 'width':
            ele = self.base.get_element_from_css(self.width)
            ele.clear()
        elif field == 'weight':
            ele = self.base.get_element_from_css(self.weight)
            ele.clear()
        elif field == 'quantity':
            ele = self.base.get_element_from_css(self.quantity)
            ele.clear()
        elif field == 'mail':
            ele = self.base.get_element_from_css(self.mail)
            ele.clear()
        elif field == 'clear':
            self.click_clear()

    def get_invalid_email_error(self, email):
        """
        Get in valid email error
        """
        instant_quote_pop = BaseInstantQuotePopup(self.driver)
        instant_quote_pop.input_mail(email)
        error_msg = self.get_text_if_present(self.msg_invalid_mail)
        return error_msg

    def enter_dimension_value(self, field, value):
        """
        Enter value for dimension
        """
        if field == 'length':
            self.input_length(value)
        elif field == 'height':
            self.input_height(value)
        elif field == 'width':
            self.input_width(value)
        elif field == 'weight':
            self.input_weight(value)
        elif field == 'quantity':
            self.input_quantity(value)
        elif field == 'mail':
            self.input_mail(value)

    def check_dimension_input_error(self, _type):
        """
        Check if dimension value is input invalid or not
        """
        result = False
        if _type == 'length':
            result = self.check_invalid_input_length()
        elif _type == 'width':
            result = self.check_invalid_input_width()
        elif _type == 'height':
            result = self.check_invalid_input_height()
        elif _type == 'quantity':
            result = self.check_invalid_input_quantity()
        elif _type == 'weight':
            result = self.check_invalid_input_weight()
        return result




