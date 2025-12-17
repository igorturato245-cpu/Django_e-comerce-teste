from django.shortcuts import get_object_or_404, redirect
from carrinho.models import Carrinho, ItemCarrinho
from e_comerce.models import Produto

def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    # 🔹 Carrinho único (por enquanto)
    carrinho, created = Carrinho.objects.get_or_create(id=1)

    # 🔹 quantidade vinda do produto
    quantidade = int(request.POST.get("quantidade", 1))
    quantidade = max(1, quantidade)

    item, created = ItemCarrinho.objects.get_or_create(
        carrinho=carrinho,
        produto=produto,
        defaults={'quantidade': quantidade}
    )

    if not created:
        item.quantidade += quantidade
        item.save()

    # 🔹 Decide para onde vai depois
    acao = request.POST.get('acao')

    if acao == 'comprar':
        return redirect('carrinho:carrinho')  # ou ver_carrinho

    return redirect('produtos:index')
