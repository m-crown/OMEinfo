import numpy as np
import rasterio

im1 = 'odiac2020b_1km_excl_intl_1901.tif'
im2 = 'odiac2020b_1km_excl_intl_1902.tif'
im3 = 'odiac2020b_1km_excl_intl_1903.tif'
im4 = 'odiac2020b_1km_excl_intl_1904.tif'
im5 = 'odiac2020b_1km_excl_intl_1905.tif'
im6 = 'odiac2020b_1km_excl_intl_1906.tif'
im7 = 'odiac2020b_1km_excl_intl_1907.tif'
im8 = 'odiac2020b_1km_excl_intl_1908.tif'
im9 = 'odiac2020b_1km_excl_intl_1909.tif'
im10 = 'odiac2020b_1km_excl_intl_1910.tif'
im11 = 'odiac2020b_1km_excl_intl_1911.tif'
im12 = 'odiac2020b_1km_excl_intl_1912.tif'

with rasterio.open(im1) as src:
    array1 = src.read()
    profile1 = src.profile
with rasterio.open(im2) as src:
    array2 = src.read()
    profile2 = src.profile
with rasterio.open(im3) as src:
    array3 = src.read()
    profile3 = src.profile
with rasterio.open(im4) as src:
    array4 = src.read()
    profile4 = src.profile
with rasterio.open(im5) as src:
    array5 = src.read()
    profile5 = src.profile
with rasterio.open(im6) as src:
    array6 = src.read()
    profile6 = src.profile
with rasterio.open(im7) as src:
    array7 = src.read()
    profile7 = src.profile
with rasterio.open(im8) as src:
    array8 = src.read()
    profile8 = src.profile
with rasterio.open(im9) as src:
    array9 = src.read()
    profile9 = src.profile
with rasterio.open(im10) as src:
    array10 = src.read()
    profile10 = src.profile
with rasterio.open(im11) as src:
    array11 = src.read()
    profile11 = src.profile
with rasterio.open(im12) as src:
    array12 = src.read()
    profile12 = src.profile


# Create nodata mask (True is nodata)
nodata_mask = np.any((array1 == profile1.get('nodata'),
                      array2 == profile2.get('nodata'),
                      array3 == profile3.get('nodata'),
                      array4 == profile4.get('nodata'),
                      array5 == profile5.get('nodata'),
                      array6 == profile6.get('nodata'),
                      array7 == profile7.get('nodata'),
                      array8 == profile8.get('nodata'),
                      array9 == profile9.get('nodata'),
                      array10 == profile10.get('nodata'),
                      array11 == profile11.get('nodata'),
                      array12 == profile12.get('nodata'),),
                     axis=0)
# Compute anything what you want
array_mean = np.mean((array1, array2, array3,array4, array5, array6,array7, array8, array9,array10, array11, array12), axis=0)
array_sd = np.std((array1, array2, array3,array4, array5, array6,array7, array8, array9,array10, array11, array12), axis=0)

# replace nodata pixels to np.nan
array_mean[nodata_mask] = np.nan
array_sd[nodata_mask] = np.nan

# Write as geotiff file
profile_out = profile1.copy()
profile_out.update(dtype=array_mean.dtype.name,
                   nodata=np.nan)
with rasterio.open('co2.tif', 'w', **profile_out) as dst:
    dst.write(array_mean)