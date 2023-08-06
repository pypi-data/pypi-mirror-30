from . import gfs_parser
import requests # Do the following inorder to install: conda install -c conda-forge requests
#http://www.nco.ncep.noaa.gov/pmb/products/

class GFS_Provider():
    
    def __init__(self):
        self.parser = gfs_parser.TheParser()
        self.parser.reset()
        self.my_list = []
        self.NCEP_BASE_SITE_URL = "http://www.nco.ncep.noaa.gov/pmb/products/"
        self.NCEP_BASE_FTP_URL = "http://www.ftp.ncep.noaa.gov/data/nccf/com/"
        self.gfs_products = {"GFS": 
                            {"Global longitude-latitude grid": "pgrb", 
                            "0.50 deg 'full' file description": "pgrb2full", 
                            "T1534 Semi-Lagrangian grid": "sfluxgrb", 
                             "MOS Aviation Product": "mdl_", 
                             "MDL Extratropical Storm Surge": " mdlsurge", 
                             "Smart Initialization Guam": "smartguam",
                             "WAFS/ICAO/International Exchange/FOS Grids": "wafsgfs_", 
                             "global longitude-latitude grid (1.0 deg)": "1p0deg", 
                             "32km Lambert Conformal grid": "grd221",
                             "World Area Forecast System": "wafs", 
                             "Sigma Atmospheric Model Data": "atm", 
                             "Surface Boundary Conditions": "sfc",
                             "Surface Analysis": "sfcanl", 
                             "Binary Universal Form for the Representation of meteorological data (BUFR)": "bufr_d", 
                             "Prepared BUFR files": "prepbufr",
                             "BUFR Sounding Files per Station": "bufr", 
                             "Tropical Cyclone Vital Statistics": "syndata"},
                             "GDAS": 
                             {"Pressure Level Data": "pgrb2", 
                             "Surface Flux": "sfluxgrb",
                             "Prepared BUFR files": "prepbufr", 
                             "Binary Universal Form for the Representation of meteorological data (BUFR)": "bufr_d(Y)", 
                             "Time Dependent Satellite Bias Correction": "abias",
                             "Atmospheric Analysis": "atmanl", 
                             "Surface Analysis": "sfcanl", 
                             "Atmospheric Model Data": "atm", 
                             "Surface Boundary Conditions": "sfc", 
                             "Tropical Cyclone Vital Statistics": "tcvitals"}}


    def reset(self):
        self.NCEP_BASE_SITE_URL = "http://www.nco.ncep.noaa.gov/pmb/products/"
        self.NCEP_BASE_FTP_URL = "http://www.ftp.ncep.noaa.gov/data/nccf/com/"
        self.parser.reset()
        self.parser.our_reset()
        self.my_list = []


    def get(self, url):

        try:
            response = requests.get(url=url)
            if response.status_code in (200, 201):
                return response.text
            else:
                return "Error:  Unexpected response {}".format(response)
        except requests.exceptions.RequestException as e:
            return "Error: {}".format(e)     


    def get_products(self):
        return self.gfs_products


    def get_data(self, product_date, product_format, product_path, **kwargs):
        """
            Required Params:
                product_date
                product_format
                product_path
            
            Not Required Params:
                product_type
                name_of_product
                resolution
                cycle_runtime
                forecast_start
                forecast_end
                
        """
        link = None
        verify = None
        temp_path = None
        download_url = None
        proper_cycle_runtime = None
        Forecast_Start = None
        Forecast_End = None
        Resolution = None
        Cycle_runtime = None
        name_of_product = None
        product_type = None
        list_holder_1 = []
        list_holder_2 = []
        the_data = []
        temp_holding_dict = {}
        
        if kwargs["cycle_runtime"] is not None and type(kwargs["cycle_runtime"]) == str:
            Cycle_runtime = kwargs["cycle_runtime"]
            proper_cycle_runtime = "t" + Cycle_runtime + "z"
        
        if kwargs["resolution"] is not None and type(kwargs["resolution"]) == str:
            Resolution = kwargs["resolution"]

        if kwargs["product_type"] is not None and type(kwargs["product_type"]) == str:
            product_type = kwargs["product_type"]

        if kwargs["name_of_product"] is not None and type(kwargs["name_of_product"]) == str:
            name_of_product = kwargs["name_of_product"]            

        if product_format is not None and type(product_format) == str:
            if product_format == "enkf":
                raise ValueError("Sorry, this product format is not yet supported.")
        else:
            raise ValueError("Sorry, but the product format that you are looking for is required.")
        
        if product_type is not None and name_of_product is not None:
            if product_type in self.gfs_products:
                if name_of_product in self.gfs_products[product_type]:
                    name_of_product = self.gfs_products[product_type][name_of_product]
                else:
                    raise ValueError("Sorry, but that name of product is not associated to the given product type.")
            else:
                raise ValueError("Sorry, but that product type is not in dictionary of products.")

        if kwargs["name_of_product"] is not None:
            if type(kwargs["name_of_product"]) != str:
                raise ValueError("Sorry, but name_of_product needs to be a string.")
            else:
                if name_of_product == "pgrb":
                    name_of_product = proper_cycle_runtime + "." + name_of_product 

        if product_type == "GFS":
            if Cycle_runtime is None:
                raise ValueError("Sorry, but the cycle_runtime was not given or the type that was given is not correct.")
            else:
                product_date += Cycle_runtime

        if kwargs["forecast_start"] is not None and type(kwargs["forecast_start"]) == str:
            my_int = kwargs["forecast_start"]
            my_int = my_int.lstrip('0')
            if len(my_int) == 0:
                my_int = 0
            else:
                my_int = int(my_int)
            if my_int >= 0 and my_int <= 385:
                Forecast_Start = int(my_int)
            else:
                raise ValueError("Sorry, but the start hour has to be a positive number and less than 385.")
        
        if kwargs["forecast_end"] is not None and type(kwargs["forecast_end"]) == str:
            if Forecast_Start is not None:
                my_int = kwargs["forecast_end"]
                my_int = my_int.lstrip('0')
                if len(my_int) == 0:
                    my_int = 0
                else:
                    my_int = int(my_int)
                if my_int >= 0 and my_int <= 386:
                    Forecast_End = int(my_int)
                else:
                    raise ValueError("Sorry, but the start hour has to be a positive number and less than 385.")
                if Forecast_Start > Forecast_End:
                    raise ValueError("Sorry, but you cannot have your starting hour be larger then your ending hour.")
            else:
                raise ValueError("Sorry, but you cannot have a ending forecast hour and not have starting hour.")

        html_data = self.get(product_path)
        self.parser.feed(html_data)
        product_data = self.parser.get_all_product_data()
        self.reset()

        if product_format is not None:
            if product_date in product_data[product_format]:
                link  = product_format + "." + product_date
                verify = True
        else:
            for key, value in product_data.items():
                if product_date in value:
                    link = key + "." + product_date
                    verify = True

        if verify is None:
            raise ValueError("Sorry, the date given is not in the database.")

        product_path += link
        html_data = self.get(product_path)
        self.parser.feed(html_data)
        the_data = self.parser.get_list()
        self.reset()

        for item in the_data:
            identifier, link = item.split(",")
            link = link.replace(")", "").replace("'", "").replace(" ", "")
            if ".idx" not in link:
                if name_of_product is not None:
                    if name_of_product in link:
                        list_holder_1.append(link)
                else:
                    list_holder_1.append(link)

        if Resolution is not None:
            for item in list_holder_1:
                if Resolution in item:
                    list_holder_2.append(item)
            
            if len(list_holder_2) != 0:
                list_holder_1 = list_holder_2
                list_holder_2 = []
            else:
                list_holder_1 = []
                return list_holder_1

        if Cycle_runtime is not None:
            for item in list_holder_1:
                if proper_cycle_runtime in item:
                    list_holder_2.append(item)
            
            if len(list_holder_2) != 0:
                list_holder_1 = list_holder_2
                list_holder_2 = []
            else:
                list_holder_1 = []
                return list_holder_1

        if Forecast_Start is not None and Forecast_End is not None:
            for item in list_holder_1:
                for x in range(Forecast_Start, Forecast_End + 1):
                    my_string = '{0:03}'.format(x)
                    my_string = "f" + my_string
                    if my_string in item:
                        list_holder_2.append(item)
                        break

            if len(list_holder_2) != 0:
                list_holder_1 = list_holder_2
                list_holder_2 = []
            else:
                list_holder_1 = []
                return list_holder_1

        if len(list_holder_1) > 0:
            for item in list_holder_1:
                if product_type is not None:
                    if product_type.lower() in item:
                        temp_list = item.split(".")
                        temp_path = product_path + "/" + item
                        temp_holding_dict = {"file_name": item, "id": "ncep", "download_url": temp_path, "file_format":  temp_list[-1]}
                        list_holder_2.append(temp_holding_dict)
                else:
                    temp_list = item.split(".")
                    temp_path = product_path + "/" + item
                    temp_holding_dict = {"file_name": item, "id": "ncep", "download_url": temp_path, "file_format":  temp_list[-1]}
                    list_holder_2.append(temp_holding_dict)
            if len(list_holder_2) != 0:
                list_holder_1 = list_holder_2
                list_holder_2 = []
            else:
                list_holder_1 = []
        
        return list_holder_1
