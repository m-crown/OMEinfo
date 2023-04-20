
# Import necessary packages
import boto3
from botocore.exceptions import NoCredentialsError
from rio_tiler.io import Reader

s3_bucket = 'cloudgeotiffbucket'
s3_key1 = 'rur_pop_kop_multilayer_cog.tif'
s3_key2= 'co2_cog.tif'
s3_region = 'eu-north-1'
s3_url = f"https://{s3_bucket}.s3.{s3_region}.amazonaws.com/{s3_key1}"

def upload_cog_s3(key, bucket_name, local_filepath):
    session = boto3.client('s3')
    try:
        session.upload_file(local_filepath, bucket_name, key)
        return("Upload successful")
    except FileNotFoundError:
        return("The file was not found")
    except NoCredentialsError:
        return("Credentials not available")

def get_s3_point_data(x,y, s3_url, coord_projection="EPSG:3857"):
    with Reader(s3_url) as cog:
        rurality_values = []
        pop_density_values = []
        koppen_values = []
        
        # Read pixel values for all bands at coordinates (x, y)
        pointdata = cog.point(x, y, coord_crs=coord_projection, indexes=[1, 2, 3])
        print(pointdata.data.shape)
        rurality_values.append(int(pointdata.data[0]))
        pop_density_values.append(float(pointdata.data[1]))
        koppen_values.append(int(pointdata.data[2]))
        print(rurality_values, pop_density_values, koppen_values)
    


print(upload_cog_s3(s3_key1, s3_bucket, "test_output_multilayer_cog.tif"))
print(upload_cog_s3(s3_key2, s3_bucket, "result_cog.tif"))

print(get_s3_point_data(-7447, 6031275, s3_url, coord_projection = "ESRI:54009"))