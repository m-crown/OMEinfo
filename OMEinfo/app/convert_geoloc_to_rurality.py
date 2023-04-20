#Convert geolocation e.g. Postcode and House Number or Lat Long to a rurality measure. 

#Take as input a CSV file, with postcode and house number, or lat long values (with header to detect format)

import pandas as pd
from geopy.geocoders import GoogleV3
import pyproj as proj
import rasterio
import os

from rio_tiler.io import Reader

def get_s3_point_data(df, s3_url, geo_type, coord_projection="EPSG:3857"):
    print(s3_url)
    with Reader(s3_url) as cog:
        if geo_type == "rur_pop_kop":
            rurality_values = []
            pop_density_values = []
            koppen_values = []
            
            for _, row in df.iterrows():
                x, y = row["moll_lon"], row["moll_lat"]
                # Read pixel values for all bands at coordinates (x, y)
                pointdata = cog.point(x, y, coord_crs=coord_projection, indexes=[1, 2, 3])
                
                rurality_values.append(int(pointdata.data[0]))
                pop_density_values.append(float(pointdata.data[1]))
                koppen_values.append(int(pointdata.data[2]))
            
            df["Rurality"] = rurality_values
            df["Population Density"] = pop_density_values
            df["Koppen"] = koppen_values
        if geo_type == "co2":
            co2_values = []
            for _, row in df.iterrows():
                x, y = row["moll_lon"], row["moll_lat"]
                # Read pixel values for all bands at coordinates (x, y)
                pointdata = cog.point(x, y, coord_crs=coord_projection, indexes=[1])
                co2_values.append(float(pointdata.data[0]))
            
            df["CO2 emissions"] = co2_values
    
    return df

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




