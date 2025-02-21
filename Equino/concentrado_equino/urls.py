from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as especial

from . import views

urlpatterns = [

#inicio
    path('', views.index, name='index'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
    path('productos/', views.productos, name='productos'),
    path('contactenos/', views.contactenos, name='contactenos'),

#usuario
    path('iniciar-sesion/', views.login, name='iniciar_sesion'),
    path('registrarse/', views.registro, name='registrarse'),
    path('logout/', views.logout, name='logout'),
    path('ver-perfil/', views.ver_perfil, name='ver_perfil'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('cambiar_contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),

#carrito
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_producto_carrito, name='agregar_producto_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_producto_carrito, name='eliminar_producto_carrito'),
    path('pagar/', views.realizar_pago, name='realizar_pago'),


#CRUD PRODUCTOS
    path('productos/', views.lista_productos, name='lista_productos'),

#pagos
    path('pagar/', views.realizar_pago, name='pagar'),
]