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


    def our_reset(self):
        """
            Overview: This method resets the list so we can gather new information and not have the old.

            Returning: None
        """
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


    def get_all_product_data(self):
        """
            Overview: This method loops through the entire list of files for a given product format and date.
            I create a dictionary that has the product format as the key and a list of six character
            long date as the value. Why I need this is because I have to know which date associates
            too what data format.

            Returning: Dictionary
        """
        dictionary = {}
        for item in self.my_list:
            identifier, link = item.split(",")
            extension, date = link.split(".")
            cleaned_date = date.replace("/", "").replace(")", "").replace("'","")
            cleaned_extension = extension.replace("'", "").replace(" ", "")
            if cleaned_extension in dictionary:
                dictionary[cleaned_extension].append(cleaned_date)
            else:
                dictionary[cleaned_extension] = []
                dictionary[cleaned_extension].append(cleaned_date)
            
        return dictionary


    def get_list(self):
        """
            Overview: This method returns the list of data that was gathered by the methods below.

            Returning: List
        """        
        return self.my_list
        