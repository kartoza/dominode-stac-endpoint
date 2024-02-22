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
            itemsNotIndexed = []

            for item in itemsArr:
                item_name = item["item_name"]
                map_index = MapIndex()
                index = map_index.mapItem(collection_name, item_name)

                if len(index) > 0:
                    self.stdout.write('index.json exists')
                else:
                    itemsNotIndexed.append(item_name)
                
            self.stdout.write(f"items not indexed {itemsNotIndexed}")

            if len(itemsNotIndexed) > 0:
                collection_items = []

                for folder in itemsArr:

                    if folder["item_name"] in itemsNotIndexed:
                        collection_item = createStacItem(assets=folder["assets"], item_name=folder["item_name"], collection_name=collection_name)
                        collection_items.append(collection_item)
                    
                collection = pystac.ItemCollection(collection_items)
                collection_dict = collection.to_dict()
                features = collection_dict["features"]
                
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