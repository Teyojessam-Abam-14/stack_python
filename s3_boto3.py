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
   
    
#Empty Bucket
def empty_s3_bucket(s3,bucket_name):
    
    object_list=s3.list_objects_v2(Bucket=bucket_name)
    
    if "Contents" in object_list:
        objects=[]
        for obj in object_list["Contents"]:
           objects.append({"Key": obj["Key"]})
        
        # Delete all objects in the bucket
        s3.delete_objects(
            Bucket=bucket_name,
            Delete={"Objects": objects}
        )
        
#Upload files to S3
def upload_file_to_s3(s3, file_paths, bucket_name, object_name):
    count=0
    for file in file_paths:
        count=count+1
        s3.upload_file(file, bucket_name, "{}_{}".format(object_name, count), ExtraArgs={'ContentType': 'text/html'})
        
#List Bucket
def list_s3_bucket(s3,bucket_name):
    
    object_list=s3.list_objects_v2(Bucket=bucket_name)
    
    if "Contents" in object_list:
        objects=[]
        for obj in object_list["Contents"]:
           objects.append({"Key": obj["Key"]})
        print(objects)
    
