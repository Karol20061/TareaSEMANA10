from django.contrib import admin
from django.urls import path, include
from . import views                                    # Nuestras vistas

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("saludo/", views.saludo, name="saludo"),
    path("info/", views.info_peticion, name="info"),

    # ---------- AUTENTICACIÓN (funciones) ----------
    path("login/", views.ingresar, name="login"),      # GET: formulario · POST: abre la sesión
    path("logout/", views.salir, name="logout"),       # Solo POST: cierra la sesión
    path("registro/", views.registro, name="registro"),  # GET: formulario · POST: crea el usuario

    path("facturacion/", include("facturacion.urls")),
]
