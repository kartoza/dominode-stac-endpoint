from django.urls import path
from .views import catalog, collections, item_collection, item

urlpatterns = [
    path('catalog/', catalog, name='catalog'),
    path('collections/', collections, name='collections'),
    path('collections/<collection_name>/items/', item_collection, name='item_collection'),
    path('collections/<collection_name>/items/<item_name>', item, name='item'),
]