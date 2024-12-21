from django.contrib import admin
from django.utils.html import mark_safe
from .models import *
# Register your models here.

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['id','nombre','descripcion','precio','foto']
    list_filter = ['id','nombre']
    list_editable = ['nombre','descripcion','precio','foto']

    def ver_foto(self, obj):
        return mark_safe(f"<a href='{obj.foto.url}'><img src='{obj.foto.url}' width='10%'></a>")
    
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['id','nombre','email','direccion','password','rol','estado','foto']
    search_fields = ['id','nombre','email']
    list_filter = ['rol']
    list_editable = ['rol','estado','direccion','password','foto']

    def ver_foto(self, obj):
        return mark_safe(f"<a href='{obj.foto.url}'><img src='{obj.foto.url}' width='10%'></a>")
    
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'ver_productos', 'estado']  # Cambiar productos_list por ver_productos
    list_filter = ['id', 'estado', 'usuario', 'fecha']
    list_editable = ['estado']

    def ver_foto(self, obj):
        return mark_safe(f"<a href='{obj.foto.url}'><img src='{obj.foto.url}' width='10%'></a>")
    
    def ver_productos(self, obj):
        """Método personalizado para mostrar los productos asociados al pedido."""
        return ', '.join([producto.nombre for producto in obj.productos.all()])
    
    ver_productos.short_description = 'Productos'  # Esto es opcional, establece un nombre más amigable en la columna

    