# ==========================================
# Configuración de rutas principales del proyecto
# ==========================================
from django.contrib import admin
from django.urls import path
from . import views
from .views import pacientes_doctor, graficas_view


urlpatterns = [
    # ============================
    # Rutas de administración
    # ============================

    path('admin/', admin.site.urls), # Acceso a la administracion

    # ============================
    # Página principal
    # ============================
    path('', views.inicio, name='inicio'), # Pagina principal 

    # ============================
    # Pacientes
    # ============================
    path('pacientes', views.pacientes, name='pacientes'), #lista de pacientes (solo busqueda)
    path('pacientes/crear', views.crear, name='crear'), # Formulario para crear paciente
    path('paciente_login', views.paciente_login, name='paciente_login'), # formulario para crear paciente (paciente) 
    path('paciente/<str:paciente_id>/pdf/', views.generar_pdf, name='generar_pdf'), #generacion de pdf (pase)
    path('paciente/exito/<str:paciente_id>/', views.paciente_exito, name='paciente_exito'), #envio de formulario exitoso

    # ============================
    # Doctor
    # ============================
    path('pacientes/editar/<str:id>', views.editar, name='editar'), # Boton editar (para doctor) | se coloco str para numeros y letras en ID
    path('eliminar/<str:id>', views.eliminar, name='eliminar'), # Eliminar paciente (para doctor) 
    path('doctor_register', views.doctor_register, name='doctor_register'), #registrar un nuevo doctor
    path('doctor_login/', views.doctor_login_view, name='doctor_login'), #inicio de sesion doctores
    path('pacientes/todos/', pacientes_doctor, name='pacientes_doctor'), #Lista de pacientes (doctor)
    path("recuperar_contrasena", views.restablecer_contrasena, name="recuperar_contrasena"),
    path('logout/', views.salir, name='logout'), # Salir de la sesion (doctor)

    # ============================
    # Funcionalidades extra
    # ============================

    path('graficas/', graficas_view, name='graficas'), #graficas de los pacientes
]   