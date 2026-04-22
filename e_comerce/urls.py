from django.urls import path
from e_comerce.views import view_principal
from e_comerce.views import view_produto
from e_comerce.views import qtd_prod
from django.contrib.sitemaps.views import sitemap
from .sitemap import ProdutoSitemap,CategoriaSitemap
from django.views.generic import TemplateView

app_name='produtos'

sitemaps ={ 'produtos':ProdutoSitemap,
           'categorias':CategoriaSitemap}

urlpatterns = [
    path('', view_principal.index, name='index'),
    path('<slug:categoria_slug>/<slug:produto_slug>/', view_produto.produto, name='produto'),
    path('atualizar_qtd',qtd_prod.atualizar_qtd, name='qtd_prod'),
    path('sitemap.xml',sitemap, {'sitemaps':sitemaps}),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]
