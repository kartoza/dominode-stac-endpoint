from typing import Any
from django.core.management.base import BaseCommand
import json
from ...minio_client.crawl_collection import CrawlAllCollections
from ...minio_client.map_catalog import MapIndex
import pystac
import os
from ...helpers import createStacItem
from ...minio_client.client import client


class Command(BaseCommand):
    help = 'Index item collection'
    def handle(self, *args: Any, **options: Any):

        crawl = CrawlAllCollections()
        folder_structure = crawl.mapCollection()
        
        for collection in folder_structure:

            collection_name = collection["collection_name"]
            itemsArr = collection["items"]

            map_index = MapIndex()
            index = map_index.mapItemCollection(collection_name)

            if len(index) > 0:
                self.stdout.write('index.json exists')
                str = "/"
                file_path = str.join(index)
                response = client.get_object("dominode", file_path)
                data = json.load(response)

                # check for new items
                featuresArr = data["features"] 
                featuresIndex = []
                featuresNotIndexed = []
                for feature in featuresIndex:
                    featuresIndex.append(feature["id"])

                for item in itemsArr:
                    if item["item_name"] not in featuresIndex:
                        featuresNotIndexed.append(item)

                if len(featuresNotIndexed) > 0:
                    collection_items = []

                    for folder in featuresNotIndexed:

                        collection_item = createStacItem(assets=folder["assets"], item_name=folder["item_name"], collection_name=collection_name)
                        collection_items.append(collection_item)
                    
                        collection = pystac.ItemCollection(collection_items)

                        full_path = os.path.realpath(__file__)
                        dir_path = (os.path.dirname(full_path))
                        file_path = f'{dir_path}/tmp/item_collection/index.json'

                        with open(file_path, 'w') as fp:
                            json.dump(collection.to_dict(), fp, indent=4)

                        # Upload data with progress bar.
                        result = client.fput_object(
                            "dominode", f"stac/{collection_name}/items/index.json", file_path
                        )

                        os.remove(file_path)
            
            else:
                collection_items = []

                for folder in itemsArr:

                    collection_item = createStacItem(assets=folder["assets"], item_name=folder["item_name"], collection_name=collection_name)
                    collection_items.append(collection_item)
                
                collection = pystac.ItemCollection(collection_items)

                full_path = os.path.realpath(__file__)
                dir_path = (os.path.dirname(full_path))
                file_path = f'{dir_path}/tmp/item_collection/index.json'

                with open(file_path, 'w') as fp:
                    json.dump(collection.to_dict(), fp, indent=4)

                # Upload data with progress bar.
                result = client.fput_object(
                    "dominode", f"stac/{collection_name}/items/index.json", file_path
                )

                os.remove(file_path)
        self.stdout.write('Item collection has been indexed successfully')