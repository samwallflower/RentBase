from django.urls import path
from .views import StartVerificationView

urlpatterns = [
    path('start/', StartVerificationView.as_view(), name='start_verification'),
]