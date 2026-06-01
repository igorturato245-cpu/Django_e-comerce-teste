import requests
from django.conf import settings
from django.utils import timezone
import re

def apenas_numeros(valor):
    if not valor: return ""
    return re.sub(r'\D','',str(valor))

def build_order_payload(pedido):
    items=[]
    for it in pedido.items.all():
        items.append({
            'codigo': it.produto.erp_id if it.produto and it.produto.erp_id else it.produto_id_string,
            'nome': it.produto_name,
            'quantidade': it.quantidade,
            'valor': str(it.price),
            'descricao':it.produto_name[:120]
        })
        
    perfil = pedido.usuario.perfil_set.first() if pedido.usuario else ""
    cpf_cliente = apenas_numeros(perfil.cpf) if perfil else ""
    
    metadata_endereco = pedido.metadata.get('endereco_entrega', {}) if pedido.metadata else {}
    
    nome_cliente=pedido.usuario.get_full_name() or pedido.usuario.username

    payload={
        'numero':str(pedido.id),
        'data':timezone.localdate(pedido.created_at).strftime('%Y-%m-%d'),
        'contato':{
            'nome':nome_cliente,
            'numeroDocumento':cpf_cliente
        },
        
        'items':items,
        'transporte':{
            'fretePorConta':0,
            'enderecoEntrega':{
                'nome':nome_cliente,
                'endereco':metadata_endereco.get('rua',''),
                'numero':metadata_endereco.get('numero',''),
                'complemento':metadata_endereco.get('complemento',''),
                'bairro':metadata_endereco.get('bairro',''),
                'municipio':metadata_endereco.get('cidade',''),
                'uf':metadata_endereco.get('estado',''),
                'cep':metadata_endereco.get('cep',''),
            }
        }
    }
    return payload


def send_order(pedido):
    if not getattr(settings,'ERP_API_URL',None) or not getattr(settings,'ERP_API_KEY',None):
        raise RuntimeError('ERP_API_URL not configured')
    
    payload=build_order_payload(pedido)
    headers={
        'Authorization': f'Bearer {settings.ERP_API_KEY}',
        'Content-Type':'application/json'
    }
    
    timeout=getattr(settings,'ERP_TIMEOUT',10)
    
    resp=requests.post(f'{settings.ERP_API_URL}/orders', json=payload,timeout=timeout,headers=headers)
    resp.raise_for_status()
    return resp.json()



def send_order_cancelled(pedido):
    if not getattr(settings, 'ERP_API_URL', None) or not getattr(settings, 'ERP_API_KEY', None):
        raise RuntimeError('ERP_API_URL not configured')
    
    headers={
        'Authorization': f'Bearer {settings.ERP_API_KEY}',
        'Content-Type':'application/json'        
    }
    
    timeout=getattr(settings,'ERP_TIMEOUT',10)
    
    resp=requests.post(f'{settings.ERP_API_URL}/orders/{pedido.erp_order_id}/cancel',timeout=timeout,headers=headers)
    resp.raise_for_status()
    return resp.json()


def get_order_info(erp_order_id):
    if not getattr(settings, 'ERP_API_URL', None) or not getattr(settings, 'ERP_API_KEY', None):
        raise RuntimeError('ERP_API_URL not configured')
    
    headers={
        'Authorization':f'Bearer {settings.ERP_API_KEY}',
        'Content-Type':'application/json'
    }
    
    timeout=getattr(settings,'ERP_TIMEOUT',10)
    
    resp=requests.get(f'{settings.ERP_API_URL}/orders/{erp_order_id}/' ,timeout=timeout,headers=headers)
    resp.raise_for_status()
    return resp.json()
    