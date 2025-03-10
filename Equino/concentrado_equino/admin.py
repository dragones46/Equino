from django.contrib import admin
from django.utils.html import mark_safe
from .models import *

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'descripcion', 'precio', 'kg', 'ver_foto', 'cantidad']
    list_filter = ['id', 'nombre']
    list_editable = ['nombre', 'descripcion', 'precio', 'kg', 'cantidad']

    def ver_foto(self, obj):
        if obj.foto:
            return mark_safe(f"<a href='{obj.foto.url}'><img src='{obj.foto.url}' width='50%'></a>")
        return "No foto"

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'email', 'direccion', 'password', 'rol', 'estado', 'ver_foto']
    search_fields = ['id', 'nombre', 'email']
    list_filter = ['rol']
    list_editable = ['rol', 'estado', 'direccion', 'password']

    def ver_foto(self, obj):
        if obj.foto:
            return mark_safe(f"<a href='{obj.foto.url}'><img src='{obj.foto.url}' width='10%'></a>")
        return "No foto"

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'ver_productos', 'estado']
    list_filter = ['id', 'estado', 'usuario', 'fecha']
    list_editable = ['estado']

    def ver_productos(self, obj):
        """Método personalizado para mostrar los productos asociados al pedido."""
        return ', '.join([producto.nombre for producto in obj.productos.all()])

    ver_productos.short_description = 'Productos'
