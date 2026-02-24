# images/urls.py
from django.urls import path
from .views import create_account, payment_handler, send_request_kaspi, create_tilda

urlpatterns = [

    path('create_account', create_account, name='create_account'),
    path('create_tilda', create_tilda, name='create_tilda'),
    path('payment_handler', payment_handler, name='payment_handler'),
    path('kaspi_request', send_request_kaspi, name='send_request_kaspi'),

]
