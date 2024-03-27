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