from decimal import Decimal
from typing import Any
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from e_comerce.models import Produto,Category
from e_comerce.services import erp as erp_service
from e_comerce.models import TokenFornecedor
from django.conf import settings


class Command(BaseCommand):
    help = 'Sincroniza produtos do ERP para o catálogo local'


    def handle(self, *args: Any, **options: Any) -> str | None:
        page = 1
        max_pages=1000

        self.stdout.write('Iniciando sincronização...')
        
        token_obj=TokenFornecedor.objects.first()
        refresh_token_atual=token_obj.refresh_token if token_obj else settings.ERP_REFRESH_TOKEN
        
        try:
            novos_dados=erp_service.refresh_bling_token(refresh_token_atual)
            
            token_obj,created=TokenFornecedor.objects.update_or_create(
                id=1,
                defaults={
                    'access_token':novos_dados.get('access_token'),
                    'refresh_token':novos_dados.get('refresh_token'),
                }
            )
            
            self.stdout.write(self.style.SUCCESS('Token atualizado no banco!'))
            
            access_token=token_obj.access_token
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Falha ao iniciar:{e}'))
            if not token_obj :return
        
        while page <= max_pages:
            try:
                response_data=erp_service.fetch_products(page=page)
                items=response_data.get('data', []) 

                if not items :
                    self.stdout.write(self.style.SUCCESS(f"Sincronização concluída. Total de páginas: {page-1}"))
                    break

                    
                for item in items:
                    erp_id=str(item.get('id'))
                    name=item.get('nome','---')

                    cat_name='Geral'

                    category,_=Category.objects.get_or_create(
                        name=cat_name,
                        defaults={'slug':slugify(cat_name)}
                    )


                    stock=item.get('estoque',{}).get('saldoVirtual',0)
                    price=Decimal(str(item.get('preco') or 0))
                    
                    defaults={
                            'category': category,
                            'name': name,
                            'descricao':item.get('description',''),
                            'preco': price,
                            'remote_price': price,
                            'remote_stock':stock,
                            'estoque':stock,
                            'disponivel':stock > 0,
                            'image_url':item.get('image_url'),
                            'last_synced':timezone.now(),
                        }

                    produto,created=Produto.objects.update_or_create(
                        erp_id=erp_id,
                        defaults={'slug':slugify(f'{name}-{erp_id}')}
                    )
                    
                    for key, value in defaults.items():
                        setattr(produto,key,value)
                    produto.save()
                    
                    action="Criado" if created else "Atualizado"
                    self.stdout.write(f"{action}:{name} (ERP ID:{erp_id})")

                
                page += 1 
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro na página {page}:{e}"))
                break


        
        if page > max_pages:
            self.stdout.write(self.style.WARNING("Limite máximo de páginas atingidas."))