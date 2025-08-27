# ==========================================
# Definición de formularios personalizados
# Incluye:
#   - PacienteForm: para registrar/editar pacientes
#   - DoctorRegisterForm: para registrar doctores
#   - DoctorLoginForm: para inicio de sesión de doctores
#   - RestablecerContrasenaForm: para recuperación de contraseña
# ==========================================
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Paciente, PerfilDoctor

# ============================
# Formulario Paciente
# ============================
class PacienteForm(forms.ModelForm):
    """
    Formulario basado en el modelo Paciente.
    Incluye selección de doctor y personalización de campos.
    """
    doctor = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name="Doctores"),  
        required=False,
        label="Doctor asignado"
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
        """
        Configura campos obligatorios para las preguntas STOP-BANG.
        """
        super().__init__(*args, **kwargs)
        self.fields['ronca'].required = True
        self.fields['cansado'].required = True
        self.fields['observado'].required = True
        self.fields['presion_alta'].required = True

# ============================
# Registro de doctores
# ============================
class DoctorRegisterForm(forms.ModelForm):
    """
    Formulario para registrar nuevos doctores.
    Crea también el PerfilDoctor con NIP de recuperación.
    """
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
        """
        Valida que el NIP tenga exactamente 5 dígitos numéricos.
        """
        nip = self.cleaned_data['nip']
        if not nip.isdigit():
            raise ValidationError("El NIP debe contener solo números.")
        if len(nip) != 5:
            raise ValidationError("El NIP debe tener exactamente 5 dígitos.")
        return nip

    def save(self, commit=True):
        """
        Guarda el nuevo usuario con contraseña encriptada y crea su PerfilDoctor.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hasheamos la contraseña
        if commit:
            user.save()
            print(">>> Creando PerfilDoctor...")  # <-- Para confirmar ejecución
            # Creamos el perfil asociado al usuario
            PerfilDoctor.objects.create(user=user, nip=self.cleaned_data['nip'])
        return user

# ============================
# Inicio de sesión doctores
# ============================
class DoctorLoginForm(forms.Form):
    username = forms.CharField(label='Usuario', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

# ============================
# Recuperación de contraseña doctores
# ============================
class RestablecerContrasenaForm(forms.Form):
    """
    Formulario para que los doctores recuperen su contraseña
    usando su usuario y NIP de seguridad.
    """
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
        """
        Valida que el NIP tenga exactamente 5 caracteres.
        """
        nip = self.cleaned_data.get("nip")
        if len(nip) != 5:
            raise ValidationError("El NIP debe tener exactamente 5 caracteres.")
        return nip

