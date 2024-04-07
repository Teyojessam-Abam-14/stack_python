#!/usr/bin/python
import boto3,sys,json,os
from s3_boto3 import create_s3_bucket, delete_s3_bucket, upload_file_to_s3, empty_s3_bucket, list_s3_bucket
from s3_boto3 import enable_bucket_versioning, disable_bucket_versioning, object_lock, enable_access_logging
from s3_boto3 import enable_s3_bucket_KMS_encryption, disable_s3_bucket_encryption, configure_static_website_hosting
from s3_boto3 import update_bucket_policy_for_obj_logging, enable_object_logging_via_cloudtrail, upload_file_to_s3_website
from s3_boto3 import configure_static_website_hosting, update_bucket_policy_to_s3_website
from s3_boto3 import add_policy_to_s3_eng_role, put_replication_rule_to_source_bucket, add_policy_to_dest_bucket


if __name__=="__main__": 
 #s3_function=sys.argv[1]

 #Calling STS service
 sts_client=boto3.client('sts')
 
 #Assuming the Engineering role in Development1 account (role must already exist, have stack_programmatic_access trust policy, as well as have admin access)
 assumed_role_object_eng=sts_client.assume_role(
    RoleArn="arn:aws:iam::721636561061:role/Engineer",
    RoleSessionName="EngineerAtDevelopment1"
 )
 
 #Assuming a ManagementDev role in a Management account (role must already exist, have stack_programmatic_access trust policy, as well as have admin access)
 assumed_role_object_managedev=sts_client.assume_role(
    RoleArn="arn:aws:iam::529184592602:role/ManagementDev", 
    RoleSessionName="ManagementDevAtManagment"
 )
 
 #Referencing credentials of assumed roles
 eng_credentials=assumed_role_object_eng['Credentials']
 managedev_credentials=assumed_role_object_managedev['Credentials']
 
 #Calling the IAM service using assumed roles credentials 
 iam_eng=boto3.client('iam', aws_access_key_id=eng_credentials['AccessKeyId'], aws_secret_access_key=eng_credentials['SecretAccessKey'], aws_session_token=eng_credentials['SessionToken'], region_name='us-east-1')
 
 #Calling the S3 service using assumed roles credentials
 #Eng (source) role
 s3_eng=boto3.client('s3', aws_access_key_id=eng_credentials['AccessKeyId'], aws_secret_access_key=eng_credentials['SecretAccessKey'], aws_session_token=eng_credentials['SessionToken'], region_name='us-east-1')
 
 #ManageDev (dest) role
 s3_managedev=boto3.client('s3', aws_access_key_id=managedev_credentials['AccessKeyId'], aws_secret_access_key=managedev_credentials['SecretAccessKey'], aws_session_token=managedev_credentials['SessionToken'], region_name='us-east-1')
 
 #Variables
 source_bucket_name='boto3-teejay-source'
 dest_bucket_name='boto3-teejay-dest'
 file_paths=['./s3_file_for_upload.txt', './s3_file_for_upload_2.txt']
 object_name='obj'
 
 
 #Create source bucket
 create_s3_bucket(s3_eng, source_bucket_name)
 
 #Create dest bucket
 create_s3_bucket(s3_managedev, dest_bucket_name)
 
 #Enable versioning for source and dest buckets
 enable_bucket_versioning(s3_eng, source_bucket_name)
 enable_bucket_versioning(s3_managedev, dest_bucket_name)
 
 #Adding S3 replication permissions to Engineering (source) role
 add_policy_to_s3_eng_role(iam_eng, source_bucket_name, dest_bucket_name)
 
 #Attaching a replication rule to the source bucket that will allow replication to the destination bucket
 put_replication_rule_to_source_bucket(s3_eng, source_bucket_name, dest_bucket_name)
 
 #Adding S3 bucket policy to destination bucket to allow replication
 add_policy_to_dest_bucket(s3_managedev, dest_bucket_name)
 
 #Upload files to source bucket
 upload_file_to_s3(s3_eng, file_paths, source_bucket_name, object_name)
