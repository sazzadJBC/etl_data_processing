import boto3
import os
from botocore.exceptions import ClientError

# ---- CONFIGURATION ----
AWS_ACCESS_KEY = "access key"
AWS_SECRET_KEY = "secret key"
REGION = 'ap-northeast-1'
BUCKET_NAME = "sevensix-documents"
LOCAL_DOWNLOAD_PATH = "./s3_downloads"  # Local directory to save files

# ---- INITIATE S3 CLIENT ----
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION
)

# ---- DOWNLOAD ALL FILES FROM BUCKET ----
def download_s3_bucket(bucket_name, local_dir):
    paginator = s3.get_paginator('list_objects_v2')
    try:
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get('Contents', []):
                s3_key = obj['Key']
                local_file_path = os.path.join(local_dir, s3_key)
                local_folder = os.path.dirname(local_file_path)
                if not os.path.exists(local_folder):
                    os.makedirs(local_folder)
                s3.download_file(bucket_name, s3_key, local_file_path)
                print(f"Downloaded: {s3_key} -> {local_file_path}")
    except ClientError as e:
        print(f"Error occurred: {e}")

# ---- RUN THE DOWNLOAD ----
download_s3_bucket(BUCKET_NAME, LOCAL_DOWNLOAD_PATH)
