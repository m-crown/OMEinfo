# OMEinfo Data Processing

## Data Packet Version 2

* The fossil fuel CO<sub>2</sub> emissions data from ODIAC is averaged using the `average_geotif.py` script.
* To obtain the Copernicus S3p NO<sub>2</sub> geotiff files, the following code is executed in Google Earth Engine:
  
  ```
  // Define the time range
  var start_date = '2022-01-01';  // The start date
  var end_date = '2022-12-31';  // The end date
  ```

// Define the product name
var product = 'COPERNICUS/S5P/OFFL/L3_NO2';

// Create an ImageCollection for the desired time range and product
var collection = ee.ImageCollection(product)
                  .select('tropospheric_NO2_column_number_density')
                  .filterDate(start_date, end_date);

print('Number of images in the collection:', collection.size());

// Calculate the mean of the ImageCollection
var mean = collection.mean();

// Define the export parameters
var exportParams = {
   maxPixels: 1e13,
 };

// Define the export task
Export.image.toDrive({
  image: mean,
  description: 'no2_v1',
  folder: 'EarthEngineData',
  fileNamePrefix: 'no2_v1',
  maxPixels: exportParams.maxPixels,
  fileFormat: 'GeoTIFF',
  formatOptions: {
    cloudOptimized: true
  }
});

```
This produces an annual average NO2 value for each pixel. The files are then downloaded from Drive.

* Earth engine outputs a range after file prefix, and outputs are split, to combine use gdal_merge.py:

`gdal_merge.py -o no2_v1.tif no2_v1-0000*`

* The population density and rurality data sources are reprojected into WGS84 format using gdalwarp:
`gdalwarp -t_srs EPSG:4326 GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K_V2_0.tif GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K_V2_0_wgs84.tif`
`gdalwarp -t_srs EPSG:4326 GHS_POP_E2015_GLOBE_R2019A_54009_1K_V1_0_.tif GHS_POP_E2015_GLOBE_R2019A_54009_1K_V1_0_wgs84.tif`

* Merge the data sources into a single file:

`gdal_merge.py -separate -o omeinfo_v2_merge.tif GHS_POP_E2015_GLOBE_R2019A_54009_1K_V1_0_wgs84.tif GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K_V2_0_wgs84.tif no2_v1.tif co2.tif povmap-grdi-v1.tif Beck_KG_V1_present_0p0083.tif`

* Create the COG file:

`rio cogeo create omeinfo_v2_merge.tif omeinfo_v2.tif`

* Upload the COG files:
`python3 cog_creator.py`

## DEPRECATED: Data Packet Version 1


* The fossil fuel CO2 emissions data from ODIAC is averaged using the `average_geotif.py` script.
* To obtain the Copernicus S3p NO2 geotiff files, the following code is executed in Google Earth Engine:
```

// Define the time range
var start_date = '2022-01-01';  // The start date
var end_date = '2022-12-31';  // The end date

// Define the product name
var product = 'COPERNICUS/S5P/OFFL/L3_NO2';

// Create an ImageCollection for the desired time range and product
var collection = ee.ImageCollection(product)
                  .select('tropospheric_NO2_column_number_density')
                  .filterDate(start_date, end_date);

print('Number of images in the collection:', collection.size());

// Calculate the mean of the ImageCollection
var mean = collection.mean();

// Define the export parameters
var exportParams = {
   maxPixels: 1e13,
 };

// Define the export task
Export.image.toDrive({
  image: mean,
  description: 'no2_v1',
  folder: 'EarthEngineData',
  fileNamePrefix: 'no2_v1',
  maxPixels: exportParams.maxPixels,
  fileFormat: 'GeoTIFF',
  formatOptions: {
    cloudOptimized: true
  }
});

```
This produces an annual average NO2 value for each pixel. The files are then downloaded from Drive.

* Earth engine outputs a range after file prefix, and outputs are split, to combine use gdal_merge.py:

`gdal_merge.py -o no2_v1.tif no2_v1-0000*`

* Reproject KG classification to mollweide to combine with population density and rurality geotiffs.
`gdalwarp -t_srs ESRI:54009 Beck_KG_V1_present_0p0083.tif Beck_KG_V1_present_0p0083_mollweide.tif`

* Merge KG, population density and rurality geotiffs into single file:
`gdal_merge.py -separate -o rurpopkop_v1.tif GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K_V2_0.tif GHS_POP_E2015_GLOBE_R2019A_54009_1K_V1_0.tif  Beck_KG_V1_present_0p0083_mollweide.tif`

*Note* Can also use: `rio warp Beck_KG_V1_present_0p0083.tif Beck_KG_V1_present_0p0083_mollweide.tif --like GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K_V2_0.tif`

* Create the COG files:
```

rio cogeo create rurpopkop_v1.tif rurpopkop_v1_cog.tif
rio cogeo create co2_v1.tif co2_v1_cog.tif
rio cogeo create no2_v1.tif no2_v1_cog.tif

```
* Upload the COG files to S3:
  `python3 cog_creator.py`
```
