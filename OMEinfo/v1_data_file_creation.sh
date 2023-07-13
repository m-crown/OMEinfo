#usr/bin/sh
#v1 data file creation.
gdalwarp -t_srs ESRI:54009 Beck_KG_V1_present_0p0083.tif Beck_KG_V1_present_0p0083_mollweide.tif
merge_tif.sh rurpopkop_v1.tif GHS_POP_E2015_GLOBE_R2019A_54009_1K_V1_0.tif GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K_V2_0.tif Beck_KG_V1_present_0p0083_mollweide.tif

#average the co2 geotif files
python3 average_geotif.py

#in google earth engine:
# // Define the time range
# var start_date = '2022-01-01';  // The start date
# var end_date = '2022-12-31';  // The end date

# // Define the product name
# var product = 'COPERNICUS/S5P/OFFL/L3_NO2';

# // Create an ImageCollection for the desired time range and product
# var collection = ee.ImageCollection(product)
#                   .select('tropospheric_NO2_column_number_density')
#                   .filterDate(start_date, end_date);

# print('Number of images in the collection:', collection.size());

# // Calculate the mean of the ImageCollection
# var mean = collection.mean();

# // Define the export parameters
# var exportParams = {
#   maxPixels: 1e13,
# };

# // Define the export task
# Export.image.toDrive({
#   image: mean,
#   description: 'no2_v1',
#   folder: 'EarthEngineData',
#   fileNamePrefix: 'no2_v1',
#   maxPixels: exportParams.maxPixels,
#   fileFormat: 'GeoTIFF',
#   formatOptions: {
#     cloudOptimized: true
#   }
# });

# // Print the export task
# print('Export task started')
#note earth engine outputs a range after file prefix, needs to be removed before upload with cog creator
#outputs are split, to combine use gdal_merge.py

gdal_merge.py -o no2_v1.tif no2_v1-0000*

#create the cog files
rio cogeo create rurpopkop_v1.tif rurpopkop_v1_cog.tif
rio cogeo create co2_v1.tif co2_v1_cog.tif
rio cogeo create no2_v1.tif no2_v1_cog.tif

#upload the cog files
python3 cog_creator.py