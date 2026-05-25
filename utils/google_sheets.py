import requests


WEBHOOK_URL = 'https://script.google.com/macros/s/AKfycbxYKskdIU9vjRJuXFwXy1rKwG484tXMysaQPS0-ETLObuZ-P3p5SwwZFANppwRqcfrr0g/exec'


def enviar_pedido_para_sheet(pedido):

    data = {

        'id_pedido': pedido.id,
        'data': str(pedido.data),
        'cliente': pedido.cliente.nome,
        'produto': pedido.produto.nome,
        'sku': pedido.produto.sku,
        'fornecedor': pedido.produto.fornecedor,
        'valor_produto': float(pedido.valor_produto),
        'frete_cobrado': float(pedido.frete),
        'custo_produto': float(pedido.custo_produto),
        'frete_fornecedor': float(pedido.frete_fornecedor),
        'taxa_gateway': float(pedido.taxa_gateway),
        'taxa_parcelamento': float(pedido.taxa_parcelamento),
        'custo_anuncio': float(pedido.custo_anuncio),
        'imposto': float(pedido.imposto),
        'status': pedido.status,
        'codigo_rastreio': pedido.codigo_rastreio or ''
    }

    response = requests.post(
        WEBHOOK_URL,
        json=data,
        timeout=10
    )

    return response.text