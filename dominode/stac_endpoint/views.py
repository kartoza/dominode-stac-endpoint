import json
from rest_framework.response import Response
from rest_framework.decorators import api_view
from minio import Minio
from minio.error import S3Error


client = Minio(
    'api.minio.do.kartoza.com', 
    access_key='TlL5eQVvBUXkcY7NQl2J',
    secret_key='5OlXF6ZEKJNQSrzwx7gQCOD9OgcovQgF7OxObdps', 
)

# Create catalog
@api_view(['GET'])
def catalog(request):
    objects = client.list_objects('dominode')
    for obj in objects:
        print(obj)
    return Response({"status": 200})

# Create collection
@api_view(['GET'])
def collections(request):
    return Response({"status": 200})

# Create item collection
@api_view(['GET'])
def item_collection(request, collection_name):
    return Response({"status": 200})

#Create Item
@api_view(['GET'])
def item(request, collection_name, item_name):
    return Response({"status": 200})