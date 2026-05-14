import requests
from django.conf import settings
from django.shortcuts import redirect

BASE = getattr(settings,'ERP_API_URL', None)
API_KEY=getattr(settings,'ERP_API_KEY',None)
TIMEOUT=getattr(settings,'ERP_TIMEOUT',10)


def _auth_headers():
    headers={'Content-Type':'application/json'}
    if API_KEY:
        headers['Authorization']=f'Bearer {API_KEY}'
    return headers


def fetch_products(page=1,per_page=100):
    if not BASE:raise RuntimeError('ERP_API_URL not configured')
    resp=requests.get(f'{BASE}/products', params={'page':page,'per_page':per_page},headers=_auth_headers(),timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def check_availability(erp_id,quantity=1):
    resp=requests.get(f'{BASE}/products/{erp_id}/availability',headers=_auth_headers(),timeout=TIMEOUT)
    resp.raise_for_status()
    data=resp.json()
    return{
        'available':data.get('available',False),
        'stock':data.get('stock',0),
        'price':data.get('price')
    }



def send_order(payload):
    resp=requests.post(f'{BASE}/orders',json=payload,headers=_auth_headers(),timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()




def get_shipping_quote(cep,items):
    
    
    if not BASE:   
        return None
    
    
    paylod={
        'zipcode':cep,
        'items':items
    }
    
    
    try:
        resp=requests.post(f'{BASE}/shipping/quote' ,json=paylod,headers=_auth_headers(),timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    
    except Exception as e:
        return {'price': '25.00', 'delivery_days': 10}