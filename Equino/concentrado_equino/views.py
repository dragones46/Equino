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
    return render(request, 'Equino/productos/productos.html')

#contactenos
def contactenos(request):
    return render(request, 'Equino/contactenos/contactenos.html')

# login y registro
def iniciar_sesion(request):
    return render(request, 'Equino/login/iniciar_sesion.html')

def registrarse(request):
    return render(request, 'Equino/registro/registro.html')