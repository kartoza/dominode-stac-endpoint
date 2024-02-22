from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
import os

load_dotenv()

client = Minio(
    os.getenv("HOST"), 
    access_key=os.getenv("ACCESS_KEY"),
    secret_key=os.getenv("SECRET_KEY"), 
)