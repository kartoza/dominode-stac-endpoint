from typing import Any
from django.core.management.base import BaseCommand
from ...stac_helpers import indexCatalog, indexCollection, indexItemCollection, indexItem
from ...minio_client.client import client


class Command(BaseCommand):
    help = 'Index STAC'
    def handle(self, *args: Any, **options: Any):

        indexCatalog()
        indexCollection()
        indexItemCollection()
        indexItem()

        self.stdout.write('Item collection has been indexed successfully')