from django.urls import path
from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView #salir de la sesion
from django.contrib import admin
from .views import pacientes_doctor
from .views import graficas_view  



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('nosotros', views.nosotros, name='nosotros'),
    path('pacientes', views.pacientes, name='pacientes'), #lista
    path('pacientes/crear', views.crear, name='crear'), # creacion
    path('pacientes/editar', views.editar, name='editar'), 
    path('eliminar/<str:id>', views.eliminar, name='eliminar'),
    path('pacientes/editar/<str:id>', views.editar, name='editar'), # se coloco str para numeros y letras en ID | Boton editar (doctor)
    path('paciente_login', views.paciente_login, name='paciente_login'),
    path('doctor_register', views.doctor_register, name='doctor_register'),
    path('paciente/<str:paciente_id>/pdf/', views.generar_pdf, name='generar_pdf'), #generacion de pdf
    path('doctor_login/', views.doctor_login_view, name='doctor_login'), #para ingresar doc
    path('recuperar_contrasena', views.restablecer_contrasena, name='recuperar_contrasena'),
    path('logout/', views.salir, name='logout'), # Salir de la sesion
    path('pacientes/todos/', pacientes_doctor, name='pacientes_doctor'), #Lista de los doctores
    path('graficas/', graficas_view, name='graficas'), #graficas
    path('paciente/exito/<int:paciente_id>/', views.paciente_exito, name='paciente_exito'), #envio de formulario exitoso

]