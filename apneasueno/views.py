import os
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.db.models import Q
from django.db.models import Count
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.contrib.auth.models import Group
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.shortcuts import redirect
from weasyprint import HTML
from .models import Paciente
from .forms import DoctorRegisterForm
from .forms import PacienteForm
from .forms import DoctorLoginForm
from .models import PerfilDoctor
from .forms import RestablecerContrasenaForm
from weasyprint import HTML
from datetime import datetime
import base64
import os


# Create your views here.

#Funcion que se le envia una solicitud (vista se llama inicio)
def inicio(request): 
   return render(request, 'paginas/inicio.html')

def editar(request, id):
    pacientes = Paciente.objects.get(id=id)
    formulario = PacienteForm(request.POST or None, request.FILES or None, instance=pacientes)
    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('doctor_login')
    return render(request, 'paginas/pacientes/editar.html', {'formulario':formulario})

def eliminar(request, id):
    paciente = Paciente.objects.get(id=id)
    paciente.delete()
    return redirect('doctor_login')

def doctor_login(request):
    return render(request, 'paginas/doctor_login.html')

# ESTE ES EL QUE MANEJA EL FORMULARIO
def paciente_login(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save()  # Guardar y obtener el objeto paciente
            return redirect('paciente_exito', paciente_id=paciente.id)  # Redirigir a página de éxito
    else:
        form = PacienteForm()
    return render(request, 'paginas/pacientes/crear.html', {'form': form})

#envio exitoso encuesta
def paciente_exito(request, paciente_id):
    paciente = Paciente.objects.get(id=paciente_id)
    return render(request, 'paginas/pacientes/exito.html', {'paciente': paciente})

def crear(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pacientes')
    else:
        form = PacienteForm()
    return render(request, 'paginas/pacientes/crear.html', {'form': form})

#REGISTRO DEL DOCTOR (asignados al grupo doctores automaticamente)
def doctor_register(request):
    if request.method == 'POST':
        form = DoctorRegisterForm(request.POST)
        if form.is_valid():
            doctor = form.save()
            group = Group.objects.get(name='Doctores')
            doctor.groups.add(group)
            messages.success(request, "✅ Doctor registrado exitosamente.")
            return redirect('doctor_login')
    else:
        form = DoctorRegisterForm()
    return render(request, 'paginas/doctor_register.html', {'form': form})


#PDF DEL PACIENTE
def generar_pdf(request, paciente_id):
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

#INICIO DE SESION DOCTORES 
def doctor_login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "Ya tienes una sesión iniciada.")
        return redirect('pacientes_doctor')  # nos dirige a la lista que tiene todo

    if request.method == 'POST':
        form = DoctorLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                if not user.groups.filter(name='Doctores').exists():
                    messages.error(request, "No tienes permisos de doctor.")
                    return render(request, 'paginas/doctor_login.html', {'form': form})

                login(request, user)
                return redirect('pacientes_doctor')  # # nos dirige a la lista que tiene todo
            else:
                messages.error(request, "Credenciales incorrectas.")
    else:
        form = DoctorLoginForm()

    return render(request, 'paginas/doctor_login.html', {'form': form})


# Lista que solo mostrara el ID cuando se ingrese uno
def pacientes(request):
    query = request.GET.get('buscar')
    pacientes = None  # Por defecto, no mostrar nada

    # Verificar si es doctor
    es_doctor = False
    if request.user.is_authenticated:
        es_doctor = request.user.groups.filter(name='Doctores').exists()

    if query:
        if es_doctor:
            # ✅ Los doctores pueden buscar con coincidencias parciales
            pacientes = Paciente.objects.filter(
                Q(id__icontains=query) |
                Q(nombres__icontains=query) |
                Q(apellidos__icontains=query)
            )
        else:
            # ✅ Los pacientes solo verán su info si el ID coincide exactamente
            pacientes = Paciente.objects.filter(id=query)

    context = {
        'pacientes': pacientes,
        'es_doctor': es_doctor,
    }
    return render(request, 'paginas/pacientes/index.html', context)


# RECUPERAR CONTRASEÑA DOCTOREs

# 🔹 Definir la función ANTES de usarla en el decorador
def es_doctor_check(user):
    return user.is_authenticated and user.groups.filter(name='Doctores').exists()


@user_passes_test(es_doctor_check)
def pacientes_doctor(request):
    query = request.GET.get('buscar')
    pacientes = None

    if query:
        pacientes = Paciente.objects.filter(
            Q(id__icontains=query) |
            Q(nombres__icontains=query) |
            Q(apellidos__icontains=query) 
        )

    context = {
        'pacientes': pacientes,
        'es_doctor': True,
    }
    return render(request, 'paginas/pacientes/index.html', context)

    #GRAFICAS
@login_required
@user_passes_test(es_doctor_check)
def graficas_view(request):
    # Conteo por nivel de riesgo
    conteos_riesgo = Paciente.objects.values('riesgo').annotate(total=Count('riesgo'))

    # Inicializamos los datos para asegurar que todos los niveles aparezcan
    riesgo_data = {
        'Alto riesgo de AOS': 0,
        'Riesgo intermedio de AOS': 0,
        'Bajo riesgo de AOS': 0,
    }
    for item in conteos_riesgo:
        riesgo_data[item['riesgo']] = item['total']

    # Conteo por sexo
    conteos_sexo = Paciente.objects.values('sexo').annotate(total=Count('sexo'))

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

    from django.templatetags.static import static


#salir de la sesion
def salir(request):
    logout(request)  # Cierra la sesión
    return redirect('doctor_login')  # Redirige al login

