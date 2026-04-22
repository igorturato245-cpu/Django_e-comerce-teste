from django.core.management.base import BaseCommand
from carrinho.tasks import executa_limpeza_carrinhos

class Command(BaseCommand):
    help='Remove carrinhos abandonados há mais de 7 dias'
    
    def handle(self,*args, **kwargs):
        self.stdout.write('Iniciando limpeza manual...')        
        resultado=executa_limpeza_carrinhos()
        self.stdout.write(self.style.SUCCESS(resultado))
        
        