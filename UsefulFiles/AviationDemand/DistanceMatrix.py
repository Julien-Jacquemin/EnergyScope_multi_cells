# -*- coding: utf-8 -*-
"""
Created on Mon May 22 12:38:09 2023

Used to generate extra-EU and intra-EU aviation passenger demand based on number of passenger
carried between countries avia_paexcc and avia_paincc from Eurostat and distance calculated via 
geopy. .csv file from eurostat should be modified to correspond to the format :
unit	tra_meas	partner	geo\time	<year analyzed (2019 for this case)>

@author: JulienJacquemin
"""

import geopy.distance
from geopy.geocoders import Nominatim
import pandas as pd

# Countries of which we want to evaluate the aviation demand
country_code = ["AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "GR", "ES", "FI", "FR", 
 "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", 
 "SE", "SI", "SK", "UK"]
data_pkm = dict.fromkeys(country_code)

geolocator = Nominatim(user_agent="DistanceMatrix")

# Open Eurostat data file, avia_paincc.tsv is for intra-EU aviation
# avia_paexcc.tsv is for extra-EU aviation.
# PAS_CRD_DEP is the data code related to departure of aircrafts.
with open("avia_paincc.tsv", "r") as pass_data_file:
    data_frame = pd.read_csv(pass_data_file, keep_default_na=False, index_col=[0, 2, 1], usecols=[1, 2, 3, 4], sep="\t").loc["PAS_CRD_DEP"]
    data_frame = data_frame.replace(to_replace=": ", value=0)
    
nb_pass_tot = 0
for country in country_code:
    country_pkm = 0
    
    location_country = geolocator.geocode({"country": country})
    # If a country data code is not recognized by the geolocator
    if type(location_country) == "NoneType":
        print("EU country wrong : " + country)
    lat_lon_country = (location_country.latitude, location_country.longitude)
    
    data = data_frame.loc[country]
    
    for partner in data.index :
        if len(partner) == 2 : # Recognize country only and no aggregated regions such as AFR
            nb_pass_tot = nb_pass_tot + float(data.loc[partner])
            
            location_partner = geolocator.geocode({"country": partner})
            if location_partner is None:
                print("EU partner wrong : " + partner)
            # Some partner country data code are not recognized so manual location is performed
            if partner == "AN":
                lat_lon_partner = (12.226079,  -69.060087)
            elif partner == "AW":
                lat_lon_partner = (12.521110, -69.968338)
            elif partner == "HK":
                lat_lon_partner = (22.302711, 114.177216)
            elif partner == "NC":
                lat_lon_partner = (-21.123889, 165.846901)
            elif partner == "PF":
                lat_lon_partner = (-17.535000, -149.569595)
            elif partner == "VI":
                lat_lon_partner = (18.335765,  -64.896335)
            elif partner == "PS":
                lat_lon_partner = (31.952162, 35.233154)
            else :
                lat_lon_partner = (location_partner.latitude, location_partner.longitude)
            distance = geopy.distance.distance(lat_lon_country, lat_lon_partner)
            country_pkm = country_pkm + float(data.loc[partner])*distance.km
            
    data_pkm[country] = country_pkm
        
    
with open("IntraEU_aviation_demand(eurostat).csv", "w") as demand_file:
    print("Country ; Aviation demand [Gpkm]", file=demand_file)
    for country, demand in data_pkm.items():
        if demand != None:
            print(country + " ; %.2f" %(demand*10**-9), file=demand_file)
    total_demand = sum(list(data_pkm.values()))
    print("Total [Gpkm] ; %.2f" %(total_demand*10**-9), file=demand_file)
    print("Average flight length of a passenger [km] ; %.2f" %(total_demand/nb_pass_tot), file=demand_file)

    