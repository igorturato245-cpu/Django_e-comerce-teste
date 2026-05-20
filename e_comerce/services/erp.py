import requests
import base64
from django.conf import settings

BASE = getattr(settings,'ERP_API_URL', None)
API_KEY=getattr(settings,'ERP_API_KEY',None)
TIMEOUT=getattr(settings,'ERP_TIMEOUT',10)


def _auth_headers():
    #token_obj = TokenFornecedor.objects.first()
    access_token = getattr(settings, 'ERP_ACCES_TOKEN', API_KEY)#token_obj.access_token if token_obj else getattr(settings, 'ERP_ACCESS_TOKEN', '')
    
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

def fetch_products(page=1,per_page=100):
    if not BASE:
        raise RuntimeError('ERP_API_URL not configured')
    
    url=f'{BASE}produtos'
    params={'pagina':page,'limite':per_page}
    
    resp=requests.get(url, params=params,headers=_auth_headers(),timeout=TIMEOUT)
    
    if resp.status_code == 403:
        print(f"DEBUG BLING 403: {resp.text}")
    
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
    url=f'{BASE}pedidos/vendas'
    
    resp=requests.post(url,json=payload,headers=_auth_headers(),timeout=TIMEOUT)
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
        return {'price': '0.50', 'delivery_days': 10}
    
    
def refresh_bling_token(current_refresh_token):
    url='https://www.bling.com.br/Api/v3/oauth/token'
    
    credential=f'{settings.ERP_CLIENT_ID}:{settings.ERP_CLIENT_SECRET}'
    auth_header=base64.b64encode(credential.encode()).decode()
    
    headers = {
        'Authorization':f'Basic {auth_header}',
        'Content-Type':'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type':'refresh_token',
        'refresh_token':current_refresh_token       
    }
    
    response=requests.post(url,data=data,headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f'Erro ao renovar token:{response.text}')