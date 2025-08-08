from django import forms
from .models import Paciente
from .models import PerfilDoctor
from django.contrib.auth.models import User


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'
        widgets = {
            'sexo': forms.Select(choices=Paciente.SEXO_OPCIONES, attrs={'class': 'form-control'}),
            'ronca': forms.RadioSelect(choices=[(True, 'Sí'), (False, 'No')]),
            'cansado': forms.RadioSelect(choices=[(True, 'Sí'), (False, 'No')]),
            'observado': forms.RadioSelect(choices=[(True, 'Sí'), (False, 'No')]),
            'presion_alta': forms.RadioSelect(choices=[(True, 'Sí'), (False, 'No')]),
        }

#REGISTRO DE LOS DOCTORES
class DoctorRegisterForm(forms.ModelForm):
    username = forms.CharField(label='Usuario', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    nip = forms.CharField(
        label='NIP de recuperación',
        max_length=5,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '5 dígitos numéricos'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean_nip(self):
        nip = self.cleaned_data['nip']
        if not nip.isdigit():
            raise ValidationError("El NIP debe contener solo números.")
        if len(nip) != 5:
            raise ValidationError("El NIP debe tener exactamente 5 dígitos.")
        return nip

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hasheamos la contraseña
        if commit:
            user.save()
            print(">>> Creando PerfilDoctor...")  # <-- Para confirmar ejecución
            # Creamos el perfil asociado al usuario
            PerfilDoctor.objects.create(user=user, nip=self.cleaned_data['nip'])
        return user

# INICIO DE SESION DE LOS DOCTORES
class DoctorLoginForm(forms.Form):
    username = forms.CharField(label='Usuario', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

#RECUPERAR CONTRASEÑA DOCTORES
class RestablecerContrasenaForm(forms.Form):
    username = forms.CharField(label='Usuario')
    nip = forms.CharField(
        label='NIP',
        widget=forms.PasswordInput,
        max_length=5,
        min_length=5,
        help_text="Debe contener exactamente 5 caracteres."
    )
    nueva_contrasena = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput
    )

    def clean_nip(self):
        nip = self.cleaned_data.get("nip")
        if len(nip) != 5:
            raise ValidationError("El NIP debe tener exactamente 5 caracteres.")
        return nip

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        nip = cleaned_data.get("nip")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("Usuario no encontrado")

        try:
            PerfilDoctor.objects.get(user=user, nip=nip)
        except PerfilDoctor.DoesNotExist:
            raise forms.ValidationError("El NIP no coincide con el usuario")

        return cleaned_data
