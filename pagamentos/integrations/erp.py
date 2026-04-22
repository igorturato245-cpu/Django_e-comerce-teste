import requests
from django.conf import settings
from django.utils import timezone


def build_order_payload(pedido):
    items=[]
    for it in pedido.items.all():
        items.append({
            'product_id': it.produto.erp_id if it.produto and it.produto.erp_id else it.produto_id_string,
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
    if not settings.ERP_API_URL or not settings.ERP_API_KEY:
        raise RuntimeError('ERP_API_URL not configured')
    payload=build_order_payload(pedido)
    headers={
        'Authorization': f'Bearer {settings.ERP_API_KEY}',
        'Content-Type':'application/json'
    }
    resp=requests.post(f'{settings.ERP_API_URL}/orders', json=payload,timeout=settings.ERP_TIMEOUT,headers=headers)
    resp.raise_for_status()
    return resp.json()



def send_order_cancelled(pedido):
    if not settings.ERP_API_URL or not settings.ERP_API_KEY:
        raise RuntimeError('ERP_API_URL not configured')
    
    headers={
        'Authorization': f'Bearer {settings.ERP_API_KEY}',
        'Content-Type':'application/json'        
    }
    resp=requests.post(f'{settings.ERP_API_URL}/orders/{pedido.erp_order_id}/cancel',timeout=settings.ERP_TIMEOUT,headers=headers)
    resp.raise_for_status()
    return resp.json()


def get_order_info(erp_order_id):
    if not settings.ERP_API_URL or not settings.ERP_API_KEY:
        raise RuntimeError('ERP_API_URL not configured')
    
    headers={
        'Authorization':f'Bearer {settings.ERP_API_KEY}',
        'Content-Type':'application/json'
    }
    
    resp=requests.get(f'{settings.ERP_API_URL}/orders/{erp_order_id}/' ,timeout=settings.ERP_TIMEOUT,headers=headers)
    resp.raise_for_status()
    return resp.json()
    