import requests


WEBHOOK_URL = 'https://script.google.com/macros/s/AKfycbxYKskdIU9vjRJuXFwXy1rKwG484tXMysaQPS0-ETLObuZ-P3p5SwwZFANppwRqcfrr0g/exec'


def enviar_pedido_para_sheet(pedido):
    primeiro_item=pedido.pedidoitem_set.first()
    
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
        'codigo_rastreio': pedido.tracking_code or ''
    }

    response = requests.post(
        WEBHOOK_URL,
        json=data,
        timeout=10
    )

    return response.text