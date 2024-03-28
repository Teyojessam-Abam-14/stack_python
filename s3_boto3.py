#!/usr/bin/python
import boto3,sys,json,os

#Create Bucket
def create_s3_bucket(s3,bucket_name):
    s3.create_bucket(
        Bucket=bucket_name,
        ObjectLockEnabledForBucket=False
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
        
#Object locking
def object_lock(s3, new_object_lock_bucket):
#Created a new bucket where Object Locking is Enabled
  create_s3_bucket(s3,new_object_lock_bucket)
  
  s3.put_object_lock_configuration(
    Bucket=new_object_lock_bucket,
    ObjectLockConfiguration={
        'ObjectLockEnabled': 'Enabled',
        'Rule': {
            'DefaultRetention': {
                'Mode': 'GOVERNANCE',
                'Days': 30
            }
        }
    }
  )
        

#Enable versioning
def enable_bucket_versioning(s3,bucket_name):
    s3.put_bucket_versioning(
        Bucket=bucket_name,
        VersioningConfiguration={
            'Status': 'Enabled'
        }
    )

#Disable versioning
def disable_bucket_versioning(s3,bucket_name):
    s3.put_bucket_versioning(
        Bucket=bucket_name,
        VersioningConfiguration={
            'Status': 'Suspended'
        }
    )
    
def enable_s3_bucket_KMS_encryption(s3,bucket_name):

    # Define the KMS encryption configuration
    default_encryption={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'aws:kms',
                    'KMSMasterKeyID': 'arn:aws:kms:us-east-1:721636561061:key/67fb8dab-60e7-46b0-986c-bbc500d80246'
                }
            }
        ]
    }
    #Apply KMS encryption
    s3.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration=default_encryption
        )

    
#Disable all S3 bucket encryption
def disable_s3_bucket_encryption(s3,bucket_name):
    s3.delete_bucket_encryption(
    Bucket=bucket_name
)
    
def enable_access_logging(s3, bucket_name):
    # Create the target bucket if haven't already
    create_s3_bucket(s3, "{}-logs".format(bucket_name))
    
    #Define logging configuration
    logging_config={
        'LoggingEnabled': {
            'TargetBucket': "{}-logs".format(bucket_name),
            'TargetPrefix': "logs/"
        }
    }

    s3.put_bucket_logging(
        Bucket=bucket_name,
        BucketLoggingStatus=logging_config
    )

