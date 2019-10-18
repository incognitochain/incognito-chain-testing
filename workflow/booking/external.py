"""
Created Dec 24 2018

@Author: Van.Vo
"""
from Automation.pages.booking.base_external import BaseBookingExternal


class BookingExternal(BaseBookingExternal):
    """
    Booking external workflow
    """
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    def add_shipment_name(self, shipment_name):
        """
        Add shipment name
        """
        self.input_shipment_name(shipment_name)

    def input_dimension(self, weight, width, height, length, quantity):
        """
        Input dimension
        """
        self.input_product_weight(weight)
        self.input_product_width(width)
        self.input_product_height(height)
        self.input_product_length(length)
        self.input_product_quantity(quantity)

    def input_product_information(self):
        """
        Input product information
        """
