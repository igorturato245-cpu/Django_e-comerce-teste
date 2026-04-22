import os
from celery import Celery

# 1. Define o módulo de configurações padrão do Django para o programa 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')

# 2. Lê as configurações do Django. 
# O namespace='CELERY' significa que todas as configurações do Celery 
# no settings.py devem começar com o prefixo 'CELERY_'.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 3. Descobre automaticamente as tasks em todos os seus apps instalados (tasks.py).
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')