from django.contrib import messages
from django.contrib.auth.decorators import login_required   # Exige sesión iniciada
from django.core.paginator import Paginator
from django.db.models import Count, ProtectedError, Q
from django.shortcuts import render, redirect, get_object_or_404

from .forms import MarcaForm, ProductoForm, CategoriaForm, ClienteForm, PerfilForm
from .models import Marca, Producto, Categoria, Cliente, Perfil


# =====================================================================
# MARCAS · Vistas Basadas en Funciones (VBF) · Unidad 2
# =====================================================================

@login_required
def marca_lista(request):                                  # READ · solo GET
    q = request.GET.get("q", "")                           # Buscador: ?q=sam
    marcas = Marca.objects.all()
    if q:
        marcas = marcas.filter(nombre__icontains=q)
    contexto = {"titulo": "Marcas", "marcas": marcas, "q": q}
    return render(request, "facturacion/marca_lista.html", contexto)


@login_required
def marca_crear(request):                                  # CREATE
    if request.method == "POST":                           # POST: guardar
        form = MarcaForm(request.POST)
        if form.is_valid():
            marca = form.save()
            messages.success(request, f"Marca «{marca.nombre}» creada correctamente.")
            return redirect("facturacion:marca_lista")
    else:                                                  # GET: formulario vacío
        form = MarcaForm()
    contexto = {"titulo": "Nueva marca", "form": form, "boton": "Guardar"}
    return render(request, "facturacion/marca_form.html", contexto)


@login_required
def marca_editar(request, pk):                             # UPDATE
    marca = get_object_or_404(Marca, pk=pk)
    if request.method == "POST":                           # POST: actualizar
        form = MarcaForm(request.POST, instance=marca)
        if form.is_valid():
            form.save()
            messages.success(request, f"Marca «{marca.nombre}» actualizada.")
            return redirect("facturacion:marca_lista")
    else:                                                  # GET: formulario lleno
        form = MarcaForm(instance=marca)
    contexto = {"titulo": f"Editar marca: {marca.nombre}", "form": form, "boton": "Actualizar"}
    return render(request, "facturacion/marca_form.html", contexto)


@login_required
def marca_eliminar(request, pk):                           # DELETE
    marca = get_object_or_404(Marca, pk=pk)
    if request.method == "POST":                           # POST: borrar
        try:
            nombre = marca.nombre
            marca.delete()
            messages.success(request, f"Marca «{nombre}» eliminada.")
        except ProtectedError:                             # on_delete=PROTECT: tiene productos
            messages.error(request, f"No se puede eliminar «{marca.nombre}» porque tiene productos. Desactívala en su lugar.")
        return redirect("facturacion:marca_lista")
    contexto = {"titulo": "Eliminar marca", "marca": marca}   # GET: pregunta «¿Seguro?»
    return render(request, "facturacion/marca_eliminar.html", contexto)


# =====================================================================
# PRODUCTOS · Vistas Basadas en Funciones (VBF) · Unidad 3
# =====================================================================

@login_required
def producto_lista(request):                               # READ · solo GET
    q = request.GET.get("q", "")
    productos = (
        Producto.objects
        .select_related("marca")                           # 1:N → JOIN
        .prefetch_related("categorias")                    # N:M → 1 consulta extra
    )
    if q:
        productos = productos.filter(nombre__icontains=q)
    paginador = Paginator(productos, 5)                    # 5 por página
    page_obj = paginador.get_page(request.GET.get("page"))
    contexto = {"titulo": "Productos", "page_obj": page_obj, "q": q}
    return render(request, "facturacion/producto_lista.html", contexto)


@login_required
def producto_crear(request):                               # CREATE
    if request.method == "POST":                           # POST: guardar
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()                         # INSERT + categorías (N:M)
            messages.success(request, f"Producto «{producto.nombre}» creado.")
            return redirect("facturacion:producto_lista")
    else:                                                  # GET: formulario vacío
        form = ProductoForm()
    contexto = {"titulo": "Nuevo producto", "form": form, "boton": "Guardar"}
    return render(request, "facturacion/producto_form.html", contexto)


@login_required
def producto_editar(request, pk):                          # UPDATE
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":                           # POST: actualizar
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f"Producto «{producto.nombre}» actualizado.")
            return redirect("facturacion:producto_lista")
        messages.error(request, "Revisa los campos marcados en rojo.")
    else:                                                  # GET: formulario lleno
        form = ProductoForm(instance=producto)
    contexto = {"titulo": f"Editar producto: {producto.nombre}", "form": form, "boton": "Actualizar"}
    return render(request, "facturacion/producto_form.html", contexto)


@login_required
def producto_detalle(request, pk):                         # READ (uno) · solo GET
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, "facturacion/producto_detalle.html", {"producto": producto})


@login_required
def producto_eliminar(request, pk):                        # DELETE
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":                           # POST: borrar
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f"Producto «{nombre}» eliminado.")
        return redirect("facturacion:producto_lista")
    contexto = {"titulo": "Eliminar producto", "producto": producto}   # GET: pregunta
    return render(request, "facturacion/producto_eliminar.html", contexto)


# =====================================================================
# CATEGORÍAS · Tarea 1 · Vistas Basadas en Funciones (VBF)
# =====================================================================

@login_required
def categoria_lista(request):                              # READ · solo GET
    # GET es lo único que atiende: lista y busca, nunca cambia datos.
    q = request.GET.get("q", "")                           # 1. Buscador: /categorias/?q=aud (si no hay, "")
    categorias = Categoria.objects.annotate(               # 2. Todas las categorías, y a cada una le agregamos
        num_productos=Count("productos")                   #    num_productos (N:M al revés con related_name).
    )                                                      #    Así la tabla hace 1 consulta en vez de 1 por fila
    if q:                                                  # 3. Si escribió algo...
        categorias = categorias.filter(nombre__icontains=q)    # ...filtramos por nombre
    contexto = {"titulo": "Categorías", "categorias": categorias, "q": q}
    return render(request, "facturacion/categoria_lista.html", contexto)


@login_required
def categoria_crear(request):                              # CREATE
    if request.method == "POST":                           # POST: el usuario presionó «Guardar»
        form = CategoriaForm(request.POST)                 # Formulario con lo que escribió
        if form.is_valid():                                # ¿Pasa clean_nombre y el unique?
            categoria = form.save()                        # INSERT
            messages.success(request, f"Categoría «{categoria.nombre}» creada correctamente.")
            return redirect("facturacion:categoria_lista") # Post/Redirect/Get: F5 no duplica
        # Si no es válido, baja al render y muestra el formulario CON errores
    else:                                                  # GET: solo abrió la página
        form = CategoriaForm()                             # Formulario vacío
    contexto = {"titulo": "Nueva categoría", "form": form, "boton": "Guardar"}
    return render(request, "facturacion/categoria_form.html", contexto)


@login_required
def categoria_editar(request, pk):                         # UPDATE
    categoria = get_object_or_404(Categoria, pk=pk)        # pk viene de la URL; si no existe → 404
    if request.method == "POST":                           # POST: presionó «Actualizar»
        form = CategoriaForm(request.POST, instance=categoria)   # instance = «trabaja sobre ESTA categoría»
        if form.is_valid():
            form.save()                                    # UPDATE
            messages.success(request, f"Categoría «{categoria.nombre}» actualizada.")
            return redirect("facturacion:categoria_lista")
        messages.error(request, "Revisa los campos marcados en rojo.")
    else:                                                  # GET: formulario LLENO con los datos actuales
        form = CategoriaForm(instance=categoria)
    contexto = {"titulo": f"Editar categoría: {categoria.nombre}", "form": form, "boton": "Actualizar"}
    return render(request, "facturacion/categoria_form.html", contexto)


@login_required
def categoria_eliminar(request, pk):                       # DELETE
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":                           # POST: presionó «Sí, eliminar»
        nombre = categoria.nombre
        categoria.delete()                                 # Borra la categoría y SUS FILAS de la tabla intermedia (N:M).
        messages.success(request, f"Categoría «{nombre}» eliminada.")   # Los productos NO se borran.
        return redirect("facturacion:categoria_lista")
    # GET: mostramos la pregunta «¿Seguro?» avisando a cuántos productos afecta
    contexto = {
        "titulo": "Eliminar categoría",
        "categoria": categoria,
        "num_productos": categoria.productos.count(),      # N:M al revés con related_name
    }
    return render(request, "facturacion/categoria_eliminar.html", contexto)


# =====================================================================
# CLIENTES · Tarea 2 · Vistas Basadas en Funciones (VBF)
# =====================================================================

@login_required
def cliente_lista(request):                                # READ · solo GET
    # GET: lista con buscador y 5 clientes por página. No cambia datos.
    q = request.GET.get("q", "").strip()                   # 1. Texto del buscador
    clientes = Cliente.objects.all()                       # 2. Todos (ordenados por apellidos, nombres: Meta)
    if q:                                                  # 3. Reto extra: apellidos O cédula (objetos Q)
        clientes = clientes.filter(Q(apellidos__icontains=q) | Q(cedula__startswith=q))
    paginador = Paginator(clientes, 5)                     # 4. Páginas de 5 en 5
    page_obj = paginador.get_page(request.GET.get("page")) # 5. Página pedida (?page=2)
    contexto = {"titulo": "Clientes", "page_obj": page_obj, "q": q}
    return render(request, "facturacion/cliente_lista.html", contexto)


@login_required
def cliente_crear(request):                                # CREATE
    if request.method == "POST":                           # POST: guardar
        form = ClienteForm(request.POST)
        if form.is_valid():                                # clean_cedula + unique de cédula
            cliente = form.save()                          # INSERT (fecha_registro se llena sola)
            messages.success(request, f"Cliente «{cliente}» creado correctamente.")
            return redirect("facturacion:cliente_lista")
    else:                                                  # GET: formulario vacío
        form = ClienteForm()
    contexto = {"titulo": "Nuevo cliente", "form": form, "boton": "Guardar"}
    return render(request, "facturacion/cliente_form.html", contexto)


@login_required
def cliente_editar(request, pk):                           # UPDATE
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":                           # POST: actualizar
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()                                    # UPDATE
            messages.success(request, f"Cliente «{cliente}» actualizado.")
            return redirect("facturacion:cliente_lista")
        messages.error(request, "Revisa los campos marcados en rojo.")
    else:                                                  # GET: formulario lleno
        form = ClienteForm(instance=cliente)
    contexto = {"titulo": f"Editar cliente: {cliente}", "form": form, "boton": "Actualizar"}
    return render(request, "facturacion/cliente_form.html", contexto)


@login_required
def cliente_detalle(request, pk):                          # READ (uno) · opcional · solo GET
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, "facturacion/cliente_detalle.html", {"cliente": cliente})


@login_required
def cliente_eliminar(request, pk):                         # DELETE
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":                           # POST: borrar
        nombre = str(cliente)
        cliente.delete()
        messages.success(request, f"Cliente «{nombre}» eliminado.")
        return redirect("facturacion:cliente_lista")
    contexto = {"titulo": "Eliminar cliente", "cliente": cliente}   # GET: pregunta
    return render(request, "facturacion/cliente_eliminar.html", contexto)


# =====================================================================
# MI PERFIL · Reto · relación 1:1 con User
# =====================================================================

@login_required
def mi_perfil(request):                                    # Sin <int:pk>: SIEMPRE el perfil del usuario conectado
    # get_or_create: busca el perfil de este usuario; si no existe, lo crea vacío.
    # Devuelve DOS cosas: el perfil y True/False (si lo acaba de crear).
    perfil, creado = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == "POST":                           # POST: presionó «Guardar cambios»
        form = PerfilForm(request.POST, instance=perfil)   # Datos nuevos + SU perfil
        if form.is_valid():
            form.save()                                    # UPDATE
            messages.success(request, "Tu perfil fue actualizado.")
            return redirect("facturacion:mi_perfil")       # Vuelve a la misma página (Post/Redirect/Get)
        messages.error(request, "Revisa los campos marcados en rojo.")
    else:                                                  # GET: formulario lleno con sus datos
        form = PerfilForm(instance=perfil)

    contexto = {"titulo": "Mi perfil", "form": form, "boton": "Guardar cambios", "perfil": perfil}
    return render(request, "facturacion/mi_perfil.html", contexto)
