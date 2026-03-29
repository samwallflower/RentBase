from django.urls import path
from .views import CreatePaymentIntentView
from .webhooks import stripe_webhook

urlpatterns = [
    path('<uuid:booking_id>/create-intent/', CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
]