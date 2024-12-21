from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as especial

from . import views

urlpatterns = [

#inicio
    path('', views.index, name='home'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
    path('productos/', views.productos, name='productos'),
    path('contactenos/', views.contactenos, name='contactenos'),
    path('iniciar-sesion/', views.iniciar_sesion, name='iniciar_sesion'),
    path('registrarse/', views.registrarse, name='registrarse'),
]