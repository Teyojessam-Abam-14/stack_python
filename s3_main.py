#!/usr/bin/python
import boto3,sys,json,os
from s3_boto3 import create_s3_bucket, upload_file_to_s3, empty_s3_bucket

if __name__=="__main__": 
 #s3_function=sys.argv[1]

 #Calling STS service
 sts_client=boto3.client('sts')
 
 #Assuming the Engineering role in Development1 account
 assumed_role_object=sts_client.assume_role(
    RoleArn="arn:aws:iam::721636561061:role/Engineer",
    RoleSessionName="EngineerAtDevelopment1"
 )
 
 #Referencing credentials of assumed role
 credentials=assumed_role_object['Credentials']

 #Calling the S3 service using assumed role credentials
 s3=boto3.client('s3', aws_access_key_id=credentials['AccessKeyId'], aws_secret_access_key=credentials['SecretAccessKey'], aws_session_token=credentials['SessionToken'], region_name='us-east-1')
 
 #Variables
 bucket_name='teejay-3'
 file_path='./s3_file_for_upload.txt'
 object_name='S3 file'
 
 #Emptying bucket
 empty_s3_bucket(s3,bucket_name)
 
 #Calling create bucket function
 
 
 
