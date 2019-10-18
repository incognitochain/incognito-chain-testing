"""
Created Nov 12

@Author: Van Vo
"""
from selenium.webdriver.common.by import By

import re
from Automation.libs.swlog import wait_time, INFO, DEBUG
from Automation.pages.base_page import BasePage


class BaseUserProfile(BasePage):
    """
    class user profile
    """
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        # Locators for user profile
        self.menu_user = "[data-test='menu-bar-user']"
        self.menu_my_account = "[data-test='menu-bar-user-my-account']"
        self.menu_address_book = "[data-test='menu-bar-user-address-book']"
        self.menu_log_out = "[data-test='menu-bar-user-logout']"
        self.my_account_tab = "[data-test='profile-menu-tabs-my-account']"
        self.address_book_tab = "[data-test='profile-menu-tabs-address-book']"
        self.account_email = "[data-test='basic-info-account-email'] input"
        self.account_password = "[data-test='basic-info-account-password'] input"

        self.change_avatar = "[data-test='basic-info-account-change-avantar'] img"
        self.avatar = "[data-test='basic-info-account-avantar']"
        self.back_home = ""
        self.change_password = "[data-test='login-info-change-password']"
        self.old_password = "[data-test='basic-info-account-old-password'] input"
        self.new_password = "[data-test='basic-info-account-new-password'] input"
        self.confirm_new_password = "[data-test='basic-info-account-re-password'] input"

        self.edit_information = "[data-test='ganeral-info-account-edit']"
        self.edit_name = "[data-test='ganeral-info-account-name'] input"
        self.edit_phone = "[data-test='ganeral-info-account-phone'] input"
        self.edit_company_name = "[data-test='ganeral-info-account-companyName'] input"
        self.edit_business_uen = "[data-test='ganeral-info-account-businessUEN'] input"

        self.change_pass_cancel_btn = "[data-test='basic-info-account-cancel']"
        self.change_pass_save_btn = "[data-test='basic-info-account-save']"

        self.edit_info_cancel_btn = "[data-test='ganeral-info-account-cancel']"
        self.edit_info_save_btn = "[data-test='ganeral-info-account-save']"
        self.change_password_error_msg = "[data-test='reset-password_mess-new-password']"
        self.change_password_error_msg_inconsistent = "[data-test='reset-password_mess-re-password']"

        self.contact_add_new = "[data-test='address-book-menu-add']"
        self.contact_name = "[data-test='address-name'] input"
        self.contact_phone = "[data-test='address-phone'] input"
        self.contact_address = "[data-test='address-address'] input"
        self.contact_city = "[data-test='address-city'] input"
        self.contact_post_code = "[data-test='address-post-code'] input"
        self.contact_cancel_btn = "[data-test='address-cancel']"
        self.contact_create_btn = "[data-test='address-ok']"
        self.contact_all_address = "[data-test='address-book-menu-all']"

        self.edit_contact = "[data-test='address-book-item-edit']"

        self.delete_contact = "[data-test='address-book-item-delete']"
        self.confirm_del_contact = "[data-test='address-book-delete-conform-dalete']"
        self.show_password = "div[class*='show-password-icon']"

    def go_to_my_account_from_menu_user(self):
        """
        Go to My Account from menu bar user
        """
        # Move mouse to User name
        self.move_mouse(self.menu_user)
        wait_time(1)
        # Move mouse to My Account and click
        self.move_mouse(self.menu_my_account, click=True)

    def go_to_address_book_from_menu_user(self):
        """
        Go to Address Book from menu bar user
        """
        # Move mouse to User name
        self.move_mouse(self.menu_user)
        wait_time(1)
        # Move mouse to Address Book and click
        self.move_mouse(self.menu_address_book, click=True)

    def log_out(self):
        """
        Log out
        """
        # Move mouse to User name
        self.move_mouse(self.menu_user)
        wait_time(1)
        # Move mouse to Logout and click
        self.move_mouse(self.menu_log_out, click=True)

    def click_my_account_tab(self):
        """
        Click my account tab
        """
        self.click_element(self.my_account_tab)

    def click_address_book_tab(self):
        """
        Click address book tab
        """
        self.click_element(self.address_book_tab)

    # def change_avatar_profile(self, image_path):
    #     """
    #     Change avatar for user profile
    #     """
    #     change_avatar = self.get_element_from_css(self.change_avatar)
    #     wait_time(5)
    #     change_avatar.send_keys(image_path)

    def click_change_password(self):
        """
        Click change password at my account
        """
        self.click_element(self.change_password)

    def click_edit_information(self):
        """
        Click edit information at my account
        """
        self.click_element(self.edit_information)

    def input_current_password(self, password):
        """
        Input current password
        """
        self.input_text(self.old_password, password)

    def input_new_password(self, password):
        """
        Input new password
        """
        self.input_text(self.new_password, password)

    def input_confirm_new_password(self, password):
        """
        Input confirm new password
        """
        self.input_text(self.confirm_new_password, password)

    def click_save_change_new_password(self):
        """
        Click to save new password
        """
        self.click_element(self.change_pass_save_btn)

    def input_new_name(self, name):
        """
        Input new name
        """
        self.input_text(self.edit_name, name)

    def input_new_phone(self, phone):
        """
        Input new phone number
        """
        self.input_text(self.edit_phone, phone)

    def input_new_company_name(self, company_name):
        """
        Input new company name
        """
        self.input_text(self.edit_company_name, company_name)

    def input_new_business_uen(self, business_uen):
        """
        Input new business uen
        """
        self.input_text(self.edit_business_uen, business_uen)

    def click_save_change_account_info(self):
        """
        Click save change new information
        """
        self.click_element(self.edit_info_save_btn)

    def click_add_new_contact(self):
        """
        Click add new contact
        """
        self.click_element(self.contact_add_new)

    def input_contact_name(self, name):
        """
        Input address name
        """
        self.input_text(self.contact_name, name)

    def input_contact_phone(self, address_phone):
        """
        Input address phone
        """
        self.input_text(self.contact_phone, address_phone)

    def input_contact_address(self, address):
        """
        Input address
        """
        self.input_text(self.contact_address, address)

    def input_contact_city(self, city):
        """
        Input city
        """
        self.input_text(self.contact_city, city)

    def input_contact_post_code(self, post_code):
        """
        Input post code
        """
        self.input_text(self.contact_post_code, post_code)

    def click_contact_cancel_button(self):
        """
        Click cancel button at add address popup
        """
        self.click_element(self.contact_cancel_btn)

    def click_contact_save_button(self):
        """
        Click save button at add address popup
        """
        self.click_element(self.contact_create_btn)

    def click_edit_contact(self):
        """
        Click edit contact
        """
        self.click_element(self.edit_contact)

    def delete_last_contact(self):
        """
        Delete contact
        """
        # Get all contact
        elements = self.get_all_elements_from_css(self.delete_contact)
        DEBUG("elements: %s" % elements)
        if len(elements) == 0:
            raise Exception("The address book is empty !!!")
        else:
            DEBUG("element: %s" % elements[-1])
            # Click delete button
            elements[-1].click()
            # Confirm delete
            self.click_element(self.confirm_del_contact)
            wait_time(2)

    def get_name_from_field(self):
        """
        Get name from input field
        """
        name = self.get_element_from_css(self.edit_name).get_attribute('value')
        return name

    def get_phone_number_from_field(self):
        """
        Get phone number from input field
        """
        phone_number = self.get_element_from_css(self.edit_phone).get_attribute('value')
        return phone_number

    def get_company_name_from_field(self):
        """
        Get company name from input field
        """
        company_name = self.get_element_from_css(self.edit_company_name).get_attribute('value')
        return company_name

    def get_uen_from_field(self):
        """
        Get business uen from input field
        """
        business_uen = self.get_element_from_css(self.edit_business_uen).get_attribute('value')
        return business_uen

    def show_password_field(self):
        """
        Show password
        """
        self.click_element(self.show_password)

    def get_err_msg_input_wrong_current_pass(self):
        """
        Get error message when change password with wrong current password
        """
        err_msg = self.get_text_if_present(self.change_password_error_msg)
        return err_msg

    def get_err_msg_input_inconsistent_new_pass(self):
        """
        Get error message when change password with inconsistent new password
        """
        err_msg = self.get_text_if_present(self.change_password_error_msg_inconsistent)
        return err_msg

    def get_email_from_field(self):
        """
        Get email from input field
        """
        email = self.get_element_from_css(self.account_email).get_attribute('value')
        return email

    def get_password_attribute(self):
        """
        Get  password attribute at account information
        """
        password_type = self.get_element_from_css(self.account_password).get_attribute('type')
        return password_type

    def change_profile_avatar(self, file_path):
        """
        Use to change avatar for user profile
        """
        # Move mouse to default avatar
        self.move_mouse(self.avatar)
        # Change avatar
        self.upload_file(self.change_avatar, file_path)

    def get_all_number_address_book(self):
        """
        Get number address book
        """
        element = self.contact_all_address + " p"
        number_address_text = self.get_text_if_present(element)
        regex_number = re.compile(r"^All\s\((\d+)\)")
        number_address = regex_number.search(number_address_text).group(1)
        # number_address = number_address.group(1)
        DEBUG("Number all addresses are: %s" % number_address)
        return int(number_address)
