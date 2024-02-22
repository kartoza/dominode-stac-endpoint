from .client import client
from ..helpers import convertToList

class CrawlCatalog():

    def mapCatalog(self):
        response = client.list_objects('dominode', prefix="stac", recursive=True)
        catalogArr = []
        for obj in response:
            object_name = obj.object_name
            li = convertToList(object_name)
            if "index.json" not in li:
                if li[1] not in catalogArr:
                    catalogArr.append(li[1])
        return catalogArr
            