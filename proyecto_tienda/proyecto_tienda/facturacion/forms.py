from django import forms
from .models import Marca, Producto, Categoria, Cliente, Perfil


# =====================================================================
# MARCA (Unidad 2)
# =====================================================================
class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ["nombre", "pais_origen", "activo"]
        labels = {"nombre": "Nombre de la marca"}
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Samsung"}),
            "pais_origen": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Corea del Sur"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 letras.")
        return nombre.title()


# =====================================================================
# PRODUCTO (Unidad 3)
# =====================================================================
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["nombre", "descripcion", "marca", "categorias", "precio", "stock", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Laptop Pro 14"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "marca": forms.Select(attrs={"class": "form-select"}),                       # 1:N → lista desplegable
            "categorias": forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),  # N:M → casillas
            "precio": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["marca"].queryset = Marca.objects.filter(activo=True)   # Solo marcas activas
        self.fields["marca"].empty_label = "— Elige una marca —"

    def clean_precio(self):
        precio = self.cleaned_data["precio"]
        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor que 0.")
        return precio


# =====================================================================
# CATEGORÍA (Unidad 5 · Tarea 1)
# =====================================================================
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion", "activo"]
        labels = {"nombre": "Nombre de la categoría"}
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Laptops"}),
            # Textarea = caja grande de varias líneas (igual que la descripción de ProductoForm)
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_nombre(self):                              # Validación propia: clean_ + nombre del campo
        nombre = self.cleaned_data["nombre"].strip()     # Quitamos espacios: "  ofertas  " → "ofertas"
        if len(nombre) < 3:                              # Mínimo 3 letras
            raise forms.ValidationError("El nombre debe tener al menos 3 letras.")
        # Solo la PRIMERA letra en mayúscula; el resto queda como lo escribió ("Gaming y PC" no se daña)
        # Django revisa unique=True DESPUÉS de este método, así que "ofertas" y "Ofertas" cuentan como repetidas
        return nombre[0].upper() + nombre[1:]


# =====================================================================
# CLIENTE (Unidad 5 · Tarea 2)
# =====================================================================
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        # Todos los campos MENOS fecha_registro (auto_now_add: se llena sola)
        fields = ["cedula", "nombres", "apellidos", "email", "telefono", "direccion"]
        widgets = {
            "cedula": forms.TextInput(attrs={"class": "form-control", "placeholder": "10 dígitos", "maxlength": "10"}),
            "nombres": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Ana María"}),
            "apellidos": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Pérez Mora"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "correo@ejemplo.com"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "0991234567"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data["cedula"].strip()     # Texto ya limpio de espacios
        if len(cedula) != 10:                            # Exactamente 10 caracteres
            raise forms.ValidationError("La cédula debe tener exactamente 10 dígitos.")
        if not cedula.isdigit():                         # isdigit(): True si TODOS son números
            raise forms.ValidationError("La cédula solo puede tener números.")
        return cedula                                    # Que no se repita lo revisa unique=True del modelo


# =====================================================================
# PERFIL (Reto · relación 1:1)
# =====================================================================
class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ["cedula", "telefono", "direccion", "cargo"]   # SIN usuario: nadie lo elige
        widgets = {
            "cedula": forms.TextInput(attrs={"class": "form-control", "maxlength": "10"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "cargo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Vendedor"}),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data["cedula"].strip()
        if cedula and (len(cedula) != 10 or not cedula.isdigit()):   # Opcional, pero si la escribe debe ser válida
            raise forms.ValidationError("La cédula debe tener 10 dígitos y solo números.")
        return cedula
