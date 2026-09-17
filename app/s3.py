import boto3, os
from botocore.exceptions import ClientError

BUCKET = os.getenv("S3_BUCKET", "notemind-uploads-roy2026")
s3 = boto3.client("s3")   # on EC2 with the role attached, boto3 finds credentials automatically via the instance metadata service — no keys in code

def upload_file(key: str, file_bytes: bytes, content_type: str) -> None:
    s3.put_object(Bucket=BUCKET, Key=key, Body=file_bytes, ContentType=content_type)

def presigned_url(key: str, expires_in: int = 3600) -> str:
    return s3.generate_presigned_url(
        "get_object", Params={"Bucket": BUCKET, "Key": key}, ExpiresIn=expires_in
    )