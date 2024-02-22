from django.urls import path
from .views import catalog, collection, item_collection, item

urlpatterns = [
    path('', catalog, name='catalog'),
    path('collections/<collection_name>/', collection, name='collections'),
    path('collections/<collection_name>/items/', item_collection, name='item_collection'),
    path('collections/<collection_name>/items/<item_name>/', item, name='item'),
]