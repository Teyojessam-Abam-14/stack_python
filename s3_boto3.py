#!/usr/bin/python
import boto3,sys,json,os

#Create Source Bucket
def create_s3_bucket_source(s3,bucket_name):
    s3.create_bucket(
        Bucket=bucket_name,
        ObjectLockEnabledForBucket=False
    )
    
#Create Destination Bucket 
def create_s3_bucket_dest(s3,bucket_name,region):
    s3.create_bucket(
        Bucket=bucket_name,
        ObjectLockEnabledForBucket=False,
        CreateBucketConfiguration={
        'LocationConstraint': '{}'.format(region),
      }
    )
#NB: Only specify 'LocationConstraint' when using another region that is not the default region

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
def update_bucket_policy_for_obj_logging(s3, bucket_name, account_id):

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
    
#Attaching policy to S3 Engineering role
def add_policy_to_s3_eng_role(iam, source_bucket_name, dest_bucket_name):
  
  #Adding S3 replication permissions to Engineering (source) role 
  iam_policy={
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SourceBucketPermissions",
      "Effect": "Allow",
      "Action": [
        "s3:GetObjectRetention",
        "s3:GetObjectVersionTagging",
        "s3:GetObjectVersionAcl",
        "s3:ListBucket",
        "s3:GetObjectVersionForReplication",
        "s3:GetObjectLegalHold",
        "s3:GetReplicationConfiguration"
      ],
      "Resource": [
        "arn:aws:s3:::{}/*".format(source_bucket_name),
        "arn:aws:s3:::{}".format(source_bucket_name)
      ]
    },
    {
      "Sid": "DestinationBucketPermissions",
      "Effect": "Allow",
      "Action": [
        "s3:ReplicateObject",
        "s3:ObjectOwnerOverrideToBucketOwner",
        "s3:GetObjectVersionTagging",
        "s3:ReplicateTags",
        "s3:ReplicateDelete"
      ],
      "Resource": [
        "arn:aws:s3:::{}/*".format(dest_bucket_name)
      ]
     }
    ]
 }
    
  #Convert the IAM policy to a JSON string
  iam_policy_json = json.dumps(iam_policy)
    
  #Set the IAM policy
  iam.put_role_policy(
    RoleName='Engineer',
    PolicyName='S3ReplicationPermissions',
    PolicyDocument=iam_policy_json
   )
    
#Attaching a replication rule to the source bucket that will allow replication to the destination bucket
def put_replication_rule_to_source_bucket(s3, source_bucket_name, dest_bucket_name):
    
    #Defining the replication rule (from source bucket to destination bucket)
    bucket_rule={
    "Role": "arn:aws:iam::721636561061:role/Engineer",
    "Rules": [
      {
        "Status": "Enabled",
        "Priority": 10,
        "DeleteMarkerReplication": {
          "Status": "Disabled"
        },
        "Filter": {
          "Prefix": ""
        },
        "Destination": {
          "Bucket": "arn:aws:s3:::{}".format(dest_bucket_name)
        }
      }
     ]
    }
    
    
    #Setting the rule to the source bucket
    s3.put_bucket_replication(
    Bucket=source_bucket_name,
    ReplicationConfiguration=bucket_rule
    ) 

#Attaching policy to destination bucket
def add_policy_to_dest_bucket(s3, dest_bucket_name):
    
    #Adding S3 bucket policy to destination bucket to allow replication
    bucket_policy={
    "Version": "2012-10-17",
    "Id": "PolicyForDestinationBucket",
    "Statement": [
         {
      "Sid": "ReplicationPermissions",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::721636561061:role/Engineer"
        },
      "Action": [
        "s3:ReplicateDelete",
        "s3:ReplicateObject",
        "s3:ObjectOwnerOverrideToBucketOwner",
        "s3:GetBucketVersioning",
        "s3:PutBucketVersioning"
        ],
      "Resource": [
        "arn:aws:s3:::{}/*".format(dest_bucket_name),
        "arn:aws:s3:::{}".format(dest_bucket_name)
        ]  
      }
     ]
    }
    
    # Convert the bucket policy to a JSON string
    bucket_policy_json = json.dumps(bucket_policy)

    # Set the bucket policy
    s3.put_bucket_policy(
        Bucket=dest_bucket_name,
        Policy=bucket_policy_json
    )
    
    
   
    






    

    


   