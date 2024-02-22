from typing import Any
from django.core.management.base import BaseCommand
import json
from ...minio_client.crawl_catalog import CrawlCatalog
import pystac
import os
from ...minio_client.client import client


class Command(BaseCommand):
    help = 'Index catalog'
    def handle(self, *args: Any, **options: Any):
        crawl = CrawlCatalog()
        folder_structure = crawl.mapCatalog()
        catalog = pystac.Catalog(id="Dominode", description="Dominode Catalog")
        catalog.add_link(pystac.Link.root(f"{os.getenv('URL')}/stac/catalog/"))
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