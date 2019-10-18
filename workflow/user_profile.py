"""
Created Nov 15 2018

@Author: Van Vo
"""
from Automation.libs.swlog import INFO, wait_time
from Automation.pages.user_profile.base_user_profile import BaseUserProfile


class UserProfile(BaseUserProfile):
    """
    Workflow for user profile
    """
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    def edit_business_account_info(self, new_name, new_phone,
                                   new_company_name, new_uen):
        """
        Edit business account info
        """
        # Click edit information button
        self.click_edit_information()
        # Input new full name
        self.input_new_name(new_name)
        # Input new mobile phone
        self.input_new_phone(new_phone)
        # Input new company name
        self.input_new_company_name(new_company_name)
        # Input new business uen
        self.input_new_business_uen(new_uen)
        # Click save change
        self.click_save_change_account_info()

    def edit_client_account_info(self, new_name, new_phone):
        """
        Edit client account info
        """
        # Click edit information button
        self.click_edit_information()
        # Input new full name
        self.input_new_name(new_name)
        # Input new mobile phone
        self.input_new_phone(new_phone)
        # Click save change
        self.click_save_change_account_info()

    def verify_business_account_information(self, name, phone, company_name, uen):
        """
        Verify information of business account.
        """
        expected_name = self.get_name_from_field()
        if expected_name != name:
            raise Exception("Invalid field name, Expected is: %s" % name)
        else:
            INFO("Got expected name.")

        expected_phone_number = self.get_phone_number_from_field()
        if expected_phone_number != phone:
            raise Exception("Invalid field phone number, Expected is: %s" % phone)
        else:
            INFO("Got expected phone number.")

        expected_company_name = self.get_company_name_from_field()
        if expected_company_name != company_name:
            raise Exception("Invalid field company name, Expected is: %s" % company_name)
        else:
            INFO("Got expected company name.")

        expected_uen = self.get_uen_from_field()
        if expected_uen != uen:
            raise Exception("Invalid field business uen, Expected is: %s" % uen)
        else:
            INFO("Got expected company name.")

    def verify_client_account_information(self, name, phone):
        """
        Verify information of business account.
        """
        expected_name = self.get_name_from_field()
        if expected_name != name:
            raise Exception("Invalid field name, Expected is: %s" % name)
        else:
            INFO("Got expected name.")

        expected_phone_number = self.get_phone_number_from_field()
        if expected_phone_number != phone:
            raise Exception("Invalid field phone number, Expected is: %s" % phone)
        else:
            INFO("Got expected phone number.")

    def change_account_password(self, current_password,
                                new_password, confirm_password, click=True):
        """
        Change password at account information
        """
        # Click change password
        self.click_change_password()
        # Input current password
        self.input_current_password(current_password)
        # Input new password
        self.input_new_password(new_password)
        # Input confirm new password
        self.input_confirm_new_password(confirm_password)
        # Click change password button
        if click:
            self.click_save_change_new_password()
        wait_time(3)

    def verify_error_message_with_wrong_current_password(self, expected_msg):
        """
         Verify error message is display when change password with wrong current password
        """
        actual_err_msg = self.get_err_msg_input_wrong_current_pass()
        if actual_err_msg != expected_msg:
            raise Exception("Unexpected error message, It should be: %s" % expected_msg)
        else:
            INFO("Expected error message \"%s\" is display" % expected_msg)

    def verify_error_message_with_inconsistent_new_password(self, expected_msg):
        """
         Verify error message is display when change password with inconsistent new password
        """
        actual_err_msg = self.get_err_msg_input_inconsistent_new_pass()
        if actual_err_msg != expected_msg:
            raise Exception("Unexpected error message, It should be: %s" % expected_msg)
        else:
            INFO("Expected error message \"%s\" is display" % expected_msg)

    def verify_email_is_displayed_in_account_infor(self, email):
        """
        Verify email is displayed in account information
        """
        actual_email = self.get_email_from_field()
        if actual_email != email:
            raise Exception("Unexpected email: %s, It should be: %s" % (actual_email, email))
        else:
            INFO("Expected email \"%s\" is display" % email)

    def verify_password_is_covered_in_account_infor(self):
        """
        Verify password is covered in account information
        """
        password_type = self.get_password_attribute()
        if password_type != "password":
            raise Exception("Password in account information page should be covered")
        else:
            INFO("Password in account information page is covered as expected")

    def add_new_address(self, name, phone_number, address ,city, post_code):
        """
        This method use to add new address to address book
        """
        # Click add new address button
        self.click_add_new_contact()
        # Input contact name
        self.input_contact_name(name)
        # Input phone number
        self.input_contact_phone(phone_number)
        # Input address
        self.input_contact_address(address)
        # Input city
        self.input_contact_city(city)
        # Input post code
        self.input_contact_post_code(post_code)
        # Click add button
        self.click_contact_save_button()
        wait_time(2)

    def verify_address_is_added(self):
        """
        Verify address is added to address book successfully
        """
        number_add_before = self.get_all_number_address_book()
