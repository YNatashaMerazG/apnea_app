from django import forms
from .models import Doctor, Paciente
from .models import PerfilDoctor
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError


class PacienteForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.all(),
        empty_label="Seleccione un doctor",
        label="Doctor que atiende"
    )

    class Meta:
        model = Paciente
        fields = "__all__"
        widgets = {
            'sexo': forms.Select(choices=Paciente.SEXO_OPCIONES, attrs={'class': 'form-control'}),
            'ronca': forms.RadioSelect(choices=[(True, 'Sí'), (False, 'No')]),
            'cansado': forms.RadioSelect(choices=[(True, 'Sí'), (False, 'No')]),
            'observado': forms.RadioSelect(choices=[(True, 'Sí'), (False, 'No')]),
            'presion_alta': forms.RadioSelect(choices=[(True, 'Sí'), (False, 'No')]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 🔹 Hacemos obligatorios los radios
        self.fields['ronca'].required = True
        self.fields['cansado'].required = True
        self.fields['observado'].required = True
        self.fields['presion_alta'].required = True

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
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu usuario'
        })
    )

    nip = forms.CharField(
        label='NIP',
        max_length=5,
        min_length=5,
        help_text="Debe contener exactamente 5 caracteres.",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu NIP'
        })
    )

    nueva_contrasena = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Escribe tu nueva contraseña'
        })
    )

    def clean_nip(self):
        nip = self.cleaned_data.get("nip")
        if len(nip) != 5:
            raise ValidationError("El NIP debe tener exactamente 5 caracteres.")
        return nip

