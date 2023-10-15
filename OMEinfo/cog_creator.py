
# Import necessary packages
import boto3
from botocore.exceptions import NoCredentialsError
from rio_tiler.io import Reader
import pandas as pd

s3_bucket = 'cloudgeotiffbucket'
s3_key1 = 'rurpopkoppov_v1_cog.tif'
s3_key2= 'co2_v1_cog.tif'
s3_key3= 'no2_v1_cog.tif'
s3_key4= 'omeinfo_v2.tif'
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


#old uploads commented out.
#print(upload_cog_s3(s3_key1, s3_bucket, "rurpopkoppov_v1_cog.tif"))
#print(upload_cog_s3(s3_key2, s3_bucket, "co2_v1_cog.tif"))
#print(upload_cog_s3(s3_key3, s3_bucket, "no2_v1_cog.tif"))

print(upload_cog_s3(s3_key4, s3_bucket, "omeinfo_v2.tif"))