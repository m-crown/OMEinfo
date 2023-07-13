
# Import necessary packages
import boto3
from botocore.exceptions import NoCredentialsError
from rio_tiler.io import Reader

s3_bucket = 'cloudgeotiffbucket'
s3_key1 = 'rurpopkop_v1_cog.tif'
s3_key2= 'co2_v1_cog.tif'
s3_key3= 'no2_v1_cog.tif'
s3_region = 'eu-north-1'

s3_url = f"https://{s3_bucket}.s3.{s3_region}.amazonaws.com/{s3_key3}"

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
    with Reader("no2_v1_cog.tif") as cog:
        print(cog.__dict__)
        print(cog.bounds)
        rurality_values = []
        
        # Read pixel values for all bands at coordinates (x, y)
        pointdata = cog.point(x, y, coord_crs=coord_projection, indexes=[1])
        print(pointdata.data.shape)
        rurality_values.append(int(pointdata.data[0]))
        print(rurality_values)
    


print(upload_cog_s3(s3_key1, s3_bucket, "rurpopkop_v1_cog.tif"))
print(upload_cog_s3(s3_key2, s3_bucket, "co2_v1_cog.tif"))
print(upload_cog_s3(s3_key3, s3_bucket, "no2_v1_cog.tif"))

#print(get_s3_point_data(-7447, 6031275, s3_url, coord_projection = "ESRI:54009"))

