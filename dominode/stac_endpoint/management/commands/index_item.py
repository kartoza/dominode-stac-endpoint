from typing import Any
from django.core.management.base import BaseCommand
import json
from ...minio_client.crawl_collection import CrawlAllCollections
import pystac
import os
from ...helpers import createStacItem
from ...minio_client.client import client
import pprint


class Command(BaseCommand):
    help = 'Index item collection'
    def handle(self, *args: Any, **options: Any):

        crawl = CrawlAllCollections()
        folder_structure = crawl.mapCollection()
        
        for collection in folder_structure:

            collection_name = collection["collection_name"]
            itemsArr = collection["items"]
            
            collection_items = []

            for folder in itemsArr:

                collection_item = createStacItem(assets=folder["assets"], item_name=folder["item_name"], collection_name=collection_name)
                collection_items.append(collection_item)
                
            collection = pystac.ItemCollection(collection_items)
            collection_dict = collection.to_dict()
            features = collection_dict["features"]
            pp = pprint.PrettyPrinter(width=41, compact=True)
            
            for feature in features:
                item_name = feature["id"]
                _collection_name = feature["collection"]

                _full_path = os.path.realpath(__file__)
                _dir_path = (os.path.dirname(_full_path))
                _file_path = f'{_dir_path}/tmp/item/index.json'
                self.stdout.write(str(_file_path))

                with open(_file_path, 'w') as fp:
                    json.dump(feature, fp, indent=4)

                client.fput_object(
                    "dominode", f"stac/{_collection_name}/items/{item_name}/index.json", _file_path
                )

                os.remove(_file_path)

        self.stdout.write('Item collection has been indexed successfully')