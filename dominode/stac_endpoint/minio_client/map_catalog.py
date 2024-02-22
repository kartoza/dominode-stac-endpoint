from .client import client
from ..helpers import convertToList
    
class MapIndex():
    
    def mapIndex(self):
        response = client.list_objects('dominode', prefix="stac", recursive=True)
        indexArr = []
        for obj in response:
            object_name = obj.object_name
            li = convertToList(object_name)
            if "index.json" in li:
                indexArr.append(li)
        return indexArr
    
    def mapCatalog(self):
        response = client.list_objects('dominode', prefix="stac", recursive=True)
        indexArr = []
        for obj in response:
            object_name = obj.object_name
            li = convertToList(object_name)
            if "index.json" in li:
                indexArr.append(li)
        return indexArr[0]
    
    def mapCollection(self, collection_name):
        response = client.list_objects('dominode', prefix="stac", recursive=True)
        collectionArr = []
        for obj in response:
            object_name = obj.object_name
            li = convertToList(object_name)
            if len(li) == 3:
                if "index.json" in li and li[1] == collection_name:
                    collectionArr.append(li)
        return collectionArr[0]
    

    def mapItemCollection(self, collection_name):
        response = client.list_objects('dominode', prefix="stac", recursive=True)
        collectionArr = []
        for obj in response:
            object_name = obj.object_name
            li = convertToList(object_name)
            if len(li) == 4:
                if "index.json" in li and li[1] == collection_name:
                    collectionArr.append(li)
        return collectionArr[0]
    
    def mapItem(self, collection_name, item_name):
        response = client.list_objects('dominode', prefix="stac", recursive=True)
        collectionArr = []
        for obj in response:
            object_name = obj.object_name
            li = convertToList(object_name)
            if len(li) == 5:
                print(li)
                if "index.json" in li and li[1] == collection_name and li[3] == item_name:
                    collectionArr.append(li)
        return collectionArr[0]

