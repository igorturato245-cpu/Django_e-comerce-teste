from django.urls import path
from pagamentos.views import view_pagamentos 

app_name = 'pagamentos'

urlpatterns = [
    path('',view_pagamentos.checkout, name='checkout'),
    path('start/', view_pagamentos.start_payment, name='start_payment'),
    path('retry/<int:pedido_id>/',view_pagamentos.retry_payment, name='retry_payment'),
    path('cancel/<int:pedido_id>/', view_pagamentos.cancelled_refunded_return, name='cancel_payment'),
    path('return/', view_pagamentos.payment_return, name='payment_return'),
    path('notifications/', view_pagamentos.pagseguro_notification, name='pagseguro_notify'),
    path('meuspedidos/',view_pagamentos.meuspedidos,name='meus_pedidos'),
    path('pedido/<int:pedido_id>/', view_pagamentos.detalhepedido, name='detalhe_pedido'),
    path('avaliar/pedido/<int:pedido_id>/' , view_pagamentos.avaliar_pedido , name='avaliar_pedido'),
    path('cancelar/pedido/<int:pedido_id>/', view_pagamentos.cancelar_reembolsar_pedido, name='devoluacao_reembolso'),
    path('solicitar/reembolso/pedido/<int:pedido_id>/', view_pagamentos.solicitar_cancelamento , name='solicitar_cancelamento'),
    path('analise/reembolso/pedido/<int:pedido_id>/', view_pagamentos.analise_reembolso, name='analise_reembolso'),
    path('solicitacao/reembolso/pedido/<int:pedido_id>/', view_pagamentos.reembolso_solicitacao_aprovada , name='solicitacao_reembolso_aprovada'),
]