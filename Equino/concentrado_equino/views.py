import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.core.files.uploadedfile import SimpleUploadedFile
import qrcode
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.urls import reverse
from urllib.parse import urlencode
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_POST

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
import uuid
from io import BytesIO

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

        # Validación de nombre: solo letras y espacios
        if not re.match("^[A-Za-z\\s]+$", nombre):
            messages.warning(request, "El nombre solo puede contener letras y espacios.")
            return redirect("registrarse")

        # Validación de correo electrónico
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messages.warning(request, "Por favor, ingrese un correo electrónico válido.")
            return redirect("registrarse")

        # Validación de contraseñas
        if password1 != password2:
            messages.warning(request, "Las contraseñas no coinciden.")
            return redirect("registrarse")

        # Validar si el correo ya existe
        if validar_email_existente(request, email):
            return redirect("registrarse")


        # Crear el usuario con contraseña encriptada
        Usuario.objects.create(
            nombre=nombre,
            email=email,
            username=email,  # Usar el username único generado
            direccion=direccion,
            password=make_password(password1)  # Usamos make_password de Django
        )

        messages.success(request, "Usuario creado exitosamente.")
        return redirect("login")

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

# Perfil
@login_required
def ver_perfil(request):
    logueo = request.session.get("logueo", False)
    if not logueo:
        return redirect('login')

    user = get_object_or_404(Usuario, pk=logueo["id"])

    ruta = "Equino/usuario/perfil.html"

    roles = Usuario.ROLES
    estado = user.estado
    contexto = {'user': user, 'roles': roles, 'estado': estado, 'url': 'Perfil'}
    return render(request, ruta, contexto)

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        logueo = request.session.get("logueo", False)
        if not logueo:
            return redirect('login')

        user = get_object_or_404(Usuario, pk=logueo["id"])
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        direccion = request.POST.get('direccion')
        foto = request.FILES.get('foto')

        # Validar si el correo ya está registrado
        if Usuario.objects.filter(email=email).exclude(pk=user.pk).exists():
            messages.warning(request, "El correo ya está registrado.")
            return redirect('ver_perfil')

        user.nombre = nombre
        user.email = email
        user.direccion = direccion

        if foto:
            user.foto = foto

        user.save()

        # Actualizar la sesión con los nuevos datos del usuario, incluyendo el 'id'
        request.session["logueo"] = {
            "id": user.id,  # Mantener el id
            "nombre": user.nombre,
            "rol": user.rol,  # Asegúrate de que esto sea correcto
            "nombre_rol": user.get_rol_display(),
            "foto": user.foto.url if user.foto else None  # Actualiza la foto
        }

        messages.success(request, "Perfil actualizado exitosamente")
        return redirect('ver_perfil')

    return redirect('ver_perfil')

@login_required
def cambiar_contrasena(request):
    if request.method == 'POST':
        logueo = request.session.get("logueo", False)
        if not logueo:
            return redirect('login')

        user = get_object_or_404(Usuario, pk=logueo["id"])
        contrasena = request.POST.get('contrasena')
        confirmar_contrasena = request.POST.get('confirmar_contrasena')

        if contrasena != confirmar_contrasena:
            messages.warning(request, "Las contraseñas no coinciden")
            return redirect('ver_perfil')

        user.password = hash_password(contrasena)
        user.save()

        messages.success(request, "Contraseña cambiada exitosamente")
        return redirect('ver_perfil')

    return redirect('ver_perfil')

#CRUD PRODUCTOS

@login_required
def gestionar_productos(request):
    if request.user.rol != 1:
        return redirect('perfil')

    productos = Producto.objects.all()

    if request.method == 'POST':
        if 'eliminar' in request.POST:
            producto_id = request.POST.get('eliminar')
            producto = get_object_or_404(Producto, id=producto_id)
            producto.delete()
            messages.success(request, 'Producto eliminado correctamente.')
            return redirect('gestionar_productos')

        elif 'editar' in request.POST:
            producto_id = request.POST.get('editar')
            producto = get_object_or_404(Producto, id=producto_id)
            form = ProductoForm(request.POST, request.FILES, instance=producto)
            if form.is_valid():
                form.save()
                messages.success(request, 'Producto editado correctamente.')
                return redirect('gestionar_productos')

        elif 'agregar' in request.POST:
            form = ProductoForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Producto agregado correctamente.')
                return redirect('gestionar_productos')

    else:
        form = ProductoForm()

    return render(request, 'Equino/productos/gestionar_productos.html', {'productos': productos, 'form': form})

# Vistas del carrito de compras
@rol_requerido([1, 2, 3])
def agregar_producto_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    # Verifica que el usuario esté en request.user
    if not request.user.is_authenticated:
        messages.warning(request, "Debes iniciar sesión para agregar productos al carrito")
        return redirect('login')

    if producto.cantidad <= 0:
        messages.warning(request, "El producto está agotado y no se puede agregar al carrito.")
        return redirect('productos')

    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    carrito_item, item_created = CarritoItem.objects.get_or_create(carrito=carrito, producto=producto)

    if not item_created and carrito_item.cantidad >= producto.cantidad:
        messages.warning(request, "No hay suficiente stock disponible para agregar más de este producto.")
        return redirect('ver_carrito')

    if not item_created:
        carrito_item.cantidad += 1
        carrito_item.save()

    # Contar items en el carrito
    count = CarritoItem.objects.filter(carrito=carrito).count()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'count': count})

    messages.success(request, "Producto agregado al carrito")
    return redirect('ver_carrito')

# Agregar esta vista para obtener el contador del carrito
def get_cart_count(request):
    if request.user.is_authenticated:
        try:
            carrito = Carrito.objects.get(usuario=request.user)
            count = CarritoItem.objects.filter(carrito=carrito).count()
        except Carrito.DoesNotExist:
            count = 0
    else:
        count = 0
    return JsonResponse({'count': count})

@login_required
def ver_carrito(request):
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.carritoitem_set.all()
    total = carrito.total()
    carrito_vacio = not items.exists()  # Añade esta línea para determinar si el carrito está vacío
    return render(request, 'Equino/carrito/ver_carrito.html', {'items': items, 'total': total, 'carrito_vacio': carrito_vacio})

@login_required
def eliminar_producto_carrito(request, item_id):
    item = get_object_or_404(CarritoItem, id=item_id)
    item.delete()
    return redirect('ver_carrito')

@login_required
def vaciar_carrito(request):
    carrito = get_object_or_404(Carrito, usuario=request.user)
    carrito.carritoitem_set.all().delete()
    return redirect('ver_carrito')




from django.contrib.sites.shortcuts import get_current_site

@login_required
def realizar_pago(request):
    carrito = get_object_or_404(Carrito, usuario=request.user)
    total = carrito.total()
    qr_url = None
    codigo_pago = None
    comprobante_url = None

    # Generar un código de pago único antes de renderizar la página
    if not codigo_pago:
        codigo_pago = f"PAGO-{uuid.uuid4().hex[:6].upper()}-{int(total)}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Generar el código QR antes de renderizar la página
    qr_image = qrcode.make(codigo_pago)
    buffer = BytesIO()
    qr_image.save(buffer, format='PNG')
    qr_file = ContentFile(buffer.getvalue(), name=f'qr_{codigo_pago}.png')

    # Asegurarse de que la carpeta 'qr_codes' exista
    qr_codes_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
    os.makedirs(qr_codes_dir, exist_ok=True)

    # Guardar el código QR en la carpeta 'qr_codes' dentro de 'media'
    qr_path = os.path.join('qr_codes', f'qr_{codigo_pago}.png')
    qr_url = request.build_absolute_uri(f"/media/{qr_path}")

    if request.method == 'POST':
        pedido = Pedido.objects.create(usuario=request.user, total=total)

        for item in carrito.carritoitem_set.all():
            PedidoItem.objects.create(pedido=pedido, producto=item.producto, cantidad=item.cantidad)

        pago = Pago.objects.create(
            pedido=pedido,
            valor_total=total,
            codigo_pago=codigo_pago
        )

        # Guardar el código QR en el modelo Pago
        pago.qr_codigo.save(qr_path, qr_file)

        # Manejar la subida del comprobante de pago
        if 'comprobante_pago' in request.FILES:
            comprobante_file = request.FILES['comprobante_pago']
            comprobante_path = os.path.join('comprobantes', f'comprobante_{codigo_pago}.png')
            comprobante_url = request.build_absolute_uri(f"/media/comprobantes/{comprobante_path}")
            pago.comprobante_pago.save(comprobante_path, comprobante_file)

        pago.save()

        # Generar el PDF
        context = {
            'nombre_pagina': 'Detalles del Pago',
            'usuario': request.user,
            'items': carrito.carritoitem_set.all(),
            'total': total,
            'qr_url': qr_url,
            'comprobante_url': comprobante_url,
        }
        html = render_to_string('Equino/email/pdf/email_pdf_template.html', context)
        pdf_file = BytesIO()
        pisa.CreatePDF(html, dest=pdf_file)
        pdf_file.seek(0)

        # Enviar correo al administrador y al usuario con el PDF adjunto
        email = EmailMessage(
            'Nuevo pago realizado',
            f'Se ha realizado un nuevo pago con código {pago.codigo_pago}.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL, request.user.email],  # Incluir el correo del usuario
        )
        email.attach('detalles_del_pago.pdf', pdf_file.read(), 'application/pdf')
        email.send()

        # Mensaje de confirmación de envío de correo
        messages.success(request, "El pago se ha realizado y se ha enviado un correo al propietario y al usuario.")

        carrito.carritoitem_set.all().delete()
        return redirect('ver_carrito')

    # Pasar el código de pago y la URL del código QR al contexto
    return render(request, 'Equino/pagos/realizar_pago.html', {'total': total, 'qr_url': qr_url, 'codigo_pago': codigo_pago})

#crear pedido
@login_required
def crear_pedido(request):
    carrito = Carrito.objects.get(usuario=request.user)
    if not carrito.productos.exists():
        return redirect('ver_carrito')  # Evita crear un pedido vacío

    pedido = Pedido.objects.create(usuario=request.user, total=carrito.total())

    for item in carrito.carritoitem_set.all():
        PedidoItem.objects.create(pedido=pedido, producto=item.producto, cantidad=item.cantidad)

    # Vaciar el carrito
    carrito.productos.clear()

    return redirect('realizar_pago', pedido_id=pedido.id)

# actualizar cantidad del carrito
def incrementar_cantidad(request, item_id):
    item = CarritoItem.objects.get(id=item_id)
    item.incrementar_cantidad()
    return redirect('ver_carrito')  # Redirige a la página del carrito

def disminuir_cantidad(request, item_id):
    item = CarritoItem.objects.get(id=item_id)
    item.disminuir_cantidad()
    return redirect('ver_carrito')  # Redirige a la página del carrito
    






#admin
@rol_requerido([1])
def admin_dashboard(request):
    if not request.user.is_staff:  # Check if the user is an admin
        messages.warning(request, "Acceso denegado.")
        return redirect('index')
    return render(request, 'Equino/admin/dashboard.html')


# Crud de usuarios
@login_required
def gestionar_usuarios(request):
    if request.user.rol != 1:
        return redirect('perfil')

    usuarios = Usuario.objects.all()
    form = UsuarioForm()

    if request.method == 'POST':
        if 'agregar' in request.POST:
            form = UsuarioForm(request.POST, request.FILES)
            email = request.POST.get('email')
            username = email  # Asigna el correo electrónico al campo username

            # Validar si el email o el username ya existen
            if validar_email_existente(request, email):
                return redirect('gestionar_usuarios')

            if form.is_valid():
                usuario = form.save(commit=False)
                usuario.username = username  # Asigna el username antes de guardar
                try:
                    usuario.save()
                    messages.success(request, "Usuario agregado exitosamente.")
                except IntegrityError:
                    messages.error(request, "Error de integridad: El nombre de usuario o el correo ya existen.")
                return redirect('gestionar_usuarios')
            else:
                messages.warning(request, "Error al agregar el usuario. Verifique los datos.")

        elif 'editar' in request.POST:
            usuario_id = request.POST.get('editar')
            usuario = get_object_or_404(Usuario, id=usuario_id)
            email = request.POST.get('email')
            username = email  # Asigna el correo electrónico al campo username

            # Validar si el email o el username ya existen (excluyendo el usuario actual)
            if validar_email_existente(request, email, usuario_id):
                return redirect('gestionar_usuarios')

            form = UsuarioForm(request.POST, request.FILES, instance=usuario)
            if form.is_valid():
                usuario = form.save(commit=False)
                usuario.username = username  # Asigna el username antes de guardar
                try:
                    usuario.save()
                    messages.success(request, "Usuario actualizado exitosamente.")
                except IntegrityError:
                    messages.error(request, "Error de integridad: El nombre de usuario o el correo ya existen.")
                return redirect('gestionar_usuarios')
            else:
                messages.warning(request, "Error al actualizar el usuario. Verifique los datos.")

        elif 'eliminar' in request.POST:
            usuario_id = request.POST.get('eliminar')
            usuario = get_object_or_404(Usuario, id=usuario_id)
            usuario.delete()
            messages.success(request, "Usuario eliminado exitosamente.")
            return redirect('gestionar_usuarios')

    return render(request, 'Equino/usuario/gestionar_usuario.html', {'usuarios': usuarios, 'form': form})

#VALIDACION DE EMAIL
def validar_email_existente(request, email, usuario_id=None):
    if Usuario.objects.filter(email=email).exclude(id=usuario_id).exists():
        messages.warning(request, "El correo ya está registrado.")
        return True
    return False


#VALIDACION DE USUARIO
def validar_username_existente(username):
    return Usuario.objects.filter(username=username).exists()