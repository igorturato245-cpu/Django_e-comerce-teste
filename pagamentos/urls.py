from django.urls import path
from pagamentos.views import view_pagamentos 

app_name = 'pagamentos'

urlpatterns = [
    path('',view_pagamentos.checkout, name='checkout'),
    path('start/', view_pagamentos.start_payment, name='start_payment'),
    path('return/', view_pagamentos.payment_return, name='payment_return'),
    path('notifications/', view_pagamentos.pagseguro_notification, name='pagseguro_notify'),
]