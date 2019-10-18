"""
Created Dec 11 2018

@Author: Van.Vo
"""
import time
import datetime
from datetime import timedelta
from Automation.libs.swlog import INFO, DEBUG, wait_time
from selenium.webdriver.common.by import By
from Automation.pages.base_page import BasePage


class BaseBookingExternal(BasePage):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        # Locator for booing shipment external page
        self.my_shipment_tab = "[data-test='header_my-shipment']"
        self.booking_shipment_tab = "[data-test='header_book-a-shipment']"
        self.add_shipment_name = "[data-test='add-shipment-name']"
        self.shipment_name = "[data-test='shipment-name'] input"
        self.picker_date = "[data-test='date-picker-click']"
        self.freight_service = "[data-test='select-service-shipment-click']"
        self.add_product = "[data-test='add-product']"
        self.product_name = "[data-test='form-shipment-product-name'] input"
        self.product_weight = "[data-test='info-cbm-weight'] input"
        self.product_width = "[data-test='info-cbm-width'] input"
        self.product_height = "[data-test='info-cbm-height'] input"
        self.product_length = "[data-test='info-cbm-length'] input"
        self.product_quantity = "[data-test='form-shipment-quantity'] input"
        self.unit_price = "[data-test='form-shipment-prince'] input"
        self.product_photo = "[data-test='form-shipment-photo-item']/[data-test='photo-add']"
        self.supplier_photo = "[data-test='form-shipment-spplier-invoice']/[data-test='photo-add']"
        self.supplier_info = "[data-test='form-shipment-supplier-info'] input"
        self.contact_person = "[data-test='form-shipment-contact-persion'] input"
        self.contact_phone = "[data-test='form-shipment-phone-number'] input"
        self.license_no = "[data-test='form-shipment-have-license-no'] span"
        self.license_yes = "[data-test='form-shipment-have-license-yes'] span"

        self.save_product = "[data-test='product-done']"
        self.cancel_product = "[data-test='product-cancel']"
        self.save_shipment = "[data-test='detail-bacsic-shipment-save']"
        self.submit_shipment = "[data-test='detail-bacsic-shipment-save-and-request']"
        self.cancel_shipment = "[data-test='detail-bacsic-shipment-cancel']"

    def click_add_shipment_name(self):
        """
        Click add shipment name
        """
        self.click_element(self.add_shipment_name)

    def input_shipment_name(self, shipment_name):
        """
        Input shipment name
        """
        self.input_text(self.shipment_name, shipment_name)

    @staticmethod
    def get_drop_off_day():
        """
        Get drop off day
        """
        current_date = datetime.datetime.now()
        drop_off_day = current_date.day
        return str(drop_off_day)

    @staticmethod
    def get_pick_up_day(number_day=24):
        """
        Get drop off day
        """
        if number_day < 24:
            raise Exception("Number day must be >= 24")
        else:
            current_date = datetime.datetime.now()
            expected_date = current_date + datetime.timedelta(days=number_day)
            pick_up_day = expected_date.day
            return str(pick_up_day)

    def click_drop_off_option(self):
        """
        Click drop off at warehouse or freightknot service
        """
        elements = [b for b in self.get_all_elements_from_css(self.freight_service) if b.is_displayed()]
        if elements:
            elements[0].click()
        else:
            message = "No visible link with text found"
            DEBUG(message)

    def click_pick_up_option(self):
        """
        Click pick up at warehouse or freightknot service
        """
        elements = [b for b in self.get_all_elements_from_css(self.freight_service) if b.is_displayed()]
        if elements:
            elements[1].click()
        else:
            message = "No visible link with text found"
            DEBUG(message)

    def select_drop_off_option(self, text):
        """
        Choose drop off at warehouse or freightknot service
        """
        xpath = "//*[text()[contains(., '%s')]]" % text
        self.click_drop_off_option()
        text = self.driver.find_element_by_xpath(xpath)
        if text:
            text.click()
        else:
            message = "No visible option %s found" % text
            DEBUG(message)

    def select_pick_up_option(self, text):
        """
        Choose pick up at warehouse or freightknot service
        """
        xpath = "//*[text()[contains(., '%s')]]" % text
        self.click_pick_up_option()
        text = self.driver.find_element_by_xpath(xpath)
        if text:
            text.click()
        else:
            message = "No visible option %s found" % text
            DEBUG(message)

    def click_drop_off_date_picker(self):
        """
        click drop off date picker
        """
        elements = [b for b in self.get_all_elements_from_css(self.picker_date) if b.is_displayed()]
        if elements:
            elements[0].click()
        else:
            message = "No visible link with text found"
            DEBUG(message)

    def click_pick_up_date_picker(self):
        """
        click pick_up date picker
        """
        elements = [b for b in self.get_all_elements_from_css(self.picker_date) if b.is_displayed()]
        if elements:
            elements[1].click()
        else:
            message = "No visible link with text found"
            DEBUG(message)

    def choose_drop_off_day(self):
        """
        Choose drop off day
        """
        self.click_drop_off_date_picker()
        wait_time(1)
        day = self.get_drop_off_day()
        drop_off_day = \
            self.get_element_from_xpath("//*[contains(text(), '%s')]" % day)
        if drop_off_day.is_display():
            drop_off_day.click()
        else:
            raise Exception("There is no day %s" % drop_off_day)

    def choose_pick_up_day(self):
        """
        Choose pick up day
        """
        self.click_pick_up_date_picker()
        wait_time(1)
        day = self.get_pick_up_day(number_day=24)
        pick_up_day = \
            self.get_element_from_xpath("//*[contains(text(), '%s')]" % day)
        if pick_up_day.is_display():
            pick_up_day.click()
        else:
            raise Exception("There is no day %s" % pick_up_day)

    def click_license(self, import_license='no'):
        """
        Click to import license
        """
        if import_license == 'no':
            self.click_element(self.license_no)
        elif import_license == 'yes':
            self.click_element(self.license_yes)

    def input_product_name(self, product_name):
        """
        Input product name
        """
        self.input_text(self.product_name, product_name)

    def input_product_weight(self, product_weight):
        """
        Input product weight
        """
        self.input_text(self.product_weight, product_weight)

    def input_product_width(self, product_width):
        """
        Input product weight
        """
        self.input_text(self.product_width, product_width)

    def input_product_height(self, product_height):
        """
        Input product height
        """
        self.input_text(self.product_height, product_height)

    def input_product_length(self, product_length):
        """
        Input product length
        """
        self.input_text(self.product_length, product_length)

    def input_product_quantity(self, product_quantity):
        """
        Input product quantity
        """
        self.input_text(self.product_quantity, product_quantity)

    def input_unit_price(self, unit_price):
        """
        Input product price
        """
        self.input_text(self.unit_price, unit_price)

    def input_supplier_info(self, supplier_info):
        """
        Input supplier information
        """
        self.input_text(self.supplier_info, supplier_info)

    def input_contact_person(self, contact_person):
        """
        Input contact person
        """
        self.input_text(self.contact_person, contact_person)

    def input_contact_phone(self, contact_phone):
        """
        Input contact phone
        """
        self.input_text(self.contact_person, contact_phone)

    def save_shipment_without_submit(self):
        """
        Save shipment without submit
        """
        self.click_element(self.save_shipment)

    def submit_shipment(self):
        """
        Submit shipment
        """
        self.click_element(self.submit_shipment)

    def cancel_shipment(self):
        """
        Cancel booking shipment
        """
        self.click_element(self.cancel_shipment)

    def add_product_photo(self, path):
        """
        Add product photo
        """
        self.upload_file(self.product_photo, path)

    def add_supplier_invoice_photo(self, path):
        """
        Add supplier invoice photo
        """
        self.upload_file(self.supplier_photo, path)

    def click_my_shipment_tab(self):
        """
        Click my shipment tab
        """
        self.click_element(self.my_shipment_tab)

    def click_booking_shipment_tab(self):
        """
        Click booking shipment tab
        """
        self.click_element(self.booking_shipment_tab)


