from socket import timeout
from e_comerce.models import TokenFornecedor
from e_comerce.services import erp as erp_service
from django.conf import settings
import requests
from django.conf import settings
from django.utils import timezone
from e_comerce.models import TokenFornecedor
import re

def apenas_numeros(valor):
    if not valor: return ""
    return re.sub(r'\D','',str(valor))

def get_valid_access_token():
    token_obj=TokenFornecedor.objects.first()
    refresh_token=token_obj.refresh_token if token_obj else settings.ERP_REFRESH_TOKEN
    
    try:
        novos_dados=erp_service.refresh_bling_token(refresh_token)
        
        TokenFornecedor.objects.update_or_create(
            id=1,
            defaults={
                'access_token':novos_dados.get('access_token'),
                'refresh_token':novos_dados.get('refresh_token')
            }
        )
        return novos_dados.get('access_token')
    except Exception as e:
        if token_obj and token_obj.access_token:
            return token_obj.access_token
        raise RuntimeError(f'Falha ao obter token de acesso válido: {e}')

def _get_auth_headers():
    access_token = get_valid_access_token()
    return {
        'Authorization':f'Bearer {access_token}',
        'Content-Type':'application/json'
    }


def _obter_ou_criar_contato(pedido,base_url,headers,timeout,endereco_obj):
    nome_cliente = pedido.usuario.get_full_name() or pedido.usuario.username if pedido.usuario else "Cliente Sem Nome"
    perfil = pedido.usuario.perfil_set.first() if pedido.usuario else None
    cpf_cliente = apenas_numeros(perfil.cpf) if perfil and hasattr(perfil, 'cpf') else ""

    if cpf_cliente:
        resp_busca = requests.get(f'{base_url}/contatos', params={'numeroDocumento': cpf_cliente}, headers=headers, timeout=timeout)
        if resp_busca.status_code == 200:
            data = resp_busca.json().get('data', [])
            if data:
                return data[0]['id'] 


    payload_contato = {
        "nome": nome_cliente,
        "numeroDocumento": cpf_cliente,
        "tipo": "F" if len(cpf_cliente) <= 11 else "J",
        "situacao":"A",
        "contribuinte": 9
    }
    
    if endereco_obj:
        payload_contato["endereco"]={
            'geral':{
                'endereco':endereco_obj.endereco,
                'numero':str(endereco_obj.numero),
                'complemento':endereco_obj.complemento,
                'bairro':endereco_obj.bairro,
                'municipio':endereco_obj.cidade,
                'uf':endereco_obj.estado,
                'cep':apenas_numeros(endereco_obj.cep)            
            }
        }
    
    resp_cria = requests.post(f'{base_url}/contatos', json=payload_contato, headers=headers, timeout=timeout)
    
    if resp_cria.status_code >= 400:
        print("\n==== ERRO AO CRIAR CONTATO NO BLING ====")
        print(resp_cria.text)
        print("========================================\n")
    resp_cria.raise_for_status()
    
   
    return resp_cria.json()['data']['id']



def build_order_payload(pedido, contato_id,endereco_obj):
    itens_formatados = []
    for it in pedido.items.all():
        codigo_sku = it.produto.sku if it.produto and it.produto.sku else it.produto.erp_id or str(it.produto_id)
        
        item_payload = {
            'codigo': codigo_sku,             
            'descricao': it.produto_name[:120],
            'quantidade': int(it.quantidade),
            'valor': float(it.price)
        }
        
        if it.produto and it.produto.erp_id:
            item_payload['produto'] = {'id': int(it.produto.erp_id)}
            
        itens_formatados.append(item_payload)
                
    nome_cliente = pedido.usuario.get_full_name() or pedido.usuario.username

    payload = {
        'numero': str(pedido.id),
        'data': timezone.localdate(pedido.created_at).strftime('%Y-%m-%d'),
        'contato': {
            'id': contato_id
        },
        'itens': itens_formatados,
        'transporte': {
            'fretePorConta': 0,
            'etiqueta': {
                'nome': nome_cliente,
                'endereco': endereco_obj.endereco if endereco_obj else '',
                'numero': str(endereco_obj.numero) if endereco_obj else '',
                'complemento': endereco_obj.complemento if endereco_obj else '',
                'bairro': endereco_obj.bairro if endereco_obj else '',
                'municipio': endereco_obj.cidade if endereco_obj else '',
                'uf': endereco_obj.estado if endereco_obj else '',
                'cep': apenas_numeros(endereco_obj.cep) if endereco_obj else '',
            }
        }
    }
    return payload


def send_order(pedido):
    if not getattr(settings,'ERP_API_URL',None) or not getattr(settings,'ERP_API_KEY',None):
        raise RuntimeError('ERP_API_URL not configured')
        
    headers=_get_auth_headers()
    timeout=getattr(settings,'ERP_TIMEOUT',10)
    base_url = settings.ERP_API_URL.rstrip('/')
    
    endereco_obj=None
    if pedido.usuario:
        endereco_obj=pedido.usuario.enderecos.filter(padrao=True).first()
        if not endereco_obj:
            endereco_obj=pedido.usuario.enderecos.first()
    
    contato_id=_obter_ou_criar_contato(pedido,base_url,headers,timeout,endereco_obj)
    
    payload=build_order_payload(pedido,contato_id,endereco_obj)
    
    url_bling=f'{base_url}/pedidos/vendas'
    
    resp=requests.post(url_bling, json=payload,timeout=timeout,headers=headers)
   
    if resp.status_code >= 400:
        print("\n==== ERRO REJEITADO PELO BLING ====")
        print(resp.text)
        print("====================================\n")
   
    resp.raise_for_status()
    return resp.json()



def send_order_cancelled(pedido):
    if not getattr(settings, 'ERP_API_URL', None) or not getattr(settings, 'ERP_API_KEY', None):
        raise RuntimeError('ERP_API_URL not configured')
    
    headers=_get_auth_headers()
    timeout=getattr(settings,'ERP_TIMEOUT',10)
    
    base_url=settings.ERP_API_URL.rstrip('/')
    url_bling=f'{base_url}/pedidos/vendas/{pedido.erp_order_id}/situacoes'
    
    payload={'idSituacao':12}
    
    resp=requests.post(url_bling,json=payload,timeout=timeout,headers=headers)
    resp.raise_for_status()
    return resp.json()


def get_order_info(erp_order_id):
    if not getattr(settings, 'ERP_API_URL', None) or not getattr(settings, 'ERP_API_KEY', None):
        raise RuntimeError('ERP_API_URL not configured')
    
    headers=_get_auth_headers()
    
    timeout=getattr(settings,'ERP_TIMEOUT',10)
    
    base_url=settings.ERP_API_URL.rstrip('/')
    url_bling=f'{base_url}/pedidos/vendas/{erp_order_id}'
    
    resp=requests.get(url_bling,timeout=timeout,headers=headers)
    resp.raise_for_status()
    return resp.json()
    