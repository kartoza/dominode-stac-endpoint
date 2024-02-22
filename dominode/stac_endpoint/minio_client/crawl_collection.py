from .client import client
from ..helpers import convertToList
    
class CrawlAllCollections():
    
    def mapCollection(self):
        response = client.list_objects('dominode', prefix="stac", recursive=True)
        collectionArr = []
        for obj in response:
            object_name = obj.object_name
            li = convertToList(object_name)
            
            if "index.json" not in li:
                if not any(x['collection_name'] == li[1] for x in collectionArr):
                    newArr = {"collection_name": li[1], "items": [{"item_name": li[3], "assets": [li[4]]}]}
                    collectionArr.append(newArr)
                else:
                    index = [i for i,_ in enumerate(collectionArr) if _['collection_name'] == li[1]][0]
                    itemArr = collectionArr[index]["items"]
                    if not any(x['item_name'] == li[3] for x in itemArr):
                        newArr = {"item_name": li[3], "assets": [li[4]]}
                        itemArr.append(newArr)
                    else:
                        index = [i for i,_ in enumerate(itemArr) if _['item_name'] == li[3]][0]
                        itemArr[index]["assets"].append(li[4])
                    
        return collectionArr