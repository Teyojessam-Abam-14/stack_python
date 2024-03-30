#!/usr/bin/python
import boto3,sys,json,os
from s3_boto3 import create_s3_bucket, delete_s3_bucket, upload_file_to_s3, empty_s3_bucket, list_s3_bucket
from s3_boto3 import enable_bucket_versioning, disable_bucket_versioning, object_lock, enable_access_logging
from s3_boto3 import enable_s3_bucket_KMS_encryption, disable_s3_bucket_encryption
from s3_boto3 import  update_bucket_policy, enable_object_logging_via_cloudtrail


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
 
 #Calling the CloudTrail server for object-level logging
 cloudtrail_client=boto3.client('cloudtrail', aws_access_key_id=credentials['AccessKeyId'], aws_secret_access_key=credentials['SecretAccessKey'], aws_session_token=credentials['SessionToken'], region_name='us-east-1')
 
 #Variables
 bucket_name='teejay-6'
 file_paths=['./s3_file_for_upload.txt', './s3_file_for_upload_2.txt']
 object_name='S3_file'
 account_id='721636561061'
 
 #Adding bucket policy for object-logging via CloudTrail
 update_bucket_policy(s3, bucket_name, account_id)
 
 #Enabling object-logging via CloudTrail
 enable_object_logging_via_cloudtrail(cloudtrail_client, bucket_name)

 
 

 
 
 
