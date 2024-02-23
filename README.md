# Dominode STAC Endpoint

This project was created to make api endpoints available for a STAC Catalog for data hosted on MINIO. The project automatically indexes folders and saves the data into a STAC catalog that is stored in a .json file on minio in respected folders

# Installing the project

1. Clone the project onto your machine
2. Create a virtual enviroment by running `python -m venv venv`
3. Activate virtual enviroment by running `source venv/bin/activate`
4. Install required python libraries by running `pip install requirements.txt`

# Set enviroment variables

1. The .env file can be found at directory `dominode/.env`
2. Set the `HOST` variable to your MINIO host
3. Add your `ACCESS_KEY` for MINIO
4. Add your `SECRET_KEY` for MINIO
5. Add the domain name on which the project is hosted in `URL`

# Run development server

1. cd into folder `dominode`
2. Run `python manage.py runserver`
3. By default the server runs on `http://127.0.0.1:8000/`

# CLI Commands

1. cd into folder `dominode`
2. Run `python manage.py index_stac`

This command indexes all the folders on MINIO and creates a STAC Catalog on MINIO. The function checks if a folder has been indexed or not.

# API Endpoints

## Catalog endpoint

- The enpoint for a catalog is `/stac/`
- This fetches a STAC Catlog in which STAC Collections are defined

## Collection endpoint

- The enpoint for a catalog is `/stac/collections/<collection_name>/`
- This fetches a STAC Collection in which STAC Collections are defined

## Feature Collection endpoint

- The enpoint for a catalog is `/stac/collections/<collection_name>/items/`
- This fetches a Features Collection in which features are defined which belong to a collection

## Item endpoint

- The enpoint for a catalog is `/stac/collections/<collection_name>/items/<item_name>/`
- This fetches a Features Collection in which features are defined that belong to a collection

# Folder Structure on MINIO

**Below is a overview of how the folders on MINIO should be structured for the api endpoint to work correctly**

Folders that are in bold need to have the same name. Folders in italic are the name of collections and items

|-**stac**
|--*<collection_name>*
|---**items**
|----*<item_name>*
|-----*upload tif/las/parquet/xml files that are associated with an item here*


