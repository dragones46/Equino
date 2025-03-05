from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
import qrcode
from .authentication import CustomUserManager
import uuid
from io import BytesIO
from django.core.files import File
import json
from django import forms
from django.utils import timezone
import qrcode
from django.core.files.base import ContentFile
from django.conf import settings

# Modelo de Producto
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.IntegerField()
    foto = models.ImageField(upload_to='productos/')
    kg = models.IntegerField()

    def __str__(self):
        return self.nombre

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'foto', 'kg']

# Modelo de Usuario
class Usuario(AbstractUser):
    nombre = models.CharField(max_length=100, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    direccion = models.CharField(max_length=200, blank=False, null=False)
    password = models.CharField(max_length=100, blank=False, null=False)

    ROLES = (
        (1, "Administrador"),
        (2, "Vendedor"),
        (3, "Cliente"),
    )
    rol = models.IntegerField(choices=ROLES, default=3)

    ESTADO = (
        (1, "Activo"),
        (2, "Bloqueado"),
    )
    estado = models.IntegerField(choices=ESTADO, default=1)

    foto = models.ImageField(upload_to='usuarios/', null=True, blank=True, default='usuarios/default.png')
    token_recuperar = models.CharField(max_length=254, default="", blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_groups',
        blank=True
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_permissions',
        blank=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.nombre

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'direccion', 'rol', 'estado', 'foto']
        widgets = {
            'nombre': forms.TextInput(attrs={'required': True}),
            'email': forms.EmailInput(attrs={'required': True}),
            'direccion': forms.TextInput(attrs={'required': True}),
            'rol': forms.Select(attrs={'required': True}),
            'estado': forms.Select(attrs={'required': True}),
        }


# Modelo de Carrito
class Carrito(models.Model):
    usuario = models.OneToOneField('Usuario', on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='CarritoItem')

    def total(self):
        return sum(item.subtotal() for item in self.carritoitem_set.all())

# models.py
class CarritoItem(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    carrito = models.ForeignKey('Carrito', on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)

    def subtotal(self):
        return self.producto.precio * self.cantidad

    def incrementar_cantidad(self):
        self.cantidad += 1
        self.save()

    def disminuir_cantidad(self):
        if self.cantidad > 1:
            self.cantidad -= 1
            self.save()
        else:
            self.delete()

# Modelo de Pedido
class Pedido(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.IntegerField(choices=((1, "Pendiente"), (2, "Completado"), (3, "Cancelado")), default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def total(self):
        return sum(item.subtotal() for item in self.pedidoitem_set.all())

class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.producto.precio * self.cantidad



class Pago(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, default=1)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_pago = models.CharField(max_length=100)
    qr_codigo = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    comprobante_pago = models.FileField(upload_to='comprobantes/', null=True, blank=True)

    def generar_qr(self):
        try:
            qr = qrcode.make(self.codigo_pago)
            qr_io = BytesIO()
            qr.save(qr_io, format='PNG')
            qr_filename = f'qr_{self.codigo_pago}.png'
            self.qr_codigo.save(qr_filename, ContentFile(qr_io.getvalue()), save=False)
            print(f"QR generado y guardado como {qr_filename}")
        except Exception as e:
            print(f"Error al generar QR: {e}")

    def save(self, *args, **kwargs):
        if not self.qr_codigo:
            self.generar_qr()
        super().save(*args, **kwargs)

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['codigo_pago', 'comprobante_pago']
