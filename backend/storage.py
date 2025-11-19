import boto3
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime, timedelta

load_dotenv()

class StorageService:
    """S3-compatible storage service for videos and thumbnails"""
    
    def __init__(self):
        # Use MinIO for development, S3 for production
        self.use_s3 = os.getenv("USE_S3", "false").lower() == "true"
        self.endpoint_url = os.getenv("S3_ENDPOINT_URL")  # For MinIO
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "cricket-videos")
        self.region = os.getenv("S3_REGION", "us-east-1")
        
        # Initialize client
        if self.use_s3:
            self.client = boto3.client(
                's3',
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region
            )
        else:
            # MinIO configuration
            self.client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url or "http://localhost:9000",
                aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
                aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
                region_name=self.region
            )
        
        # Ensure bucket exists
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """Create bucket if it doesn't exist"""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            try:
                if self.use_s3:
                    self.client.create_bucket(Bucket=self.bucket_name)
                else:
                    # MinIO requires LocationConstraint
                    self.client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.region}
                    )
            except ClientError as e:
                print(f"Error creating bucket: {e}")
    
    def upload_file(self, file_obj: BinaryIO, filename: str, content_type: str = "video/mp4") -> str:
        """Upload a file to S3 and return the S3 key"""
        # Generate unique key
        file_ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        s3_key = f"videos/{datetime.now().strftime('%Y/%m/%d')}/{unique_filename}"
        
        try:
            self.client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': content_type}
            )
            return s3_key
        except ClientError as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for uploading"""
        try:
            url = self.client.generate_presigned_url(
                'put_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key, 'ContentType': 'video/mp4'},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
    
    def get_presigned_download_url(self, s3_key: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for downloading"""
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate download URL: {str(e)}")
    
    def delete_file(self, s3_key: str) -> bool:
        """Delete a file from S3"""
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            print(f"Error deleting file: {e}")
            return False
    
    def file_exists(self, s3_key: str) -> bool:
        """Check if a file exists in S3"""
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False

# Global instance
storage_service = StorageService()

