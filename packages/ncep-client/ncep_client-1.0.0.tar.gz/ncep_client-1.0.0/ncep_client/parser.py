from html.parser import HTMLParser
from html.entities import name2codepoint

class TheParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.my_list = []


    def our_reset(self):
        self.my_list = []


    def get_list(self):
        return self.my_list


    def handle_starttag(self, tag, attrs):

        my_list = []
        # print("Start tag:", tag)
        for attr in attrs:
            # print("     attr:", attr)
            my_string = str(attr)
            if my_string.find(".") > 0:
                self.my_list.append(my_string)


    def get_product_formats(self):

        formats = []
        for item in self.my_list:
            identifier, link = item.split(",")
            extension, date = link.split(".")
            cleaned_extension = extension.replace("'", "").replace(" ", "")
            if cleaned_extension not in formats:
                formats.append(cleaned_extension)

        return formats


    def get_product_data_dates(self):

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