import botocore_tracer
import boto3
import moto

botocore_tracer.install(stdout=True)


with moto.mock_s3():
    s3 = boto3.client('s3', 'us-east-1')
    s3.list_buckets()
    s3.create_bucket(Bucket='test-bucket')

with moto.mock_ec2():
    ec2 = boto3.client('ec2', 'us-west-2')
    ec2.run_instances(ImageId='ami-123', MinCount=1, MaxCount=2)
