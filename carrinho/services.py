from .models import Carrinho,ItemCarrinho
from pagamentos.models import Pedido
from django.shortcuts import get_object_or_404

def marge_carts(old_session_key,user):
    
    cart_anon=Carrinho.objects.filter(session_key=old_session_key).first()
    cart_user,_=Carrinho.objects.get_or_create(usuario=user)
    
    if not cart_anon:
        return
    
    for itens in cart_anon.itens.all():#type:ignore
        item_user,created=ItemCarrinho.objects.get_or_create(
            carrinho=cart_user,
            produto=itens.produto,
            defaults={"quantidade":itens.quantidade}
        )
        
        if not created:
            item_user.quantidade += itens.quantidade
            item_user.save()
            
    cart_anon.delete()
        
    
    