from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST


def saludo(request):                                       # HttpResponse: texto/HTML escrito aquí mismo
    return HttpResponse("<h1>¡Hola desde Django!</h1><p>Esto es un HttpResponse.</p>")


def info_peticion(request):                                # JsonResponse: devuelve datos en JSON
    datos = {
        "metodo": request.method,
        "ruta": request.path,
        "parametros_get": request.GET.dict(),
        "navegador": request.headers.get("User-Agent", ""),
        "usuario": request.user.username if request.user.is_authenticated else "anónimo",
    }
    return JsonResponse(datos)


def home(request):                                         # render: página con template
    nombre = ""
    if request.method == "POST":                           # POST: el usuario envió su nombre
        nombre = request.POST.get("nombre", "").strip()
    # GET: solo se muestra la página
    contexto = {
        "titulo": "Mi Tienda",
        "nombre": nombre,
        "productos": ["Laptop", "Mouse", "Teclado"],
    }
    return render(request, "home.html", contexto)


# =====================================================================
# AUTENTICACIÓN · todo con funciones (VBF)
# =====================================================================

def ingresar(request):                                     # LOGIN
    if request.user.is_authenticated:                      # Si ya tiene sesión, no mostramos el login
        return redirect("home")
    # next = página que quería ver antes de ser enviado al login
    siguiente = request.POST.get("next") or request.GET.get("next") or ""
    if request.method == "POST":                           # POST: revisar usuario y contraseña
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)                        # Abre la sesión
            messages.success(request, f"Hola, {usuario.username}.")
            if siguiente and url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
                return redirect(siguiente)                 # Solo si "next" es de nuestro sitio
            return redirect("home")
    else:                                                  # GET: formulario vacío
        form = AuthenticationForm(request)
    return render(request, "registration/login.html", {"form": form, "next": siguiente})


@require_POST                                              # Solo acepta POST (GET → 405)
def salir(request):                                        # LOGOUT
    logout(request)
    messages.info(request, "Cerraste sesión.")
    return redirect("login")


def registro(request):                                     # CREAR CUENTA
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":                           # POST: crear el usuario
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()                          # Contraseña cifrada
            login(request, usuario)
            messages.success(request, f"¡Bienvenido, {usuario.username}! Tu cuenta fue creada.")
            return redirect("home")
    else:                                                  # GET: formulario vacío
        form = UserCreationForm()
    return render(request, "registration/registro.html", {"form": form})
