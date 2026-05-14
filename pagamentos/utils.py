from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.shortcuts import redirect

def enviar_email_pedido_recebido(pedido):
    subject=f'Pedido Recebido #{pedido.id}'
    from_email=settings.DEFAULT_FROM_EMAIL
    to=[pedido.usuario.email]
    
    html_content=render_to_string('emails/email_pedido_recebido.html',{'pedido':pedido})
    text_content=strip_tags(html_content)
    
    email=EmailMultiAlternatives(subject,text_content,from_email,to)
    email.attach_alternative(html_content,'text/html')
    email.send()

def enviar_email_status_pedido(pedido):
    subject=f'Atualização do Pedido #{pedido.id}'
    from_email=settings.DEFAULT_FROM_EMAIL
    to=[pedido.usuario.email]
    
    html_content = render_to_string('emails/email_pedido.html', {'pedido':pedido})
    text_content=strip_tags(html_content)
    
    email=EmailMultiAlternatives(subject,text_content,from_email,to)
    email.attach_alternative(html_content, 'text/html')
    email.send()
    
def enviar_email_status_erp_pedido(pedido):
    subject=f'Atualização de envio do Pedido #{pedido.id}'
    from_email=settings.DEFAULT_FROM_EMAIL
    to=[pedido.usuario.email]
    
    html_content=render_to_string('emails/email_pedido_erp.html', {'pedido':pedido})
    text_content=strip_tags(html_content)
    
    email=EmailMultiAlternatives(subject,text_content,from_email,to)
    email.attach_alternative(html_content,'text/html')
    email.send()
    
def enviar_email_status_reembolso(solicitacao, pedido):
    subject=f'Atualização de Reembolso do Pedido #{pedido.id}'
    from_email=settings.DEFAULT_FROM_EMAIL
    to=[pedido.usuario.email]
    
    context={
        'solicitacao':solicitacao,
        'pedido':pedido,
    }
    
    html_content=render_to_string('emails/email_cancelamento_status.html', context)
    text_content=strip_tags(html_content)
    
    email=EmailMultiAlternatives(subject,text_content,from_email,to)
    email.attach_alternative(html_content,'text/html')
    email.send()
    
def enviar_email_cancelamento_direto(pedido):
    subject=f'Pedido #{pedido.id} Cancelado'
    from_email=settings.DEFAULT_FROM_EMAIL
    to=[pedido.usuario.email]
    
    html_content=render_to_string('emails/email_cancelamento_direto.html', {'pedido':pedido})
    text_content=strip_tags(html_content)
    
    email=EmailMultiAlternatives(subject,text_content,from_email,to)
    email.attach_alternative(html_content,'text/html')
    email.send()
    
    
def require_api_erp(view_func):
    def wrapper(request,*args, **kwargs):
        if not getattr(settings , 'ERP_API_URL', None):
            return redirect('produtos:manutencao')
        return view_func(request, *args, **kwargs)
    return wrapper


def require_api_payment(view_func):
    def wrapper(request,*args, **kwargs):
        if not getattr(settings,'PAGSEGURO_TOKEN',None):
            return redirect('produtos:manutencao')
        return view_func(request,*args, **kwargs)
    return wrapper