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
    create_s3_bucket(s3, '{}-access-logs'.format(bucket_name))
    
    #Defining and assdding bucket policy to write logs into target bucket
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "s3.amazonaws.com"
                },
                "Action": "s3:PutObject",
                "Resource": "arn:aws:s3:::{}/logs/*".format('{}-access-logs'.format(bucket_name)),
                "Condition": {
                    "StringEquals": {
                        "s3:x-amz-acl": "bucket-owner-full-control"
                    }
                }
            }
        ]
    }
    
    s3.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(bucket_policy)
    )
    
    #Define logging configuration
    logging_config={
        'LoggingEnabled': {
            'TargetBucket': '{}-access-logs'.format(bucket_name),
            'TargetPrefix': 'logs/'
        }
    }

    s3.put_bucket_logging(
        Bucket=bucket_name,
        BucketLoggingStatus=logging_config
    )


#Add bucket policy for object logging via CloudTrail
def update_bucket_policy(s3, bucket_name, account_id):

    # Define the bucket policy
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AWSCloudTrailAclCheck20150319",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudtrail.amazonaws.com"
                },
                "Action": "s3:GetBucketAcl",
                "Resource": "arn:aws:s3:::{}".format(bucket_name)
            },
            {
                "Sid": "AWSCloudTrailWrite20150319",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudtrail.amazonaws.com"
                },
                "Action": "s3:PutObject",
                "Resource": "arn:aws:s3:::{}/AWSLogs/{}/*".format(bucket_name, account_id),
                "Condition": {
                    "StringEquals": {
                        "s3:x-amz-acl": "bucket-owner-full-control"
                    }
                }
            }
        ]
    }

    # Convert the bucket policy to a JSON string
    bucket_policy_json = json.dumps(bucket_policy)

    # Set the bucket policy
    s3.put_bucket_policy(
        Bucket=bucket_name,
        Policy=bucket_policy_json
    )
    
#Enable object-level logging via CloudTrail
def enable_object_logging_via_cloudtrail(cloudtrail_client, bucket_name):
    # Define the CloudTrail trail name
    trail_name="object-level-logging-trail-for-{}".format(bucket_name)

    # Create CloudTrail logs for existing S3 bucket
    cloudtrail_client.create_trail(
        Name=trail_name,
        S3BucketName=bucket_name,
        IsMultiRegionTrail=True,  # Enable multi-region trail for cross-region logs
        EnableLogFileValidation=True
    )

    # Start the CloudTrail trail
    cloudtrail_client.start_logging(Name=trail_name)
    
#Upload files to S3 website
def upload_file_to_s3_website(s3, file, bucket_name, object_name):
    s3.upload_file(file, bucket_name, object_name, ExtraArgs={'ContentType': 'text/html'})
    
#Add all S3 bucket policies
def update_bucket_policy_to_s3_website(s3, bucket_name):

    # Define the bucket policy
    bucket_policy = {
          "Id": "Policy1712440716296",
          "Version": "2012-10-17",
          "Statement": [
             {
              "Sid": "Stmt1712440604300",
              "Action": "s3:*",
              "Effect": "Allow",
              "Resource": "arn:aws:s3:::{}/*".format(bucket_name),
              "Principal": "*"
            }
          ]
       }   


    # Convert the bucket policy to a JSON string
    bucket_policy_json = json.dumps(bucket_policy)

    # Set the bucket policy
    s3.put_bucket_policy(
        Bucket=bucket_name,
        Policy=bucket_policy_json
    )
    
#Configure static website hosting
def configure_static_website_hosting(s3, bucket_name, index_document):
        
    #Upload index file if haven't already
    upload_file_to_s3_website(s3, index_document, bucket_name, 'index.html')
    
    # Configure the bucket for static website hosting
    website_config={
        'IndexDocument': {'Suffix': 'index.html'}
    }

    s3.put_bucket_website(
        Bucket=bucket_name, 
        WebsiteConfiguration=website_config
    )
    


    

    