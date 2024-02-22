import json
import os
import rasterio
from shapely.geometry import Polygon, mapping
import pathlib
from .minio_client.client import client
import pystac
import pandas as pd
from tempfile import TemporaryDirectory
import pathlib
import datetime
import laspy
from shapely.geometry import box
import geopandas
import xml.etree.ElementTree as ET
import xmltodict
from .minio_client.crawl_catalog import CrawlCatalog
from .minio_client.map_catalog import MapIndex
from .minio_client.crawl_collection import CrawlAllCollections
from .helpers import createStacItem, createCollection

def indexCatalog():
    crawl = CrawlCatalog()
    folder_structure = crawl.mapCatalog()

    map_index = MapIndex()
    index = map_index.mapCatalog()
    
    if len(index) > 0:
        print('Index.json exists')      
        
        str = "/"
        file_path = str.join(index)
        response = client.get_object("dominode", file_path)
        data = json.load(response)
        
        indexArr = []
        notIndexedArr = []
        
        for link in data["links"]:
            if link["rel"] == "child":
                url = link["href"]
                folder = url.rsplit('/',2)[1:][0]
                indexArr.append(folder)

        for folder in folder_structure:
            if folder not in indexArr:
                notIndexedArr.append(folder)
        
        if len(notIndexedArr) > 0:
            updated_catalog = pystac.Catalog.from_dict(data)
            for folder in notIndexedArr:
                updated_catalog.add_link(pystac.Link.child(f"{os.getenv('URL')}/stac/collections/{folder}/"))
            full_path = os.path.realpath(__file__)
            dir_path = (os.path.dirname(full_path))
            file_path = f'{dir_path}/tmp/catalog/index.json'

            with open(file_path, 'w') as fp:
                json.dump(updated_catalog.to_dict(), fp, indent=4)

            # Upload data with progress bar.
            result = client.fput_object(
                "dominode", "stac/index.json", file_path
            )

            os.remove(file_path)
    else:
        catalog = pystac.Catalog(id="Dominode", description="Dominode Catalog")
        catalog.add_link(pystac.Link.root(f"{os.getenv('URL')}/stac/"))
        for folder in folder_structure:
            catalog.add_link(pystac.Link.child(f"{os.getenv('URL')}/stac/collections/{folder}/"))
        
        full_path = os.path.realpath(__file__)
        dir_path = (os.path.dirname(full_path))
        file_path = f'{dir_path}/tmp/catalog/index.json'

        with open(file_path, 'w') as fp:
            json.dump(catalog.to_dict(), fp, indent=4)

        # Upload data with progress bar.
        result = client.fput_object(
            "dominode", "stac/index.json", file_path
        )

        os.remove(file_path)
        print('Catalog has been indexed successfully')


def indexCollection():

    crawl = CrawlAllCollections()
    folder_structure = crawl.mapCollection()
    print(folder_structure)

    for collection in folder_structure:

        collection_name = collection["collection_name"]
        itemsArr = collection["items"]

        map_index = MapIndex()
        index = map_index.mapItemCollection(collection_name)

        if len(index) > 0:
            print('index.json exists')
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

                _collection = createCollection(collection, collection_name)

                full_path = os.path.realpath(__file__)
                dir_path = (os.path.dirname(full_path))
                file_path = f'{dir_path}/tmp/collection/index.json'

                with open(file_path, 'w') as fp:
                    json.dump(_collection.to_dict(), fp, indent=4)

                # Upload data with progress bar.
                result = client.fput_object(
                    "dominode", f"stac/{collection_name}/index.json", file_path
                )

                os.remove(file_path)


        else:
            _collection = createCollection(collection, collection_name)

            full_path = os.path.realpath(__file__)
            dir_path = (os.path.dirname(full_path))
            file_path = f'{dir_path}/tmp/collection/index.json'

            with open(file_path, 'w') as fp:
                json.dump(_collection.to_dict(), fp, indent=4)

            # Upload data with progress bar.
            result = client.fput_object(
                "dominode", f"stac/{collection_name}/index.json", file_path
            )

            os.remove(file_path)
    print('Collections has been indexed successfully')


def indexItemCollection():
    crawl = CrawlAllCollections()
    folder_structure = crawl.mapCollection()
    
    for collection in folder_structure:

        collection_name = collection["collection_name"]
        itemsArr = collection["items"]

        map_index = MapIndex()
        index = map_index.mapItemCollection(collection_name)

        if len(index) > 0:
            print('index.json exists')
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
    print('Item collection has been indexed successfully')


def indexItem():
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
                print('index.json exists')
            else:
                itemsNotIndexed.append(item_name)
            
        print(f"items not indexed {itemsNotIndexed}")

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
                print(str(_file_path))

                with open(_file_path, 'w') as fp:
                    json.dump(feature, fp, indent=4)

                client.fput_object(
                    "dominode", f"stac/{_collection_name}/items/{item_name}/index.json", _file_path
                )

                os.remove(_file_path)

    print('Item collection has been indexed successfully')