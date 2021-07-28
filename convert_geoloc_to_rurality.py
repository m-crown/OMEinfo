#Convert geolocation e.g. Postcode and House Number or Lat Long to a rurality measure. 

#Take as input a CSV file, with postcode and house number, or lat long values (with header to detect format)

import pandas as pd
from geopy.geocoders import GoogleV3
import pyproj as proj
import rasterio
import os

def convert_projection(df,projection):
    #wrapper function to convert EPSG:4326 latitude and longitudes to ESRI:54009 for GHS-SMOD using a pyproj transformer
    #takes as input pandas series for latitude, longitude and sample name
    if projection == "mollweide":
        df["Latitude"].loc[df["Latitude"].isnull()] = 0
        df["Longitude"].loc[df["Longitude"].isnull()] = 0
        transformer = proj.Transformer.from_crs('EPSG:4326', 'ESRI:54009', always_xy=True)
        mollweide_lon, mollweide_lat = transformer.transform(df["Longitude"].values, df["Latitude"].values)
        df["moll_lat"] = mollweide_lat
        df["moll_lon"] = mollweide_lon
    return df

def latlon_from_address(df):
    #subset to only run the api call on locations that NEED lat lon, prevents repeated duplicate api calls
    api_key = "AIzaSyD1lkxXnVXWU384JeY0cFogmCeVk8SneNg"
    geolocator = GoogleV3(api_key = api_key, user_agent="urbrur_application")
    latlon_missing = df.loc[df["Latitude"].isnull()]
    latlon_missing['Location'] = latlon_missing['Postcode'].astype(str).fillna('') + ',' + latlon_missing['Address'].astype(str).fillna('')
    lat = []
    lon = []
    for each in latlon_missing['Location']:
        geoloc = geolocator.geocode(each)
        print(geoloc)
        if hasattr(geoloc, "latitude"):
            lat.append(geoloc.latitude)
            lon.append(geoloc.longitude)
        else:
            #this basically seems to be an issue with Greek addresses and so could pose an issue elsewhere too. Could move to google api instead
            print("Issue with: ",each,"\nCould not find this address - check format or fill manually with Google Maps")
            lat.append("Unknown")
            lon.append("Unknown") 
    latlon_missing['Latitude'] = lat
    latlon_missing['Longitude'] = lon
    #now merge the updated lat lons into the full table. 
    df.update(latlon_missing)
    return df

def get_rurality(df,geoquery):
    #function takes a pandas dataframe containing sample names, latitude and longitude, and returns a rurality measurment for each location based on GHS-SMOD raster data. 
    values = []
    if geoquery == "rurality":
        with rasterio.open("GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K_V2_0.tif") as src:
            for val in src.sample(zip(df["moll_lon"], df["moll_lat"]), indexes = 1):
                values.append(int(val))
        df = pd.concat([df, pd.Series(values, name = "Rurality")],axis =1)
    return df

def get_pop_density(df,geoquery):
    #function takes a pandas dataframe containing sample names, latitude and longitude, and returns a rurality measurment for each location based on GHS-SMOD raster data. 
    values = []
    if geoquery == "pop_density":
        with rasterio.open("GHS_POP_E2015_GLOBE_R2019A_54009_1K_V1_0.tif") as src:
            for val in src.sample(zip(df["moll_lon"], df["moll_lat"]), indexes = 1):
                values.append(float(val))
        df = pd.concat([df, pd.Series(values, name = "Population Density")],axis =1)
    return df

def get_koppen(df,geoquery):
    #function takes a pandas dataframe containing sample names, latitude and longitude, and returns a rurality measurment for each location based on GHS-SMOD raster data. 
    values = []
    if geoquery == "koppen":
        with rasterio.open("Beck_KG_V1_present_0p0083.tif") as src:
            for val in src.sample(zip(df["Longitude"], df["Latitude"]), indexes = 1):
                values.append(int(val))
        df = pd.concat([df, pd.Series(values, name = "Koppen")],axis =1)
    return df

# df = pd.read_csv("homes_mapping_rurality_rur_rem.csv")

# df = get_koppen(df, "koppen")

# print(df["Rurality"].head)
# parser.add_argument('-a', '--api_key', metavar='', type=str,
#                     help='API Key for accessing the Google Maps API')

# 



# #print(transformer.transform(-541000.000, 6500000.000))

# geolocator = GoogleV3(api_key = api_key, user_agent="urbrur_application")

# my_dir = os.path.expanduser("GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K_V2_0.tif")

# dataset = rasterio.open(my_dir)

# if location_info.columns.values.tolist() == ['Sample','Postcode','Address', "Latitude", "Longitude"]:
#     #subset to only run the api call on locations that NEED lat lon, prevents repeated duplicate api calls
#     latlon_missing = location_info.loc[location_info["Latitude"].isnull()]
#     latlon_missing['Location'] = latlon_missing['Postcode'].astype(str).fillna('') + ',' + latlon_missing['Address'].astype(str).fillna('')
#     lat = []
#     lon = []
#     for each in latlon_missing['Location']:
#         geoloc = geolocator.geocode(each)
#         print(geoloc)
#         if hasattr(geoloc, "latitude"):
#             lat.append(geoloc.latitude)
#             lon.append(geoloc.longitude)
#         else:
#             #this basically seems to be an issue with Greek addresses and so could pose an issue elsewhere too. Could move to google api instead
#             print("Issue with: ",each,"\nCould not find this address - check format or fill manually with Google Maps")
#             lat.append("Unknown")
#             lon.append("Unknown") 
#     latlon_missing['Latitude'] = lat
#     latlon_missing['Longitude'] = lon
#     #now merge the updated lat lons into the full table. 
#     location_info.update(latlon_missing)    
# else:
#     print("Unrecognised file format, please check input file columns (expected order: [Sample,Postcode,Address,Latitude,Longitude] - include latitude and longitude columns even if not known")

