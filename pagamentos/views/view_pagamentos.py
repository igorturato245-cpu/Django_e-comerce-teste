from django.shortcuts import render,get_list_or_404,redirect

def index(request):
    pagamento=...

    context={
        'pagamentos':pagamento
    }

    return render(
        request,
        '',
        context
    )