from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import AbstractUser,AbstractBaseUser, BaseUserManager

from .authentication import CustomUserManager
import uuid


from io import BytesIO
from django.core.files import File
import json
from django import forms

from django.utils import timezone

# Create your models here.

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
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    direccion = models.CharField(max_length=200)
    password = models.CharField(max_length=100)

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
        related_name='usuario_groups',  # Evita conflicto con auth.User.groups
        blank=True
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_permissions',  # Evita conflicto con auth.User.user_permissions
        blank=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.nombre




#Modelo de Carrito
class Carrito(models.Model):
    usuario = models.OneToOneField('Usuario', on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='CarritoItem')

    def total(self):
        return sum(item.subtotal() for item in self.carritoitem_set.all())

class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.producto.precio * self.cantidad


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
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE,default=1)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_pago = models.CharField(max_length=100)
    qr_codigo = models.ImageField(upload_to='qr_codes/')
    comprobante_pago = models.FileField(upload_to='comprobantes/', null=True, blank=True)

    def __str__(self):
        return f'Pago {self.codigo_pago} - Total: {self.valor_total}'
    

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['codigo_pago', 'comprobante_pago']
