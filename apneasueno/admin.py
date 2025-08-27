# ==========================================
# Configuración del panel de administración
# ==========================================

from django.contrib import admin
from .models import Paciente

# Solo una vez para crear el grupo
#Group.objects.get_or_create(name='Doctores')

# Register your models here.
#admin.site.register(Paciente)

# ============================
# Registro de modelos en admin
# ============================
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    """
    Personalización de la vista de Paciente en el panel de administración.
    """
    list_display = ('id', 'nombres', 'apellidos', 'edad', 'doctor', 'riesgo')  # columnas visibles
    search_fields = ('id', 'nombres', 'apellidos')  # barra de búsqueda
    list_filter = ('sexo', 'riesgo', 'doctor')      # filtros laterales
    ordering = ('id',)                              # orden por defecto
