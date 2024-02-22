import json
import unicodedata
from rest_framework.response import Response
from rest_framework.decorators import api_view
from dotenv import load_dotenv
from .minio_client.client import client
from .minio_client.map_catalog import MapIndex

load_dotenv()

# Create catalog
@api_view(['GET'])
def catalog(request):
    map_index = MapIndex()
    index = map_index.mapCatalog()
    str = "/"
    file_path = str.join(index)
    response = client.get_object("dominode", file_path)
    data = json.load(response)
    return Response(data)

# Create collection
@api_view(['GET'])
def collection(request, collection_name):

    map_index = MapIndex()
    index = map_index.mapCollection(collection_name)
    str = "/"
    file_path = str.join(index)
    response = client.get_object("dominode", file_path)
    data = json.load(response)
    return Response(data)

# Create item collection
@api_view(['GET'])
def item_collection(request, collection_name):
    map_index = MapIndex()
    index = map_index.mapItemCollection(collection_name)
    str = "/"
    file_path = str.join(index)
    response = client.get_object("dominode", file_path)
    data = json.load(response)
    return Response(data)

#Create Item
@api_view(['GET'])
def item(request, collection_name, item_name):
    map_index = MapIndex()
    index = map_index.mapItem(collection_name, item_name)
    str = "/"
    file_path = str.join(index)
    response = client.get_object("dominode", file_path)
    data = json.load(response)
    return Response(data)