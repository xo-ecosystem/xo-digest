
import os
import boto3

def upload_to_storj(local_path, remote_filename):
    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        aws_access_key_id=os.getenv("STORJ_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("STORJ_SECRET_KEY"),
        endpoint_url=os.getenv("STORJ_ENDPOINT"),
    )
    bucket = os.getenv("STORJ_BUCKET")

    with open(local_path, "rb") as f:
        s3.upload_fileobj(f, bucket, remote_filename)
        print(f"✅ Uploaded {local_path} to Storj as {remote_filename}")

# Example test:
# upload_to_storj("public/vault/previews/message_bottle/drop_main.webp", "previews/message_bottle/drop_main.webp")