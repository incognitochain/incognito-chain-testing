"""
Created 25 Sep 2018

@Author: Van.Vo
"""
from Automation.libs.swlog import DEBUG, wait_time
from Automation.util.webdriverfactory import WebDriverFactory
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains


class BasePage(object):
    def __init__(self, driver):
        self.timeout = 10
        self.driver = driver

    def maximize_window(self):
        """Maximize the browser window

        Returns:
          None
        """
        self.driver.maximize_window()

    def get_title(self):
        """
        Get page title.
        """
        return self.driver.title

    def input_text(self, css_locator, text):
        """Enter text into the field by css

        Args:
          css_locator(obj): WebDriver element.
          text(str): the text to enter.
        """
        if self.waiting_for_element_visible(css_locator, By.CSS_SELECTOR):
            DEBUG("Input %s to the text box" % text)
            textbox = self.driver.find_element(By.CSS_SELECTOR, css_locator)
            textbox.clear()
            wait_time(1)
            textbox.send_keys(text)
        else:
            msg = "Failed to fill '%s' to field %s" % (text, css_locator)
            raise Exception(msg)

    def input_text_by_xpath(self, xpath_locator, text):
        """Enter text into the field by xpath

        Args:
          xpath_locator(obj): WebDriver element.
          text(str): the text to enter.
        """
        if self.waiting_for_element_loaded(xpath_locator, By.XPATH):
            DEBUG("Input %s to the %s" % (text, xpath_locator))
            textbox = self.driver.find_element(By.XPATH, xpath_locator)
            textbox.clear()
            textbox.send_keys(text)
        else:
            msg = "Failed to fill '%s' to field %s" % (text, xpath_locator)
            DEBUG(msg)

    def get_element_from_xpath(self, xpath):
        """Returns elements locator using xpath.

        Args:
          xpath(str): xpath to use for lookup.

        Returns:
          obj(List): selenium web elements.
        """
        return self.driver.find_element_by_xpath(xpath)

    def get_all_elements_from_xpath(self, xpath):
        """Returns elements locator using xpath.

        Args:
          xpath(str): xpath to use for lookup.

        Returns:
          obj(List): selenium web elements.
        """
        return self.driver.find_elements_by_xpath(xpath)

    def get_element_from_css(self, css):
        """Gets an element locator using css.

        Args:
          css(str): css to use for lookup.

        Returns:
          obj: selenium web element.
        """
        return self.driver.find_element_by_css_selector(css)

    def get_all_elements_from_css(self, css):
        """Returns elements locator using css selector

        Args:
          css(str): css to use for lookup.

        Returns:
          obj(List): selenium web elements.
        """
        return self.driver.find_elements_by_css_selector(css)

    def click_element(self, locator):
        """
        Clicks an element by element xpath
        """
        wait_time(2)
        if self.wait_for_element_clickable(locator, By.CSS_SELECTOR):
            DEBUG("Click on the element by css: %s" % locator)
            element = self.driver.find_element(By.CSS_SELECTOR, locator)
            element.click()
        else:
            msg = "Element %s is not click-able" % locator
            raise Exception(msg)

    def click_element_by_xpath(self, element):
        """
        Clicks an element by element xpath
        """
        if self.wait_for_element_clickable(element, By.XPATH):
            DEBUG("Click on the element by xpath: %s" % element)
            element = self.driver.find_element(By.XPATH, element)
            element.click()
        else:
            msg = "Element %s is not click-able" % element
            raise Exception(msg)

    def get_element(self, locator, type):
        """Returns element locator using expected type.

        Args:
          type(str): xpath to use for lookup.

        Returns:
          obj(List): selenium web elements.
        """
        if type == 'xpath':
            return self.get_element_from_xpath(locator)
        elif type == 'css':
            return self.get_element_from_css(locator)

    def get_all_elements(self, locator, type):
        """Returns all elements locator using expected type.

        Args:
            locator(str): locator to use for lookup.
            type(str): type use to lookup

        Returns:
            obj(List): selenium web elements.
        """
        if type == 'xpath':
            return self.get_all_elements_from_xpath(locator)
        elif type == 'css':
            return self.get_all_elements_from_css(locator)

    def waiting_for_element_loaded(self, condition, By):
        """
        Waits for the element is loaded
        Args:
            condition: locator
            By: 
        """
        result = False
        try:
            DEBUG("Wait for element %s loaded" % condition)
            wait = WebDriverWait(self.driver, self.timeout)
            element = wait.until(
                EC.presence_of_element_located((By, condition)))
            if element:
                result = True
        except Exception as e:
            DEBUG("Wait for element loaded exception: FAILED")
        return result

    def wait_for_element_clickable(self, condition, By, timeout=None):
        """
        Waits for the element is clickable
        """
        result = False
        try:
            DEBUG("Wait for element %s click-able" % condition)
            if not timeout:
                timeout = self.timeout
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable((By, condition)))
            if element:
                result = True
        except Exception as e:
            DEBUG("waiting element exception: FAILED")
        return result

    def waiting_for_element_visible(self, condition, By, timeout=None):
        """
        Waits for the element is visible
        """
        result = False
        try:
            DEBUG("Wait for element \"%s\" visible" % condition)
            if not timeout:
                timeout = self.timeout
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(
                EC.visibility_of_element_located((By, condition)))
            if element:
                result = True
        except Exception:
            msg = "Wait for element visible exception: FAILED"
            DEBUG(msg)
        return result

    @staticmethod
    def is_visible(locator):
        """
        Checks if the element is visible on the current page.
        Args:
          locator(obj): a WebDriver element
        Returns:
            bool: True if it is visible, False otherwise.
        """
        if not locator:
            return False
        return locator.is_displayed()

    def get_text_if_present(self, locator):
        """Returns the text of the element if present, None otherwise.

        Args:
            locator(obj): Element of Webdriver
        Returns:
            str: Text present inside element

        Raises:
            TimeoutException
        """
        if not self.waiting_for_element_visible(locator, By.CSS_SELECTOR):
            return None
        return self.get_element_from_css(locator).text

    @staticmethod
    def open_new_browser(browser, new_url):
        """
        Open new URL.
        """
        wdf = WebDriverFactory(browser)
        driver = wdf.get_web_driver_instance(new_url)
        return driver

    @staticmethod
    def close_browser(browser):
        """
        Close browser.
        """
        browser.quit()

    def current_window(self):
        """Returns the handle of the current window.

        Returns:
          object: Current window handle
        """
        return self.driver.current_window_handle

    def switch_to_window(self, window):
        """
        Switches to the window with the given handle.

        Args:
          window(obj): window handle of window to switch to.
        """
        self.driver.switch_to.window(window)

    def windows(self):
        """Returns a list of window handles.

        Returns:
          list: list of window handles.
        """
        return self.driver.window_handles

    def refresh_current_browser(self):
        """
        Refresh current browser
        """
        self.driver.refresh()
        wait_time(3)

    def go_to_dash_board(self):
        """
        Go to dashboard
        """
        dash_board = "div[class*='close-icon']"
        # self.click_element(dash_board)
        if self.waiting_for_element_visible(dash_board, By.CSS_SELECTOR):
            element = self.driver.find_element(By.CSS_SELECTOR, dash_board)
            element.click()
        else:
            DEBUG("You are in DashBoard !!!!")

    def move_mouse(self, locator, click=False):
        """
        Move mouse to element
        """
        action = ActionChains(self.driver)
        element = self.get_element_from_css(locator)
        move_to_element = action.move_to_element(element)
        if click:
            move_to_element.click().perform()
            wait_time(1)
        else:
            move_to_element.perform()
            wait_time(1)

    def upload_file(self, locator, file_path):
        """
        This method use to upload file
        """
        file_input = self.get_element_from_css(locator)
        file_input.send_keys(file_path)
