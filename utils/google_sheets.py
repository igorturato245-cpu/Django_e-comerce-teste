import requests
import logging
from django.conf import settings

logger=logging.getLogger(__name__)

def enviar_pedido_para_sheet(pedido):
    URL_GOOGLE_SHEETS=getattr(settings,'URL_GOOGLE_SHEETS',None)
    
    if not URL_GOOGLE_SHEETS:
        return 'Erro:Falta de configuração'
    
    primeiro_item=pedido.items.first()
    
    if primeiro_item:
        nome_produto=primeiro_item.produto_name or "Produto Desconhecido"
        
        sku_produto=primeiro_item.produto.sku if hasattr(primeiro_item.produto, 'sku') else ''
    else:
        nome_produto='Sem item'
        sku_produto=''
        
    nome_cliente='Cliente não identificado'
    
    if pedido.usuario:
        nome_cliente=f'{pedido.usuario.first_name} {pedido.usuario.last_name}'.strip()
        if not nome_cliente:
            nome_cliente=pedido.usuario.username

    data = {

        'id_pedido': pedido.id,
        'data': str(pedido.created_at),
        'cliente': nome_cliente,
        'produto': nome_produto,
        'sku': sku_produto,
        'valor_produto': float(pedido.total),
        'frete_cobrado': float(pedido.valor_frete),
        'frete_fornecedor': float(pedido.valor_frete),
        'status': pedido.status,
        'codigo_rastreio': pedido.tracking_code or '',
        'fornecedor': '',
        'custo_produto': 0,
        'taxa_gateway': 4,
        'taxa_parcelamento': 0,
        'custo_anuncio': 20,
        'imposto': 0
    }
    
    try:

        response = requests.post(
            URL_GOOGLE_SHEETS,
            json=data,
            timeout=10
        )
        if response.text != 'OK':
            logger.error(f'Erro reportado pelo Google App Script:{response.text}')
        return response.text

    except Exception as e:
        logger.error(f'Erro de conexão com Google Sheets:{e}')
        return str(e)