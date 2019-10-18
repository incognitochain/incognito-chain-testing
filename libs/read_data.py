"""
Created 28 Sep 2018

@Author: Van.Vo
"""
import csv


def get_csv_data(file_name):
    """
    This method use to get data from csv file
    Args:
        file_name: name of file.
    Returns:
        rows
    """
    rows = []
    data_file = open(file_name, "r")
    reader = csv.reader(data_file)
    next(reader)
    for row in reader:
        rows.append(row)
    return rows
