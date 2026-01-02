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
        default_cat,_=Category.objects.get_or_create(name='Geral',defaults={'slug':'geral'})

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


                    slug_candidate=slugify(f"{name}-{erp_id}")

                    produto,created=Produto.objects.update_or_create(
                        erp_id=erp_id,
                        defaults={
                            'category': default_cat,
                            'name': name,
                            'slug': slug_candidate,
                            'preco': item.get('price') or 0,
                            'remote_price': item.get('price'),
                            'remote_stock': item.get('stock'),
                            'estoque': item.get('stock') or 0,
                            'last_synced':timezone.now()
                        }
                    )
                    action="Criado" if created else "Atualizado"
                    self.stdout.write(f"{action}:{name} (ID:{erp_id})")

                
                page += 1 
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro na página {page}:{e}"))
                break


        
        if page > max_pages:
            self.stdout.write(self.style.WARNING("Limite máximo de páginas atingidas."))