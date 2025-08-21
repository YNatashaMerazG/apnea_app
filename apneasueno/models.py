from django.db import models
from django.contrib.auth.models import User

class Paciente(models.Model):
    id = models.CharField(primary_key=True, max_length=20, verbose_name='ID o Número de Expediente')

    # Datos personales
    nombres = models.CharField(max_length=50, verbose_name='Nombre(s)', null=True)
    apellidos = models.CharField(max_length=50, verbose_name='Apellidos', null=True)
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # doctor asignado
    edad = models.PositiveIntegerField(verbose_name='Edad', null=True)
    estatura = models.FloatField(verbose_name='Estatura (m)', null=True)
    peso = models.FloatField(verbose_name='Peso (kg)', null=True)
    cuello = models.FloatField(verbose_name='Circunferencia del cuello (cm)', null=True)

    SEXO_OPCIONES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    sexo = models.CharField(max_length=1, choices=SEXO_OPCIONES, verbose_name='Sexo', null=True)

    # Preguntas STOP-BANG
    ronca = models.BooleanField(verbose_name='¿Ronca fuerte? (Tan fuerte que se escucha a través de puertas cerradas o su pareja lo codea por roncar de noche)', null=True)
    cansado = models.BooleanField(verbose_name='¿Se siente con frecuencia cansado, fatigado o somnoliento durante el dia? (por ejemplo, se queda dormido mientras conduce o habla con alguien)', null=True)
    observado = models.BooleanField(verbose_name='¿Alguien lo observó dejar de respirar o ahogarse/quedarse sin aliento mientras dormía?', null=True)
    presion_alta = models.BooleanField(verbose_name='¿Tiene o está recibiendo tratamiento para pressión arterial alta?', null=True)

    # IMC calculado automáticamente
    imc = models.FloatField(verbose_name='Índice de Masa Corporal', null=True, editable=False)
    puntuacion_stopbang = models.PositiveIntegerField(verbose_name='Puntuación STOP-BANG', null=True, editable=False)
    riesgo = models.CharField(max_length=20, verbose_name='Nivel de riesgo', null=True, editable=False)


    def __str__(self):
        return f'{self.id} - {self.nombres} {self.apellidos}'

    def save(self, *args, **kwargs):
        # Calcular IMC si se tiene peso y estatura
        if self.estatura and self.peso:
            self.imc = round(self.peso / (self.estatura ** 2), 2)

        # Calcular puntuación STOP-BANG
        puntos = 0
        if self.edad > 50: puntos += 1
        if self.ronca: puntos += 1
        if self.cansado: puntos += 1
        if self.observado: puntos += 1
        if self.presion_alta: puntos += 1
        if self.imc and self.imc > 35: puntos += 1
        if self.cuello and self.cuello > 40: puntos += 1

        self.puntuacion_stopbang = puntos

        # Determinar riesgo
        if puntos <= 1:
            self.riesgo = 'Bajo riesgo de AOS'
        elif 2 <= puntos <= 3:
            self.riesgo = 'Riesgo intermedio de AOS'
        else:
            self.riesgo = 'Alto riesgo de AOS'

        super().save(*args, **kwargs)

#Perfil del Doctor
class PerfilDoctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nip = models.CharField(max_length=5)

    def __str__(self):
        return self.user.username
