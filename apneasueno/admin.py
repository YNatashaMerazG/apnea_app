from django.contrib import admin
from .models import Paciente
from django.contrib.auth.models import Group

# Solo una vez para crear el grupo
#Group.objects.get_or_create(name='Doctores')

# Register your models here.
admin.site.register(Paciente)