"""
Created Oct 10 2018

@Author: Van.Vo
"""
import time
from Automation.libs.swlog import INFO, DEBUG


class Utils(object):

    def __init__(self):
        pass

    @staticmethod
    def get_unique_name(prefix='sw_test'):
        """
        Adds timestamp to the entity name.
        """
        suffix = str(int(time.time()))[-4:]
        return "%s_%s" % (prefix, suffix)

    @staticmethod
    def get_table_records(driver):
        """
        Get Records for given Table Css
        Args:
          table_css(str): Css of the Table.
        Returns:
          list: List of table records.
        """
        table_records = []

        table_header_css = '.table thead tr th'
        table_headers = driver.find_elements_by_css_selector(table_header_css)
        INFO('Table HEADER: %s' % table_headers)
        columns = [str(col.text).upper() for col in table_headers]
        INFO('Table Columns: %s' % str(columns))

        table_rows_css = '.table tbody tr'
        INFO('Table ROW CSS: %s' % table_rows_css)
        table_rows = driver.find_elements_by_css_selector(table_rows_css)
        table_rows = [row for row in table_rows if str(row.text).strip()]

        for row in table_rows:
            INFO('ROW: %s' % str(row.text))

        for row_index, row in enumerate(table_rows):
            entity = dict()
            for col_index, col in enumerate(columns):
                css = '%s tbody tr:nth-child(%d) td:nth-child(%d)' % ('.table',
                                                                      row_index + 1,
                                                                      col_index + 1)
                element = driver.find_element_by_css_selector(css)
                element_text = str(element.text)
                DEBUG("Element text is : %s" % element_text)
                entity[col] = element_text
            table_records.append(entity)
        DEBUG("Table records : %s" % table_records)
        return table_records
