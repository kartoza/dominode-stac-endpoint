from typing import Any
from django.core.management.base import BaseCommand
import json
from ...minio_client.crawl_collection import CrawlAllCollections
import pystac
import os
from ...helpers import getItemsSpatial
import pandas as pd
import datetime
from ...minio_client.client import client


class Command(BaseCommand):
    help = 'Index collection'
    def handle(self, *args: Any, **options: Any):
        crawl = CrawlAllCollections()
        folder_structure = crawl.mapCollection()
        print(folder_structure)

        for collection in folder_structure:

            collection_name = collection["collection_name"]

            spatialArr = getItemsSpatial(folder_structure=collection["items"], collection_name=collection_name)
            spatial_extent = pystac.SpatialExtent(bboxes=[spatialArr["bbox"]])
            collection_interval = [pd.to_datetime(datetime.date.today(), infer_datetime_format=True), None]
            temporal_extent = pystac.TemporalExtent(intervals=[collection_interval])
            collection_extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
            
            collection = pystac.Collection(
                id=collection_name,
                description="sample description of collection",
                extent=collection_extent,
                license="",
                href=f"{os.getenv('URL')}/stac/collections/{collection_name}/"
            )

            collection.add_link(pystac.Link.item(f"{os.getenv('URL')}/stac/collections/{collection_name}/items/"))

            full_path = os.path.realpath(__file__)
            dir_path = (os.path.dirname(full_path))
            file_path = f'{dir_path}/tmp/collection/index.json'

            with open(file_path, 'w') as fp:
                json.dump(collection.to_dict(), fp, indent=4)

            # Upload data with progress bar.
            result = client.fput_object(
                "dominode", f"stac/{collection_name}/index.json", file_path
            )

            os.remove(file_path)
        self.stdout.write('Collections has been indexed successfully')