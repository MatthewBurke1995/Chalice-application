import boto3
import json

# Replace these values with your AWS credentials and region
region_name = 'YOUR_REGION_NAME'

# Initialize the S3 client
session = boto3.Session(profile_name='default')
s3 = session.client('s3')

# Name of the bucket you want to create
bucket_name = 'bayesian-soccer-traces-matthew-burke'

# Create the bucket
try:
    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'us-east-2'})
except:
    print('bucket alread exists')

# Define the bucket policy to allow public read access
bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*"
        }
    ]
}

# Convert the bucket policy to JSON format
bucket_policy_json = json.dumps(bucket_policy)

# Apply the bucket policy
s3.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy_json)

print(f"Bucket '{bucket_name}' created with public read permissions.")
