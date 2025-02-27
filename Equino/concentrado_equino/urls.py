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
    path('iniciar_sesion/', views.login, name='login'),
    path('registrarse/', views.registro, name='registrarse'),
    path('logout/', views.logout, name='logout'),
    path('ver-perfil/', views.ver_perfil, name='ver_perfil'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('cambiar_contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),

#carrito
    path('agregar_producto_carrito/<int:producto_id>/', views.agregar_producto_carrito, name='agregar_producto_carrito'),
    path('ver_carrito/', views.ver_carrito, name='ver_carrito'),
    path('eliminar_producto_carrito/<int:item_id>/', views.eliminar_producto_carrito, name='eliminar_producto_carrito'),
    path('vaciar_carrito/', views.vaciar_carrito, name='vaciar_carrito'),
    path('realizar_pago/', views.realizar_pago, name='realizar_pago'),
    path('get-cart-count/', views.get_cart_count, name='get_cart_count'),


#CRUD PRODUCTOS
    path('gestionar-productos/', views.gestionar_productos, name='gestionar_productos'),
    path('administradores/', views.admin_dashboard, name='admin_dashboard'),

]