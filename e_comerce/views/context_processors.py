from django.conf import settings

def google_ads_ids(request):
    return{
        "Analytics_id" : settings.GOOGLE_ANALYTICS_ID,
        "Tag_id":settings.GOOGLE_TAG_ID,
        "Tag_carrinho":settings.CODIGO_ENVIO_GOOGLE_TAG_CARRINHO,
        "Tag_checkout":settings.CODIGO_ENVIO_GOOGLE_TAG_CHECKOUT        
    }