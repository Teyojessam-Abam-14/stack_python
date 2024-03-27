#!/usr/bin/python
import boto3,sys,json,os

#Create Bucket
def create_s3_bucket(s3,bucket_name):
    s3.create_bucket(
        Bucket=bucket_name,
        ObjectLockEnabledForBucket=True
    )

#Delete Bucket
def delete_s3_bucket(s3,bucket_name):
   s3.delete_bucket(
        Bucket=bucket_name
    )
   
#Upload files to S3
def upload_file_to_s3(s3, file_path, bucket_name, object_name):
    s3.upload_file(file_path, bucket_name, object_name, ExtraArgs={'ContentType': 'text/html'})