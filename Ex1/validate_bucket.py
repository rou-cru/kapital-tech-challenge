import os
import sys

import boto3
from botocore.exceptions import ClientError


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


if len(sys.argv) != 2:
    fail("Usage: validate_bucket.py <bucket-name>")

bucket = sys.argv[1]

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ.get("AWS_ENDPOINT_URL"),
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name=os.environ.get("AWS_DEFAULT_REGION"),
)

try:
    acl = s3.get_bucket_acl(Bucket=bucket)
except ClientError as exc:
    fail(f"Cannot read bucket ACL: {exc.response.get('Error', {}).get('Code')}")

public_grants = {
    "http://acs.amazonaws.com/groups/global/AllUsers",
    "http://acs.amazonaws.com/groups/global/AuthenticatedUsers",
}
for grant in acl.get("Grants", []):
    uri = grant.get("Grantee", {}).get("URI")
    if uri in public_grants:
        fail("Bucket ACL allows public access.")

try:
    policy = s3.get_bucket_policy(Bucket=bucket)
    if '"*"' in policy.get("Policy", ""):
        fail("Bucket policy allows public access.")
except ClientError as exc:
    code = exc.response.get("Error", {}).get("Code")
    if code != "NoSuchBucketPolicy":
        fail(f"Cannot read bucket policy: {code}")

print("OK: bucket is not public.")

try:
    encryption = s3.get_bucket_encryption(Bucket=bucket)
except ClientError as exc:
    code = exc.response.get("Error", {}).get("Code")
    if code != "ServerSideEncryptionConfigurationNotFoundError":
        fail(f"Cannot read bucket encryption: {code}")
    encryption = None

if encryption:
    rules = encryption.get("ServerSideEncryptionConfiguration", {}).get("Rules", [])
    for rule in rules:
        default = rule.get("ApplyServerSideEncryptionByDefault", {})
        if default.get("SSEAlgorithm"):
            print("OK: bucket has encryption at rest.")
            sys.exit(0)

print("ALERT: bucket missing encryption at rest. Applying default encryption.")
s3.put_bucket_encryption(
    Bucket=bucket,
    ServerSideEncryptionConfiguration={
        "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "aws:kms"}}]
    },
)
print("OK: bucket encryption applied.")
