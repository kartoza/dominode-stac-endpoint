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

tifExtArr = [".tif", ".TIF", ".TIFF"]
lasExtArr = [".las", ".LAS", ".laz", ".LAZ"]
parquetExtArr = [".parquet", ".PARQUET", ".geoparquet", ".GEOPARQUET"]

def convertToList(string):
    li = list(string.split("/"))
    return li


def get_bbox_and_footprint(raster):
    with rasterio.open(raster) as r:
        bounds = r.bounds
        bbox = [bounds.left, bounds.bottom, bounds.right, bounds.top]
        footprint = Polygon([
            [bounds.left, bounds.bottom],
            [bounds.left, bounds.top],
            [bounds.right, bounds.top],
            [bounds.right, bounds.bottom]
        ])
        
        return (bbox, mapping(footprint))
    
    
def createStacItem(assets, item_name, collection_name):
    isXML = False
    xmlItem = None
    isTiff = False
    tifItem = None
    isLass = False
    lassItem = None
    isParquet = False
    parquetItem = None
    dataProperties = None

    if any(".xml" in val for val in assets):
        isXML = True
        index = [idx for idx, s in enumerate(assets) if ".xml" in s ][0]
        xmlItem = assets[index]
        dataProperties = handleXML(xmlItem, collection_name, item_name)

    for item in assets:
        file_extension = pathlib.Path(item).suffix
        
        if file_extension in tifExtArr:
            isTiff = True
            tifItem = item
            break
        if file_extension in lasExtArr:
            isLass = True
            lassItem = item
            break
        if file_extension in parquetExtArr:
            isParquet = True
            parquetItem = item
            break

    if isTiff:
        collection_item = handleTif(tifItem, collection_name, item_name, dataProperties)
    if isLass:
        collection_item = handleLas(lassItem, collection_name, item_name, dataProperties)
    if isParquet:
        collection_item = handleParquet(parquetItem, collection_name, item_name, dataProperties)

    collection_item.add_link(
        pystac.Link.root(f"{os.getenv('URL')}/stac/collections/{collection_name}/items/{item_name}/")
    )
            
    for asset in assets:
        collection_item.add_asset(
            key=item_name,
            asset=pystac.Asset(
                href=f"dominode/stac/{collection_name}/items/{item_name}/{asset}"
            )
        )

    return collection_item


def handleTif(tifItem, collection_name, item_name, dataProperties):
    tmp_dir = TemporaryDirectory()
    file_path = os.path.join(tmp_dir.name, tifItem)
    response = client.fget_object("dominode", f"stac/{collection_name}/items/{item_name}/{tifItem}", file_path)
    file_extension = pathlib.Path(file_path).suffix
    bbox, footprint = get_bbox_and_footprint(file_path)

    collection_item = pystac.Item(
        id=item_name,
        geometry= footprint,
        bbox= bbox,
        datetime=pd.to_datetime(datetime.date.today(), infer_datetime_format=True),
        collection=collection_name,
        properties={
            "extra_fields": dataProperties
        }
    )

    return collection_item


def handleLas(lassItem, collection_name, item_name, dataProperties):
    tmp_dir = TemporaryDirectory()
    file_path = os.path.join(tmp_dir.name, lassItem)
    response = client.fget_object("dominode", f"stac/{collection_name}/items/{item_name}/{lassItem}", file_path)
    file_extension = pathlib.Path(file_path).suffix
    las = laspy.read(file_path)
    lasHeader = las.header
    lasPoints = las.points
    bbox = [lasHeader.x_min, lasHeader.y_min, lasHeader.x_max, lasHeader.y_max]
    footprint = Polygon(((lasHeader.x_min,lasHeader.y_min), (lasHeader.x_min,lasHeader.y_max), (lasHeader.x_max,lasHeader.y_max), (lasHeader.x_max,lasHeader.y_min)))

    collection_item = pystac.Item(
        id=item_name,
        geometry= mapping(footprint),
        bbox= bbox,
        datetime=pd.to_datetime(datetime.date.today(), infer_datetime_format=True),
        collection=collection_name,
        properties={
            "extra_fields": dataProperties
        }
    )

    return collection_item


def handleParquet(parquetItem, collection_name, item_name, dataProperties):
    tmp_dir = TemporaryDirectory()
    file_path = os.path.join(tmp_dir.name, parquetItem)
    response = client.fget_object("dominode", f"stac/{collection_name}/items/{item_name}/{parquetItem}", file_path)
    file_extension = pathlib.Path(file_path).suffix

    parquet = geopandas.read_parquet(file_path, columns=["geometry"])
    bounds = parquet.total_bounds
    footprint = box(*bounds)

    collection_item = pystac.Item(
        id=item_name,
        geometry= mapping(footprint),
        bbox=  mapping(footprint),
        datetime=pd.to_datetime(datetime.date.today(), infer_datetime_format=True),
        collection=collection_name,
        properties={
            "extra_fields": dataProperties
        }
    )

    return collection_item


def handleXML(xmlItem, collection_name, item_name):
    tmp_dir = TemporaryDirectory()
    file_path = os.path.join(tmp_dir.name, xmlItem)
    response = client.fget_object("dominode", f"stac/{collection_name}/items/{item_name}/{xmlItem}", file_path)
    file_extension = pathlib.Path(file_path).suffix

    isEsri = False
    dataProperties = None

    with open(file_path, 'r') as f:
        xmlData = f.read()

    xmlDict = xmltodict.parse(xmlData)
     
    dataProperties = xmlDict['metadata']['dataIdInfo']

    return dataProperties


def getItemsSpatial(collection_name, folder_structure):
    footprintArr = []
    bboxArr = []
    for folder in folder_structure:
        item_name = folder["item_name"]
        assets = folder["assets"]
        for item in assets:
            ext = pathlib.Path(item).suffix
            tmp_dir = TemporaryDirectory()
            file_path = os.path.join(tmp_dir.name, item)
            response = client.fget_object("dominode", f"stac/{collection_name}/items/{item_name}/{item}", file_path)
            if ext in tifExtArr:
                bbox, footprint = get_bbox_and_footprint(file_path)
                footprintArr.append(footprint)
                bboxArr.append(bbox)
            if ext in lasExtArr:
                las = laspy.read(file_path)
                lasHeader = las.header
                lasPoints = las.points
                bbox = [lasHeader.x_min, lasHeader.y_min, lasHeader.x_max, lasHeader.y_max]
                footprint = Polygon((
                    (lasHeader.x_min,lasHeader.y_min), 
                    (lasHeader.x_min,lasHeader.y_max), 
                    (lasHeader.x_max,lasHeader.y_max), 
                    (lasHeader.x_max,lasHeader.y_min)
                ))
                footprintArr.append(mapping(footprint))
                bboxArr.append(bbox)
            if ext in parquetExtArr:
                parquet = geopandas.read_parquet(file_path, columns=["geometry"])
                bounds = parquet.total_bounds
                footprint = box(*bounds)
                footprintArr.append(mapping(footprint))
                bboxArr.append(mapping(footprint))
    return {"footprint": footprintArr, "bbox": bboxArr}
