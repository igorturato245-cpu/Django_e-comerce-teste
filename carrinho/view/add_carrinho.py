from django.shortcuts import get_object_or_404, redirect
from carrinho.models import Carrinho, ItemCarrinho
from e_comerce.models import Produto

def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    # 🔹 Por enquanto: 1 carrinho global (depois pode virar por usuário/session)
    carrinho, created = Carrinho.objects.get_or_create(id=1)

    item, created = ItemCarrinho.objects.get_or_create(
        carrinho=carrinho,
        produto=produto,
        defaults={'quantidade': 1}
    )

    if not created:
        item.quantidade += 1
        item.save()

    # 🔹 Decide para onde vai depois
    acao = request.POST.get('acao')

    if acao == 'comprar':
        return redirect('carrinho:carrinho')

    return redirect('produtos:index')  # página principal
