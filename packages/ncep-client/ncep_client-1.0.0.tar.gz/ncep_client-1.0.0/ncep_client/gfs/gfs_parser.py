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

    
    def get_all_product_data(self):

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