import requests
from django.conf import settings
from django.utils import timezone

ERP_BASE=getattr(settings,'ERP_API_URL',None)


def build_order_payload(pedido):
    items=[]
    for it in pedido.items.all():
        items.append({
            'product_id': it.produto_id or None,
            'name': it.produto_name,
            'quantity': it.quantidade,
            'unit_price': str(it.price),
        })

    payload={
        'external_order_id': str(pedido.id),
        'total': str(pedido.total),
        'items': items,
        'customer': {
            'id': pedido.usuario.id if pedido.usuario else None,
        },
        'created_at': timezone.localtime(pedido.created_at).isoformat()
    }
    return payload


def send_order(pedido):
    if not ERP_BASE:
        raise RuntimeError('ERP_API_URL not configured')
    payload=build_order_payload(pedido)
    resp=requests.post(f'{ERP_BASE}/orders', json=payload,timeout=10,headers={'Content-Type':'application/json'})
    resp.raise_for_status()
    return resp.json()