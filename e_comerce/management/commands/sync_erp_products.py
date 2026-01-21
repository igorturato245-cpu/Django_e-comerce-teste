from typing import Any
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from e_comerce.models import Produto,Category
from e_comerce.services import erp as erp_service


class Command(BaseCommand):
    help = 'Sincroniza produtos do ERP para o catálogo local'


    def handle(self, *args: Any, **options: Any) -> str | None:
        page = 1
        max_pages=1000

        self.stdout.write('Iniciando sincronização...')

        while page <= max_pages:
            try:
                data=erp_service.fetch_products(page=page)
                items=data.get('items', []) if isinstance(data,dict) else data

                if not items :
                    self.stdout.write(self.style.SUCCESS(f"Sincronização concluída. Total de páginas: {page-1}"))
                    break

                    
                for item in items:
                    erp_id=str(item.get('id'))
                    name=item.get('name','---')

                    cat_name=item.get('category','Geral')
                    cat_slug=slugify(cat_name)

                    category,_=Category.objects.get_or_create(
                        name=cat_name,
                        defaults={'slug':cat_slug}
                    )

                    slug_candidate=slugify(f"{name}-{erp_id}")

                    stock=item.get('stock') or 0
                    price=item.get('price') or 0

                    produto,created=Produto.objects.update_or_create(
                        erp_id=erp_id,
                        defaults={
                            'category': category,
                            'name': name,
                            'slug': slug_candidate,
                            'descricao':item.get('description',''),
                            'preco': price,
                            'remote_price': price,
                            'remote_stock':stock,
                            'estoque':stock,
                            'disponivel':stock > 0,
                            'image_url':item.get('image_url'),
                            'last_synced':timezone.now(),
                        }
                    )
                    action="Criado" if created else "Atualizado"
                    self.stdout.write(f"{action}:{name} (ERP ID:{erp_id})")

                
                page += 1 
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro na página {page}:{e}"))
                break


        
        if page > max_pages:
            self.stdout.write(self.style.WARNING("Limite máximo de páginas atingidas."))