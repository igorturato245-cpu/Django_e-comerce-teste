from django.contrib.sitemaps import Sitemap
from .models import Produto,Category

class ProdutoSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Produto.objects.all()
    
class CategoriaSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Category.objects.all()