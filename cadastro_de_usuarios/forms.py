from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from .models import Perfil,Endereco

class EnderecoForm(forms.ModelForm):
    class Meta:
        model=Endereco
        exclude=('usuario','padrao')

class PerfilForm(forms.ModelForm):
    class Meta:
        model=Perfil
        exclude=('usuario',)
        widgets = {
            'cpf': forms.TextInput(attrs={'maxlength': '14', 'placeholder': '000.000.000-00'}),
            'telefone': forms.TextInput(attrs={'maxlength': '15', 'placeholder': '(00) 00000-0000'}),
            'data_de_nascimento': forms.TextInput(attrs={'maxlength': '10', 'placeholder': 'DD/MM/AAAA'}),
        }

class CadastroForm(forms.ModelForm):

    password=forms.CharField(
        label='Senha',
        strip=False,
        widget=forms.PasswordInput(),
        help_text=password_validation.password_validators_help_text_html(),
        required=False,
    )

    password2=forms.CharField(
        label="Confirme a senha",
        strip=False,
        widget=forms.PasswordInput(),
        help_text='Use a mesma senha de antes.',
        required=False
    )

    def __init__(self,usuario=None,*args, **kwargs):
        self.usuario=kwargs.pop('usuario',None)
        super().__init__(*args, **kwargs)

    class Meta:
        model=User
        fields=('first_name','last_name','username','password','password2','email'
                )
   
    def clean(self):
        cleaned = super().clean()
        
        # Sua validação manual continua funcionando perfeitamente aqui
        # pois ela pega os dados do 'cleaned' (que inclui os campos extras acima)
        
        usuario_data = cleaned.get('username')
        email_data = cleaned.get('email')
        password_data = cleaned.get('password')
        password2_data = cleaned.get('password2')
        user_instance = self.instance

        # Verificações no banco de dados User padrão
        if usuario_data and User.objects.filter(username=usuario_data).exclude(pk=self.instance.pk).exists():
             self.add_error('username', 'Usuário já existe')

        if email_data and User.objects.filter(email=email_data).exclude(pk=self.instance.pk).exists():
             self.add_error('email', 'Email já existe')

        if password_data != password2_data:
             self.add_error('password2', 'As senhas não conferem')
             
        if password_data:
            try:
                password_validation.validate_password(password_data,user_instance)
            except forms.ValidationError as e:
                self.add_error('password',e)

        return cleaned