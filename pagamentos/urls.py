from django.urls import path
from . import views

app_name = 'pagamentos'

urlpatterns = [
    path('start/', views.start_payment, name='start_payment'),
    path('return/', views.payment_return, name='payment_return'),
    path('notifications/', views.pagseguro_notification, name='pagseguro_notify'),
]