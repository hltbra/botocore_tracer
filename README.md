# botocore_tracer

Record botocore calls dynamically for auditing. This can be useful to see all AWS calls made from your app and also create tighter IAM policies.

## Use cases

### Test Suites
Inject `botocore_tracer.install()` into test suites to audit AWS calls and gain confidence on what's necessary for a production enviroment. This works well if you have an extensive test suite, but you'll have to filter out some noise (setup/teardown might make extra AWS calls).

### Development/Staging Environments
* Inject `botocore_tracer.install()` into your development/staging environments and record AWS calls over time, then analyze the `botocore_tracer--XXX.json` files.


## Examples using boto3

The following example uses `moto` to avoid creating resources in a real AWS account, but `botocore_tracer` works without `moto`.
```python
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
```

Output of `PYTHONPATH=. python examples/boto3calls.py`:
```json
{
  "_run_id": "1523e67f-16e0-4b2a-9897-678b9d601f6b",
  "_datetime": "2020-06-09T22:47:20",
  "output": {
    "examples/boto3calls.py:10": [
      [
        "s3:ListBuckets",
        "https://s3.amazonaws.com/",
        []
      ]
    ],
    "examples/boto3calls.py:11": [
      [
        "s3:CreateBucket",
        "https://test-bucket.s3.amazonaws.com/",
        []
      ]
    ],
    "examples/boto3calls.py:15": [
      [
        "ec2:RunInstances",
        "https://ec2.us-west-2.amazonaws.com/",
        [
          [
            "Action",
            "RunInstances"
          ],
          [
            "Version",
            "2016-11-15"
          ],
          [
            "ImageId",
            "ami-123"
          ],
          [
            "MinCount",
            "1"
          ],
          [
            "MaxCount",
            "2"
          ],
          [
            "ClientToken",
            "c29a492e-75bc-4be7-92b3-32d75f15340f"
          ]
        ]
      ]
    ]
  }
}
```