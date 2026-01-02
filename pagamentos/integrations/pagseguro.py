import requests
import xml.etree.ElementTree as ET
from django.conf import settings
from urllib.parse import urlencode

PAGSEGURO_EMAIL = getattr(settings, 'PAGSEGURO_EMAIL', None)
PAGSEGURO_TOKEN = getattr(settings, 'PAGSEGURO_TOKEN', None)
SANDBOX = getattr(settings, 'PAGSEGURO_SANDBOX', True)
BASE_WS = 'https://ws.sandbox.pagseguro.uol.com.br' if SANDBOX else 'https://ws.pagseguro.uol.com.br'
BASE_URL = 'https://sandbox.pagseguro.uol.com.br' if SANDBOX else 'https://pagseguro.uol.com.br'

def create_checkout(pedido, return_url, notification_url):
    """
    Cria checkout no PagSeguro e retorna código de pagamento
    """
    if not PAGSEGURO_EMAIL or not PAGSEGURO_TOKEN:
        raise RuntimeError('Credenciais PagSeguro não configuradas')
    
    params = {
        'email': PAGSEGURO_EMAIL,
        'token': PAGSEGURO_TOKEN,
        'currency': 'BRL',
        'reference': f'PED-{pedido.id}',
        'redirectURL': return_url,
        'notificationURL': notification_url,
    }
    
    # Adicionar itens ao payload
    items = pedido.items.all()
    for i, item in enumerate(items, start=1):
        params[f'itemId{i}'] = item.produto_id or str(item.id)
        params[f'itemDescription{i}'] = item.produto_name[:100]  # Limitar tamanho
        params[f'itemAmount{i}'] = f'{item.price:.2f}'
        params[f'itemQuantity{i}'] = item.quantidade
    
    # Adicionar informações do comprador se disponível
    if pedido.usuario:
        params['senderName'] = pedido.usuario.get_full_name() or pedido.usuario.username
        params['senderEmail'] = pedido.usuario.email
    
    response = requests.post(
        f'{BASE_WS}/v2/checkout',
        data=urlencode(params),
        headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
        timeout=30
    )
    
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        code = root.findtext('code')
        if not code:
            raise Exception('Código de checkout não retornado pelo PagSeguro')
        
        return {
            'redirect_url': f'{BASE_URL}/v2/checkout/payment.html?code={code}',
            'reference': f'PED-{pedido.id}',
            'code': code
        }
    else:
        error_msg = f'Erro PagSeguro: {response.status_code}'
        try:
            root = ET.fromstring(response.text)
            for error in root.findall('.//error'):
                error_msg += f" | {error.findtext('message')}"
        except:
            error_msg += f" - {response.text}"
        raise Exception(error_msg)

def get_notification_data(notification_code):
    """
    Consulta transação no PagSeguro
    """
    if not PAGSEGURO_EMAIL or not PAGSEGURO_TOKEN:
        raise RuntimeError('Credenciais PagSeguro não configuradas')
    
    url = f"{BASE_WS}/v3/transactions/notifications/{notification_code}"
    params = {
        'email': PAGSEGURO_EMAIL,
        'token': PAGSEGURO_TOKEN
    }
    
    response = requests.get(url, params=params, timeout=30)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        return {
            'reference': root.findtext('reference'),
            'status': root.findtext('status'),
            'code': root.findtext('code'),
            'lastEventDate': root.findtext('lastEventDate'),
            'grossAmount': root.findtext('grossAmount'),
            'netAmount': root.findtext('netAmount'),
            'paymentMethod': root.findtext('paymentMethod/type'),
            'installments': root.findtext('installmentCount')
        }
    return None

def validate_notification(data):
    """
    Validação básica da notificação
    """
    required_fields = ['reference', 'status', 'code']
    return all(field in data and data[field] for field in required_fields)