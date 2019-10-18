"""
Module to get the web driver instance
@Author: Van.Vo

"""
import os
from selenium import webdriver
from Automation.libs.swlog import INFO


class WebDriverFactory():

    def __init__(self, browser):
        """
        Inits WebDriverFactory class

        Returns:
            None
        """
        self.browser = browser

    def get_web_driver_instance(self, base_url):
        """
       Get WebDriver Instance based on the browser configuration

        Returns:
            'WebDriver Instance'
        """
        if self.browser == "ie":
            ie_driver = "driver/IEDriverServer.exe"
            os.environ["webdriver.ie.driver"] = ie_driver
            driver = webdriver.Ie(ie_driver)
        elif self.browser == "me":
            me_driver = "driver/MicrosoftWebDriver.exe"
            os.environ["webdriver.edge.driver"] = me_driver
            driver = webdriver.Edge(me_driver)
        elif self.browser == "firefox" or self.browser == 'ff':
            driver = webdriver.Firefox()
        elif self.browser == "chrome" or self.browser == 'gc':
            driver = webdriver.Chrome()
        else:
            driver = webdriver.Chrome()
        # Setting Driver Implicit Time out for An Element
        INFO("Set implicitly wait to 3.")
        driver.implicitly_wait(3)
        # Maximize the window
        driver.maximize_window()
        # Loading browser with App URL
        driver.delete_all_cookies()
        driver.get(base_url)
        return driver
