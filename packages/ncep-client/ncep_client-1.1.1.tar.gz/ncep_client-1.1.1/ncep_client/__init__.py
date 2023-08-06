"""
Author: Aaron Anthony Valoroso
Date: March 30th, 2018
License: BSD-3-Clause
Email: valoroso99@gmail.com
"""
# http://www.nco.ncep.noaa.gov/pmb/products/
from .gfs import GFS_Provider
from . import parser
import datetime
import requests
import os

class NCEP_Client():
    """
        Overview: This class is meant for working with the providers in the NCEP Product Inventory.
    """
    def __init__(self):
        """
            Overview: In the constructor I list the base and ftp base URL for URL construction. I declare 
            the parser here because it is used throughout the module, and did not want to have
            to declare it over and over again in all the methods. The ncep_providers is the providers
            that we offer as of right now. Last, I have a a dictionary of all the different 
            providers that I offer, and will load the specific module for the specified provider.
        """
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
        self.NCEP_PROVIDERS = {"Global Forecast System": "gfs"}
        self.providers = {"Global Forecast System": GFS_Provider()}


    def download_data(self, download_dst, list_of_datasets):
        """
            Overview: This method will take in a list of data and a file destination, and 
            download the list of files to that destination.

            param download_dst: This is the file path on your computer that you want the 
            data to be downloaded to.
                type: string
            para list_of_datasets: This is the container that will hold all the data to be 
            downloaded. 
            Example: [ {'file_name': 'gfs.t18z.pgrb2.1p00.f003', 'id': 'ncep', 'download_url': 'http://www.ftp.ncep.noaa.gov/data/nccf/com/gfs/prod/gfs.2018032218/gfs.t18z.pgrb2.1p00.f003', 'file_format': 'f003'} ]
                type: list of dictionaries.
            
            Returning: None
        """
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


    def get(self, url):
        """
            Overview: This method is used to get the web page from the server and will return a text based 
            version of the webpage that you are trying to access.

            param url: Is a complete webpage url, example: https://www.google.com.
                type: string   

            Returning: String     
        """
        try:
            response = requests.get(url=url)
            if response.status_code in (200, 201):
                return response.text
            else:
                return "Error:  Unexpected response {}".format(response)
        except requests.exceptions.RequestException as e:
            return "Error: {}".format(e)
    

    def get_data_dates_of_a_product(self, ncep_provider):
        """
            Overview: This method returns a list of dates avaliable for the whole parent directory of prooduct formats
            and dates. The dates are when the data was gathered.

            param ncep_provider: Is a provider that we are able to get from within NCEP.
                type: string            
            
            Returning: List
        """
        if type(ncep_provider) != str:
            raise ValueError("Sorry, but ncep_provider needs to be a string.")
        elif ncep_provider not in self.NCEP_PROVIDERS:
            raise ValueError("Sorry, but that provider is not avaliable.")
        
        dates = []
        temp_path = self.NCEP_BASE_FTP_URL + self.NCEP_PROVIDERS[ncep_provider] + "/prod/"
        html_data = self.get(url=temp_path)
        self.main_parser.feed(html_data)
        dates = self.main_parser.get_product_data_dates()
        self.reset()

        return dates


    def get_formats_of_a_product(self, ncep_provider):
        """
            Overview: This method returns a list formats of what data is being held by a specific date within NCEP.
            What I mean by this is when in the product inventory for GFS, there are parent directories
            that look like the following: gfs.20180220, gdas.20180220 and so forth. The first part is
            what this method is returning.

            param ncep_provider: Is a provider that we are able to get from within NCEP.
                type: string       

            Returning: List     
        """
        if type(ncep_provider) != str:
            raise ValueError("Sorry, but ncep_provider needs to be a string.")
        elif ncep_provider not in self.NCEP_PROVIDERS:
            raise ValueError("Sorry, but that provider is not avaliable.")
        
        keys = []
        temp_path = self.NCEP_BASE_FTP_URL + self.NCEP_PROVIDERS[ncep_provider] + "/prod/"
        html_data = self.get(url=temp_path)
        self.main_parser.feed(html_data)
        keys = self.main_parser.get_product_formats()
        self.reset()

        return keys


    def get_ncep_product_data(self, ncep_provider, product_date, product_format, **kwargs):
        """
            Overview: This method is used to get data from NCEP. There is a list of possible parameters that this method
            can take and give to the specified provider that the user wants. The three parameters that are given
            before kwargs are required, everything else is different for each provider. So the parameter list will and 
            can get long. There will be a better way of showing what paramerts each provider can have and will need.
            
            Required
            param ncep_provider: This the provider that the user wants data from.
                type: string
            param product_date: This is the date that the user wants for the time the data was gathered / generated.
                type: string
            param product_format: This is the product format which is what association is distributing the data from 
            under the given provider.
                type: string
            
            Not Required - Genearl Parameters that come through kwargs.
            param cycle_runtime: This is the time in which the weather forecast data was generated.
                type: string
            param forecast_end: This was the end time of the forecast hour.
                type: string
            param forecast_start: This was the start time of the forecast hour.
                type: string
            param name_of_product: This is the type of product under an association and provider. This specifies the type 
            of data that you want.
                type: string
            param product_type: This is the association of who is distributing the data.
                type: string
            param resolution: This is the resolution of the data.
                type: string
            
            Returning: List of Dictionaries
        """
        if type(ncep_provider) != str and type(product_date) != str:
            raise ValueError("Sorry, but these parameters need to be a string: ncep_provider, product_date.")
        elif ncep_provider not in self.NCEP_PROVIDERS:
            raise ValueError("Sorry, but that product is not avaliable.")

        self.validate_date(product_date)
        product_path = self.NCEP_BASE_FTP_URL + self.NCEP_PROVIDERS[ncep_provider] + "/prod/"

        return self.providers[ncep_provider].get_data(product_date, product_format, product_path, **kwargs)


    def get_provider_products(self, ncep_provider):
        """
            Overview: This method is used to get all of the different products that a provider has to offer.
            A product is a type of data that is provided in the NCEP inventory.

            param ncep_provider: Is a provider that we are able to get from within NCEP.
                type: string    

            Returning: List        
        """
        if type(ncep_provider) != str:
            raise ValueError("Sorry, but ncep_provider needs to be a string.")
        elif ncep_provider not in self.NCEP_PROVIDERS:
            raise ValueError("Sorry, but that provider is not avaliable.")
        
        products = self.providers[ncep_provider].get_products()

        the_list = []
        for key, value in products.items():
            if key not in the_list:
                the_list.append(key)
            for key2, value2 in value.items():
                if key2 not in the_list:
                    the_list.append(key2)
        
        return the_list
    

    def get_provider_types(self, ncep_provider):
        """
            Overview: This method will get all the product types of a given provider. A product type is
            who is what association underneath the provider that is giving the data. 

            param ncep_provider: Is a provider that we are able to get from within NCEP.
                type: string

            Returning: List
        """
        if type(ncep_provider) != str:
            raise ValueError("Sorry, but ncep_provider needs to be a string.")
        elif ncep_provider not in self.NCEP_PROVIDERS:
            raise ValueError("Sorry, but that provider is not avaliable.")

        products = self.providers[ncep_provider].get_products()

        the_list = []
        for key, value in products.items():
            if key not in the_list:
                the_list.append(key)
        
        return the_list


    def list_ncep_providers(self):
        """
            Overview: This method will just list all the providers that we have to offer.

            Returning: List
        """
        keys = []
        for key, value in self.NCEP_PROVIDERS.items():
            keys.append(key)
        
        return keys


    def reset(self):
        """
            Overview: This method will just reset all the variables, and the parser. I also reset the parser
            I use and the parent parser. I was having issues with parameters not being in scope
            when the module left scope.

            Returning: None
        """
        self.NCEP_BASE_SITE_URL = "http://www.nco.ncep.noaa.gov/pmb/products/"
        self.NCEP_BASE_FTP_URL = "http://www.ftp.ncep.noaa.gov/data/nccf/com/"
        self.main_parser.reset()
        self.main_parser.our_reset()
    

    def validate_date(self, product_date):
        """
            Overview: This method will validate the incoming date and make sure it is in the format that I 
            need it to be in for how NCEP has it. 

            param product_date: Holds the date that the user is trying to get data for.
                type: string
            
            Returning: None
        """
        try:
            datetime.datetime.strptime(product_date, '%Y%m%d')
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYYMMDD")















 



