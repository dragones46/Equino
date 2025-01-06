from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.urls import reverse
from urllib.parse import urlencode
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from django.db.models import Q

#Para sacar totales de eventos.
from django.db.models import Sum
from django.shortcuts import render
import locale



from django.db.models import F
from collections import defaultdict

from django.utils import timezone
from datetime import timedelta

# Para tomar el from desde el settings
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
import threading

# Para que muestre más detalles de un error
import traceback

# Importamos todos los modelos de la base de datos
from django.db import IntegrityError, transaction
from django.http import JsonResponse
import json

from django.utils import timezone

#APIVIEW
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny


#PARA EL PDF
from xhtml2pdf import pisa
from django.template.loader import render_to_string
import os
import tempfile
from django.core.files import File

from django.urls import reverse


from rest_framework import viewsets

from .serializers import *
from rest_framework import viewsets


#Importar el crypt
from .crypt import *

#Importar todos los modelos de la base de datos.
from .models import *

#Validar la fecha de Nacimiento
from datetime import datetime

# Para restringir las vistas
from .decorators import rol_requerido

# Create your views here.

# inisio
def index(request):
    return render(request, 'Equino/index.html')

# informacion
def quienes_somos(request):
    return render(request, 'Equino/quienes_somos/quienes_somos.html')

#productos
def productos(request):
    productos = Producto.objects.all()
    return render(request, 'Equino/productos/productos.html', {'productos': productos})

#contactenos
def contactenos(request):
    return render(request, 'Equino/contactenos/contactenos.html')

# login y registro
def registro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        direccion = request.POST.get('direccion')
        password1 = request.POST.get('contrasena')
        password2 = request.POST.get('confirmar_contrasena')

        if password1 != password2:
            messages.warning(request, "Las contraseñas no coinciden")
            return redirect("registro")

        if Usuario.objects.filter(email=email).exists():
            messages.warning(request, "El correo ya está registrado")
            return redirect("registro")

        Usuario.objects.create(
            nombre=nombre,
            email=email,
            direccion=direccion,
            password=hash_password(password1)
        )
        messages.success(request, "Usuario creado exitosamente")
        return redirect("iniciar_sesion")

    return render(request, 'Equino/registro/registro.html')

def login(request):
    if request.method == 'POST':
        # Asegúrate de que uses .get() en lugar de () para acceder a los valores
        email = request.POST.get('email')  # Acceso correcto al campo email
        password = request.POST.get('password')  # Acceso correcto al campo password

        try:
            user = Usuario.objects.get(email=email)
            if verify_password(password, user.password):  # Verifica la contraseña correctamente
                request.session["logueo"] = {
                    "id": user.id,
                    "nombre": user.nombre,
                    "rol": user.rol,
                    "nombre_rol": user.get_rol_display(),
                    "foto": user.foto.url if user.foto else None
                }
                messages.success(request, "Has iniciado sesión exitosamente")
                return redirect("index")
            else:
                messages.warning(request, "Usuario o contraseña incorrectos")
        except Usuario.DoesNotExist:
            messages.warning(request, "Usuario no encontrado o no existe")

    return render(request, 'Equino/login/iniciar_sesion.html')



def logout(request):
    if "logueo" in request.session:
        del request.session["logueo"]
        messages.success(request, "Sesión cerrada correctamente")
    else:
        messages.warning(request, "No hay sesión activa.")
    return redirect("index")

@login_required
def ver_perfil(request):
    logueo = request.session.get("logueo", False)
    if not logueo:
        return redirect('login')

    user = get_object_or_404(Usuario, pk=logueo["id"])

    ruta = "fennys/perfil/ver_perfil.html"

    roles = Usuario.ROLES
    estado = user.estado
    contexto = {'user': user, 'roles': roles, 'estado': estado, 'url': 'Perfil'}
    return render(request, ruta, contexto)