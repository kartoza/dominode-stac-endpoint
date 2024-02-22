from typing import Any
from django.core.management.base import BaseCommand
import json
from ...minio_client.crawl_catalog import CrawlCatalog
from ...minio_client.map_catalog import MapIndex
import pystac
import os
from ...minio_client.client import client


class Command(BaseCommand):
    help = 'Index catalog'
    def handle(self, *args: Any, **options: Any):

        crawl = CrawlCatalog()
        folder_structure = crawl.mapCatalog()

        map_index = MapIndex()
        index = map_index.mapCatalog()
        self.stdout.write(f"crawl catalog {index}")
        
        if len(index) > 0:
            self.stdout.write('Index.json exists')      
            
            str = "/"
            file_path = str.join(index)
            response = client.get_object("dominode", file_path)
            data = json.load(response)
            self.stdout.write(f"crawl catalog {folder_structure}")
            
            indexArr = []
            notIndexedArr = []
            
            for link in data["links"]:
                if link["rel"] == "child":
                    url = link["href"]
                    folder = url.rsplit('/',2)[1:][0]
                    self.stdout.write(f"folder split {folder}")
                    indexArr.append(folder)

            for folder in folder_structure:
                if folder not in indexArr:
                    notIndexedArr.append(folder)
            
            if len(notIndexedArr) > 0:
                updated_catalog = pystac.Catalog.from_dict(data)
                for folder in notIndexedArr:
                    updated_catalog.add_link(pystac.Link.child(f"{os.getenv('URL')}/stac/collections/{folder}/"))
                print(updated_catalog.to_dict())
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
            self.stdout.write('Catalog has been indexed successfully')