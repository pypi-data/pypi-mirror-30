from .gfs import GFS_Provider
from . import parser
import datetime
import requests
import os

class NCEP_Client():

    def __init__(self):
        self.main_parser = parser.TheParser()
        self.NCEP_BASE_SITE_URL = "http://www.nco.ncep.noaa.gov/pmb/products/"
        self.NCEP_BASE_FTP_URL = "http://www.ftp.ncep.noaa.gov/data/nccf/com/"
        # self.NCEP_PRODUCTS = {"Air Quality Model": "agm", "Climate Forecast System": "cfs", 
        #     "Downscaled GFS by NAM Extension": "dgex", "Extra-Tropical Storm Surge": "etss", 
        #     "Extra-Tropical Surge and Tide Operational Forecast System": "estofs",
        #     "GFS Ensemble Forecast System": "gens", "Global Forecast System": "gfs", 
        #     "High-Resolution Rapid Refresh": "hrrr", "High-Resolution Window Forecast System": "hiresw",
        #     "Hybrid Single Particle Langrangian Integrated Trajectory": "hysplit", "Hurricane Models": "hur",
        #     "NEMS GFS Aerosol Component": "ngac", "North American Ensemble Forecast System": "naefs", 
        #     "North American Land Data Assimilation Systems": "nldas",
        #     "North American Mesoscale Forecast System": "nam", "North American RAP Ensemble": "narre",
        #     "National Ocean Service": "nos", "National Water Model": "nwm",
        #     "Probabilistic Extra-Tropical Storm Surge": "petss", "Rapid Refresh": "rap",
        #     "Real-Time Mesoscale Analysis": "rtma", "Real-Time Ocean Forecast System": "omb",
        #     "Sea Ice Drift": "sea_ice_drift", "Sea Surface Temperature": "SST", 
        #     "Short Range Ensemble Forecast": "serf", "Wave Models": "wave", "WSA Enlil": "wsa_enlil"}
        self.NCEP_PRODUCTS = {"Global Forecast System": "gfs"}
        self.providers = {"Global Forecast System": GFS_Provider()}


    def reset(self):
        self.NCEP_BASE_SITE_URL = "http://www.nco.ncep.noaa.gov/pmb/products/"
        self.NCEP_BASE_FTP_URL = "http://www.ftp.ncep.noaa.gov/data/nccf/com/"
        self.main_parser.reset()
        self.main_parser.our_reset()
    

    def validate_date(self, product_date):
        try:
            datetime.datetime.strptime(product_date, '%Y%m%d')
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYYMMDD")


    def list_ncep_products(self):
        
        keys = []
        
        for key, value in self.NCEP_PRODUCTS.items():
            keys.append(key)
        
        return keys


    def list_ncep_product_of_products(self, ncep_provider):

        if type(ncep_provider) != str:
            raise ValueError("Sorry, but ncep_provider needs to be a string.")
        elif ncep_provider not in self.NCEP_PRODUCTS:
            raise ValueError("Sorry, but that provider is not avaliable.")
        
        products = self.providers[ncep_provider].get_products()

        for key, value in products.items():
            print("Product Type: " + key)
            for key2, value2 in value.items():
                print("Prodcut name: " + key2)
        

    def get(self, url):

        try:
            response = requests.get(url=url)
            if response.status_code in (200, 201):
                return response.text
            else:
                return "Error:  Unexpected response {}".format(response)
        except requests.exceptions.RequestException as e:
            return "Error: {}".format(e)
    

    def get_formats_of_a_product(self, ncep_provider):

        if type(ncep_provider) != str:
            raise ValueError("Sorry, but ncep_provider needs to be a string.")
        elif ncep_provider not in self.NCEP_PRODUCTS:
            raise ValueError("Sorry, but that provider is not avaliable.")
        
        keys = []

        temp_path = self.NCEP_BASE_FTP_URL + self.NCEP_PRODUCTS[ncep_provider] + "/prod/"
        html_data = self.get(url=temp_path)
        self.main_parser.feed(html_data)
        keys = self.main_parser.get_product_formats()
        self.reset()

        return keys


    def get_data_dates_of_a_product(self, ncep_provider):

        if type(ncep_provider) != str:
            raise ValueError("Sorry, but ncep_provider needs to be a string.")
        elif ncep_provider not in self.NCEP_PRODUCTS:
            raise ValueError("Sorry, but that provider is not avaliable.")
        
        dates = []

        temp_path = self.NCEP_BASE_FTP_URL + self.NCEP_PRODUCTS[ncep_provider] + "/prod/"
        html_data = self.get(url=temp_path)
        self.main_parser.feed(html_data)
        dates = self.main_parser.get_product_data_dates()
        self.reset()

        return dates


    def get_ncep_product_data(self, ncep_provider, product_date, product_format, **kwargs):
        
        # Might have to add the data format within the given product, but that is next to the date.

        if type(ncep_provider) != str and type(product_date) != str:
            raise ValueError("Sorry, but these parameters need to be a string: ncep_provider, product_date.")
        elif ncep_provider not in self.NCEP_PRODUCTS:
            raise ValueError("Sorry, but that product is not avaliable.")

        self.validate_date(product_date)
        product_path = self.NCEP_BASE_FTP_URL + self.NCEP_PRODUCTS[ncep_provider] + "/prod/"

        return self.providers[ncep_provider].get_data(product_date, product_format, product_path, **kwargs)


    def download_data(self, download_dst, list_of_datasets):

        temp_path = None
        if download_dst[-1] != '/':
            download_dst += '/'

        if os.path.exists(download_dst):
            for item in list_of_datasets:
                for key, value in item.items():
                    if key == "file_name":
                        temp_path = download_dst + value
                    if key == "download_url":
                        response = requests.get(value, verify=False)
                        if response.status_code == 200:
                            chunk_size = 64 * 1024
                            with open(temp_path, 'wb') as f:
                                for content in response.iter_content(chunk_size):
                                    f.write(content)
        else:
            raise ValueError("Sorry, but the download destination that you requested is not a path.")