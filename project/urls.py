"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('carrinho/',include('carrinho.urls')),
    path('cadastro_usuario/',include(('cadastro_de_usuarios.urls', 'cadastro_login'), namespace='cadastro_login')),
    path('pagamentos/',include('pagamentos.urls')),
    path('institucional/',include('institucional.urls')),
    path('senha/reset/',auth_views.PasswordResetView.as_view( template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt'),name='password_reset'),
    path('senha/reset/enviado/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('senha/reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('senha/reset/completo/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    path('admin/', admin.site.urls),
    path('',include('e_comerce.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)