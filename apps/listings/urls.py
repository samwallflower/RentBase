from django.urls import path
from .views import ItemListCreateView
from .views import ItemPhotoUploadView

urlpatterns = [
    # This will be available at /api/v1/listings/
    path('', ItemListCreateView.as_view(), name='item_list_create'),
    path('<uuid:pk>/photos/', ItemPhotoUploadView.as_view(), name='item_photo_upload'),
]