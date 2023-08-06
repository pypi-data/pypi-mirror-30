"""
Author: Aaron Anthony Valoroso
Date: March 30th, 2018
License: BSD-3-Clause
Email: valoroso99@gmail.com
"""
from html.parser import HTMLParser
from html.entities import name2codepoint

class TheParser(HTMLParser):
    """
        Overview: This class is meant for parsing HTML code and getting the specific data out of certian tags.
    """
    def __init__(self):
        super().__init__()
        self.my_list = []


    def handle_starttag(self, tag, attrs):
        """
            Overview: This mehtod loops through all the attributes looking for anything that has a decimal in 
            the attribute. Why I am looking for a decimal is because the parent directorys of NCEP 
            have a decmial in it, and no other attribute does.

            Returning: None
        """
        my_list = []
        for attr in attrs:
            my_string = str(attr)
            if my_string.find(".") > 0:
                self.my_list.append(my_string)


    def get_list(self):
        """
            Overview: This method returns the list of data that was gathered by the methods below.

            Returning: List
        """
        return self.my_list


    def get_product_formats(self):
        """
            Overview: This method returns a list formats of what data is being held by a specific date within NCEP.
            What I mean by this is when in the product inventory for GFS, there are parent directories
            that look like the following: gfs.20180220, gdas.20180220 and so forth. The first part is
            what this method is returning.

            Returning: List
        """
        formats = []
        for item in self.my_list:
            identifier, link = item.split(",")
            extension, date = link.split(".")
            cleaned_extension = extension.replace("'", "").replace(" ", "")
            if cleaned_extension not in formats:
                formats.append(cleaned_extension)

        return formats


    def get_product_data_dates(self):
        """
            Overview: This method returns a list of dates avaliable for the whole parent directory of prooduct formats
            and dates. The dates are when the data was gathered.

            Returning: List
        """
        dates = []
        for item in self.my_list:
            identifier, link = item.split(",")
            extension, date = link.split(".")
            cleaned_date = date.replace("/", "").replace(")", "").replace("'","")
            if len(cleaned_date) > 8:
                cleaned_date = cleaned_date[:-2]
            if cleaned_date not in dates:
                dates.append(cleaned_date)

        return dates


    def our_reset(self):
        """
            Overview: This method resets the list so we can gather new information and not have the old.

            Returning: None
        """
        self.my_list = []
        