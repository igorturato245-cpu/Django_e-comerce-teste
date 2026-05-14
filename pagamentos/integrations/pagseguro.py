import logging
import requests
import re
from django.conf import settings

logger = logging.getLogger(__name__)

def apenas_numeros(valor):
    if not valor:
        return ""
    # CORREÇÃO: \D (Barra Invertida) é o comando certo para limpar não-números
    return re.sub(r'\D', '', str(valor))

def _get_config():
    token = getattr(settings, 'PAGSEGURO_TOKEN', None)
    sandbox = getattr(settings, 'PAGSEGURO_SANDBOX', True)
    base_url = 'https://sandbox.api.pagseguro.com' if sandbox else 'https://api.pagseguro.com'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    return token, base_url, headers


def create_checkout(pedido, endereco, return_url, notification_url):
    token, base_url, headers = _get_config()

    if not token:
        raise RuntimeError('PAGSEGURO_TOKEN não configurado')

    items =[]
    for item in pedido.items.all():
        items.append({
            'reference_id': item.produto_id_string or str(item.id),
            'name': item.produto_name[:100],
            'quantity': item.quantidade,
            'unit_amount': int(round(item.price * 100)),
        })
        
    perfil = pedido.usuario.perfil_set.first()
    cpf_cliente = apenas_numeros(perfil.cpf) if perfil else ""
    cep_entrega = apenas_numeros(endereco.cep)

    payload = {
        'reference_id': f'PED-{pedido.id}',
        'customer': {
            'name': pedido.usuario.get_full_name() or pedido.usuario.username,
            'email': pedido.usuario.email,
            'tax_id': cpf_cliente,
        },
        'items': items,
        'shipping': {
            'type': 'FIXED',
            'amount': int(round(pedido.valor_frete * 100)),
            'address': {
                'street': endereco.endereco,
                'number': str(endereco.numero),
                'complement': endereco.complemento or "",
                'locality': endereco.bairro,
                'city': endereco.cidade,
                'region_code': endereco.estado,
                'country': 'BRA',
                'postal_code': cep_entrega
            }
        },
        # Notification dupla para garantir que você receberá o status do checkout E do pagamento
        'notification_urls': [notification_url],
        'payment_notification_urls': [notification_url], 
        'redirect_url': return_url,
        'payment_methods': [
            {'type': 'CREDIT_CARD'},
            {'type': 'BOLETO'},
            {'type': 'PIX'},
        ],
    }

    print("PAYLOAD ENVIADO:", payload)

    # 1º CORREÇÃO AQUI: Mudamos de '/orders' para '/checkouts'
    response = requests.post(f'{base_url}/checkouts', json=payload, headers=headers, timeout=30)

    print("STATUS:", response.status_code)
    print("RESPOSTA:", response.text)

    if response.status_code in (200, 201):
        data = response.json()
        links = data.get('links',[])
        pay_link = next((l['href'] for l in links if l.get('rel') == 'PAY'), None)
        if not pay_link:
            raise Exception('Link de pagamento não retornado pelo PagSeguro')
        return {
            'redirect_url': pay_link,
            'reference': f'PED-{pedido.id}',
            'code': data.get('id', ''), # Id do Checkout
        }
    else:
        raise Exception(f'Erro PagSeguro: {response.status_code} - {response.text}')


# 2º CORREÇÃO: Prepara a função para ler notificações do novo endpoint
def get_notification_data(notification_id):
    token, base_url, headers = _get_config()
    if not token:
        raise RuntimeError('PAGSEGURO_TOKEN não configurado')

    # Na API V4, o PagSeguro pode enviar avisos com IDs diferentes. Tratamos todos!
    if notification_id.startswith('CHCK_'):
        endpoint = f'{base_url}/checkouts/{notification_id}'
    elif notification_id.startswith('CHAR_'):
        endpoint = f'{base_url}/charges/{notification_id}'
    else:
        endpoint = f'{base_url}/orders/{notification_id}'

    response = requests.get(endpoint, headers=headers, timeout=30)

    if response.status_code == 200:
        data = response.json()
        
        charge = {}
        if notification_id.startswith('CHAR_'):
            charge = data
            ref = data.get('reference_id')
        elif notification_id.startswith('CHCK_'):
            ref = data.get('reference_id')
            orders = data.get('orders', [{}])
            order = orders[0] if orders else {}
            charges = order.get('charges', [{}])
            charge = charges[0] if charges else {}
        else: # ORDE_
            ref = data.get('reference_id')
            charges = data.get('charges', [{}])
            charge = charges[0] if charges else {}
            
        status = charge.get('status', 'WAITING')
        
        return {
            'reference': ref,
            'status': status, 
            'code': notification_id,         
            'charge_id': charge.get('id'),  
            'lastEventDate': charge.get('paid_at') or data.get('created_at'),
            'grossAmount': charge.get('amount', {}).get('value', 0) / 100,
        }
    return None

def validate_notification(data):
    # Simplificado porque na API V4 apenas exigimos que tenha as chaves principais
    return bool(data and data.get('reference') and data.get('code'))

# ATUALIZADO PARA API V4
def refund_transaction(charge_id, amount=None):
    token, base_url, headers = _get_config()
    if not token:
        raise RuntimeError('PAGSEGURO_TOKEN não configurado')

    # API V4 Cancela o CHARGE_ID e não o ORDER_ID
    url = f'{base_url}/charges/{charge_id}/cancel'
    payload = {}
    if amount:
        payload['amount'] = {'value': int(round(amount * 100))}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        # 200, 201 ou 204 representam sucesso
        if response.status_code in (200, 201, 204):
            logger.info(f'Transação {charge_id} reembolsada com sucesso')
            return True
        else:
            logger.error(f'Erro ao reembolsar {charge_id}: {response.text}')
            return False
    except Exception as e:
        logger.error(f'Falha na comunicação PagSeguro reembolso {charge_id}: {str(e)}')
        return False