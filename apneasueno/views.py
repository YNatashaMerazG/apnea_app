# ==============================================
# IMPORTACIONES
# ==============================================
import os
import base64
from datetime import datetime
from urllib import request

# Librerías de Django
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q, Count
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.utils import timezone

# Librerías de terceros
from weasyprint import HTML

# Archivos locales (propios de la app)
# Archivos locales (propios de la app)
from .models import Paciente, PerfilDoctor
from .forms import (
    PacienteForm,
    DoctorRegisterForm,
    DoctorLoginForm,
    RestablecerContrasenaForm,
)

# ==============================================
# VISTAS PRINCIPALES
# ==============================================

def inicio(request): 
   """Página de inicio del sistema."""
   return render(request, 'paginas/inicio.html')

# ==============================================
# PACIENTES
# ==============================================

def paciente_login(request):
    """
    Vista donde un paciente llena el formulario inicial.
    - Si es POST y válido, se guarda y se redirige a la página de éxito.
    - Si es GET, se muestra el formulario vacío.
    """
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save()  # Guardar y obtener el objeto paciente
            return redirect('paciente_exito', paciente_id=paciente.id)  # Redirigir a página de éxito
    else:
        form = PacienteForm()

    return render(request, 'paginas/pacientes/crear.html', {'form': form})

def paciente_exito(request, paciente_id):
    """Página de confirmación cuando un paciente completa su cuestionario."""
    paciente = Paciente.objects.get(id=paciente_id)
    return render(request, 'paginas/pacientes/exito.html', {'paciente': paciente})

def crear(request):
    """
    Vista para registrar un paciente con el cuestionario.
    - Guarda y redirige al listado de pacientes.
    """
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pacientes')
    else:
        form = PacienteForm()

    return render(request, 'paginas/pacientes/crear.html', {'form': form})

def editar(request, id):
    """Editar datos de un paciente existente."""
    pacientes = Paciente.objects.get(id=id)
    formulario = PacienteForm(request.POST or None, request.FILES or None, instance=pacientes)
    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('pacientes_doctor')
    return render(request, 'paginas/pacientes/editar.html', {'formulario':formulario})

def eliminar(request, id):
    """Eliminar un paciente por ID."""
    paciente = Paciente.objects.get(id=id)
    paciente.delete()
    return redirect('pacientes_doctor')

def pacientes(request):
    """
    Búsqueda de pacientes:
    - Si es doctor, solo ve sus pacientes asignados.
    - Si es paciente normal, solo puede buscar por ID.
    """
    query = request.GET.get('buscar')
    pacientes = Paciente.objects.none()  # empieza vacío

    if request.user.is_authenticated and request.user.groups.filter(name='Doctores').exists():
        # Solo pacientes asignados a este doctor
        pacientes = Paciente.objects.filter(doctor=request.user)
        if query:
            pacientes = pacientes.filter(
                Q(id__icontains=query) |
                Q(nombres__icontains=query) |
                Q(apellidos__icontains=query)
            )
    else:
        # Pacientes normales solo pueden buscar por ID
        if query:
            pacientes = Paciente.objects.filter(id=query)

    context = {
        'pacientes': pacientes,
        'es_doctor': request.user.is_authenticated and request.user.groups.filter(name='Doctores').exists(),
    }
    return render(request, 'paginas/pacientes/index.html', context)


# ==============================================
# DOCTORES
# ==============================================

def doctor_register(request):
    """
    Registro de doctores.
    - Se guardan y se asignan automáticamente al grupo 'Doctores'.
    """
    if request.method == 'POST':
        form = DoctorRegisterForm(request.POST)
        if form.is_valid():
            doctor = form.save()
            group = Group.objects.get(name='Doctores')
            doctor.groups.add(group)
            return render(request, "paginas/pacientes/exito_doctor.html", {"doctor": doctor})
    else:
        form = DoctorRegisterForm()
    return render(request, 'paginas/doctor_register.html', {'form': form})

def doctor_login_view(request): 
    """
    Maneja el inicio de sesión de doctores.
    - Verifica credenciales y grupo 'Doctores'.
    """
    if request.user.is_authenticated:
        return redirect('pacientes_doctor')  # sin messages.warning

    if request.method == 'POST':
        form = DoctorLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                if not user.groups.filter(name='Doctores').exists():
                    form.add_error(None, "No tienes permisos de doctor.")  # error general
                    return render(request, 'paginas/doctor_login.html', {'form': form})

                login(request, user)
                return redirect('pacientes_doctor')
            else:
                form.add_error(None, "Credenciales incorrectas.")  # error general
    else:
        form = DoctorLoginForm()

    return render(request, 'paginas/doctor_login.html', {'form': form})

def es_doctor_check(user):
    """
    Función auxiliar: valida que el usuario 
    pertenezca al grupo Doctores.
    """
    return user.groups.filter(name='Doctores').exists()

@login_required
@user_passes_test(es_doctor_check)
def pacientes_doctor(request):
    """
    Lista de pacientes para un doctor autenticado.
    Permite búsqueda por nombre, apellido o ID.
    """
    buscar = request.GET.get('buscar')

    # Filtramos solo pacientes asignados a este doctor
    pacientes = Paciente.objects.filter(doctor=request.user)

    # Si hay búsqueda, filtramos por nombre, apellido o ID
    if buscar:
        pacientes = pacientes.filter(
            Q(nombres__icontains=buscar) |
            Q(apellidos__icontains=buscar) |
            Q(id__icontains=buscar)
        )

    context = {
        'pacientes': pacientes,
        'es_doctor': True,
    }
    return render(request, 'paginas/pacientes/todos_los_pacientes.html', context)


    #GRAFICAS

@login_required
@user_passes_test(es_doctor_check)
def graficas_view(request):
    """
    Genera estadísticas para los doctores:
    - Distribución por nivel de riesgo.
    - Distribución por sexo.
    """
    # Filtramos solo pacientes asignados a este doctor
    pacientes = Paciente.objects.filter(doctor=request.user)

    # Conteo por nivel de riesgo (solo pacientes de este doctor)
    conteos_riesgo = pacientes.values('riesgo').annotate(total=Count('riesgo'))

    riesgo_data = {
        'Alto riesgo de AOS': 0,
        'Riesgo intermedio de AOS': 0,
        'Bajo riesgo de AOS': 0,
    }
    for item in conteos_riesgo:
        riesgo_data[item['riesgo']] = item['total']

    # Conteo por sexo (solo pacientes de este doctor)
    conteos_sexo = pacientes.values('sexo').annotate(total=Count('sexo'))

    sexo_data = {
        'Masculino': 0,
        'Femenino': 0,
    }
    for item in conteos_sexo:
        if item['sexo'] == 'M':
            sexo_data['Masculino'] = item['total']
        elif item['sexo'] == 'F':
            sexo_data['Femenino'] = item['total']

    contexto = {
        'riesgo_data': riesgo_data,
        'sexo_data': sexo_data,
    }

    return render(request, 'paginas/pacientes/graficas.html', contexto)

# ==============================================
# UTILIDADES
# ==============================================

def generar_pdf(request, paciente_id):
    """
    Genera un pase en PDF para un paciente.
    Incluye logo, fecha y datos del paciente.
    """
    paciente = Paciente.objects.get(id=paciente_id)

    # 2. Obtener fecha actual
    fecha_actual = timezone.now().strftime('%d/%m/%Y')

    with open(os.path.join(settings.STATIC_ROOT, "img/hospital.png"), "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()

    html_string = render_to_string('paginas/pacientes/pase_pdf.html', {
        'paciente': paciente,
        'year': datetime.now().year,
        'fecha_actual': fecha_actual,
        'logo_base64': logo_base64,
    })

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pase_paciente_{paciente.id}.pdf"'

    return response

def restablecer_contrasena(request):
    """
    Permite a un doctor cambiar su contraseña.
    - Busca usuario por username y actualiza contraseña.
    """
    if request.method == 'POST':
        form = RestablecerContrasenaForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            nueva_contrasena = form.cleaned_data['nueva_contrasena']
            user = User.objects.get(username=username)
            user.set_password(nueva_contrasena)
            user.save()
            messages.success(request, 'Contraseña actualizada correctamente.')
            storage = messages.get_messages(request)
            storage.used = True  # ⚡ evita que se repitan
            return redirect('doctor_login')

        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = RestablecerContrasenaForm()

    return render(request, 'paginas/recuperar_contrasena.html', {'form': form})

def salir(request):
    """Cerrar la sesión de un doctor y redirigir al login de doctores."""
    logout(request)  # Cierra la sesión
    return redirect('doctor_login')  # Redirige al login

