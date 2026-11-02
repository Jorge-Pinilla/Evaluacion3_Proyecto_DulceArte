from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .models import Pedido, Insumo, Despacho, Producto, RecetaBOM, User

# Multiplicador base para garantizar stock inicial suficiente para 15 pasteles
CANTIDAD_PASTELES_STOCK = 15

# Catálogo maestro de recetas e ingredientes basado en la lista consolidada
RECETAS_CATALOGO = {
    "Pastel de fresa": {
        "precio": 19990,
        "ingredientes": [
            {"nombre": "Harina de Trigo", "unidad": "Kg", "cantidad": 0.40},
            {"nombre": "Azúcar Flor / Glas", "unidad": "Kg", "cantidad": 0.30},
            {"nombre": "Mantequilla", "unidad": "Kg", "cantidad": 0.20},
            {"nombre": "Huevos", "unidad": "Unidades", "cantidad": 4.00},
            {"nombre": "Leche Entera", "unidad": "Litros", "cantidad": 0.25},
            {"nombre": "Polvo de Hornear", "unidad": "Kg", "cantidad": 0.02},
            {"nombre": "Esencia de Vainilla", "unidad": "Litros", "cantidad": 0.01},
            {"nombre": "Fresas Frescas", "unidad": "Kg", "cantidad": 0.50},
            {"nombre": "Crema para Batir", "unidad": "Litros", "cantidad": 0.40},
        ]
    },
    "Tiramisú": {
        "precio": 21990,
        "ingredientes": [
            {"nombre": "Queso Mascarpone", "unidad": "Kg", "cantidad": 0.50},
            {"nombre": "Huevos", "unidad": "Unidades", "cantidad": 5.00},
            {"nombre": "Azúcar Granulada", "unidad": "Kg", "cantidad": 0.20},
            {"nombre": "Café Espresso", "unidad": "Litros", "cantidad": 0.30},
            {"nombre": "Bizcochos de Soletilla", "unidad": "Kg", "cantidad": 0.30},
            {"nombre": "Cacao en Polvo", "unidad": "Kg", "cantidad": 0.05},
            {"nombre": "Licor (Amaretto/Ron)", "unidad": "Litros", "cantidad": 0.05},
        ]
    },
    "Pastel de zanahoria": {
        "precio": 17990,
        "ingredientes": [
            {"nombre": "Zanahoria Rallada", "unidad": "Kg", "cantidad": 0.40},
            {"nombre": "Harina de Trigo", "unidad": "Kg", "cantidad": 0.35},
            {"nombre": "Azúcar Moreno", "unidad": "Kg", "cantidad": 0.30},
            {"nombre": "Huevos", "unidad": "Unidades", "cantidad": 4.00},
            {"nombre": "Aceite Vegetal", "unidad": "Litros", "cantidad": 0.20},
            {"nombre": "Canela en Polvo", "unidad": "Kg", "cantidad": 0.01},
            {"nombre": "Nuez Moscada", "unidad": "Kg", "cantidad": 0.005},
            {"nombre": "Polvo de Hornear", "unidad": "Kg", "cantidad": 0.015},
            {"nombre": "Bicarbonato de Sodio", "unidad": "Kg", "cantidad": 0.01},
            {"nombre": "Nueces Picadas", "unidad": "Kg", "cantidad": 0.15},
            {"nombre": "Queso Crema", "unidad": "Kg", "cantidad": 0.30},
            {"nombre": "Mantequilla", "unidad": "Kg", "cantidad": 0.10},
            {"nombre": "Azúcar Flor / Glas", "unidad": "Kg", "cantidad": 0.20},
        ]
    },
    "Torta Selva Negra": {
        "precio": 23990,
        "ingredientes": [
            {"nombre": "Harina de Trigo", "unidad": "Kg", "cantidad": 0.35},
            {"nombre": "Cacao en Polvo", "unidad": "Kg", "cantidad": 0.10},
            {"nombre": "Azúcar Granulada", "unidad": "Kg", "cantidad": 0.30},
            {"nombre": "Huevos", "unidad": "Unidades", "cantidad": 5.00},
            {"nombre": "Mantequilla", "unidad": "Kg", "cantidad": 0.15},
            {"nombre": "Cerezas en Almíbar", "unidad": "Kg", "cantidad": 0.30},
            {"nombre": "Crema para Batir", "unidad": "Litros", "cantidad": 0.50},
            {"nombre": "Chocolate Amargo (Virutas)", "unidad": "Kg", "cantidad": 0.15},
        ]
    },
    "Pastel de colibrí": {
        "precio": 20990,
        "ingredientes": [
            {"nombre": "Harina de Trigo", "unidad": "Kg", "cantidad": 0.40},
            {"nombre": "Azúcar Granulada", "unidad": "Kg", "cantidad": 0.30},
            {"nombre": "Aceite Vegetal", "unidad": "Litros", "cantidad": 0.20},
            {"nombre": "Huevos", "unidad": "Unidades", "cantidad": 3.00},
            {"nombre": "Plátanos Maduros", "unidad": "Kg", "cantidad": 0.35},
            {"nombre": "Piña Triturada", "unidad": "Kg", "cantidad": 0.25},
            {"nombre": "Nueces Pecanas", "unidad": "Kg", "cantidad": 0.15},
            {"nombre": "Canela en Polvo", "unidad": "Kg", "cantidad": 0.01},
            {"nombre": "Queso Crema", "unidad": "Kg", "cantidad": 0.30},
        ]
    },
    "Pastel de café": {
        "precio": 18990,
        "ingredientes": [
            {"nombre": "Harina de Trigo", "unidad": "Kg", "cantidad": 0.35},
            {"nombre": "Azúcar Granulada", "unidad": "Kg", "cantidad": 0.25},
            {"nombre": "Mantequilla", "unidad": "Kg", "cantidad": 0.25},
            {"nombre": "Huevos", "unidad": "Unidades", "cantidad": 4.00},
            {"nombre": "Café Espresso", "unidad": "Litros", "cantidad": 0.15},
            {"nombre": "Polvo de Hornear", "unidad": "Kg", "cantidad": 0.015},
            {"nombre": "Leche Entera", "unidad": "Litros", "cantidad": 0.15},
            {"nombre": "Azúcar Flor / Glas", "unidad": "Kg", "cantidad": 0.20},
        ]
    },
    "Pastel de plátano": {
        "precio": 16990,
        "ingredientes": [
            {"nombre": "Plátanos Maduros", "unidad": "Kg", "cantidad": 0.45},
            {"nombre": "Harina de Trigo", "unidad": "Kg", "cantidad": 0.35},
            {"nombre": "Azúcar Granulada", "unidad": "Kg", "cantidad": 0.25},
            {"nombre": "Mantequilla", "unidad": "Kg", "cantidad": 0.15},
            {"nombre": "Huevos", "unidad": "Unidades", "cantidad": 3.00},
            {"nombre": "Bicarbonato de Sodio", "unidad": "Kg", "cantidad": 0.01},
            {"nombre": "Yogur / Leche", "unidad": "Litros", "cantidad": 0.15},
        ]
    },
    "Pastel de terciopelo rojo": {
        "precio": 22990,
        "ingredientes": [
            {"nombre": "Harina de Trigo", "unidad": "Kg", "cantidad": 0.40},
            {"nombre": "Cacao en Polvo", "unidad": "Kg", "cantidad": 0.03},
            {"nombre": "Azúcar Granulada", "unidad": "Kg", "cantidad": 0.35},
            {"nombre": "Mantequilla", "unidad": "Kg", "cantidad": 0.20},
            {"nombre": "Huevos", "unidad": "Unidades", "cantidad": 3.00},
            {"nombre": "Colorante Rojo", "unidad": "Litros", "cantidad": 0.01},
            {"nombre": "Suero de Leche", "unidad": "Litros", "cantidad": 0.25},
            {"nombre": "Vinagre Blanco", "unidad": "Litros", "cantidad": 0.01},
            {"nombre": "Queso Crema", "unidad": "Kg", "cantidad": 0.35},
        ]
    },
    "Pastel de almendras": {
        "precio": 21990,
        "ingredientes": [
            {"nombre": "Harina de Almendra", "unidad": "Kg", "cantidad": 0.25},
            {"nombre": "Harina de Trigo", "unidad": "Kg", "cantidad": 0.20},
            {"nombre": "Azúcar Granulada", "unidad": "Kg", "cantidad": 0.25},
            {"nombre": "Mantequilla", "unidad": "Kg", "cantidad": 0.20},
            {"nombre": "Huevos", "unidad": "Unidades", "cantidad": 4.00},
            {"nombre": "Extracto de Almendra", "unidad": "Litros", "cantidad": 0.01},
            {"nombre": "Almendras Laminadas", "unidad": "Kg", "cantidad": 0.10},
        ]
    },
    "Pastel de arándanos": {
        "precio": 19990,
        "ingredientes": [
            {"nombre": "Harina de Trigo", "unidad": "Kg", "cantidad": 0.35},
            {"nombre": "Azúcar Granulada", "unidad": "Kg", "cantidad": 0.25},
            {"nombre": "Mantequilla", "unidad": "Kg", "cantidad": 0.18},
            {"nombre": "Huevos", "unidad": "Unidades", "cantidad": 3.00},
            {"nombre": "Arándanos Frescos", "unidad": "Kg", "cantidad": 0.35},
            {"nombre": "Ralladura de Limón", "unidad": "Kg", "cantidad": 0.02},
            {"nombre": "Leche Entera", "unidad": "Litros", "cantidad": 0.15},
        ]
    },
    "Pastel de frambuesa y almendra": {
        "precio": 24990,
        "ingredientes": [
            {"nombre": "Harina de Almendra", "unidad": "Kg", "cantidad": 0.20},
            {"nombre": "Harina de Trigo", "unidad": "Kg", "cantidad": 0.20},
            {"nombre": "Azúcar Granulada", "unidad": "Kg", "cantidad": 0.25},
            {"nombre": "Mantequilla", "unidad": "Kg", "cantidad": 0.20},
            {"nombre": "Huevos", "unidad": "Unidades", "cantidad": 4.00},
            {"nombre": "Frambuesas Frescas", "unidad": "Kg", "cantidad": 0.30},
            {"nombre": "Mermelada de Frambuesa", "unidad": "Kg", "cantidad": 0.15},
            {"nombre": "Almendras Laminadas", "unidad": "Kg", "cantidad": 0.10},
        ]
    }
}


def inicializar_bodega_completa():
    """Crea los insumos, productos y recetas BOM iniciales sin modificar el stock si ya existen."""
    for nombre_pastel, datos in RECETAS_CATALOGO.items():
        producto, _ = Producto.objects.get_or_create(
            nombre=nombre_pastel,
            defaults={
                'descripcion': f'Delicioso {nombre_pastel} artesanal con ingredientes seleccionados.',
                'precio_base': datos["precio"]
            }
        )

        for ing in datos["ingredientes"]:
            stock_minimo_15_pasteles = round(ing["cantidad"] * CANTIDAD_PASTELES_STOCK, 2)
            
            insumo_obj, _ = Insumo.objects.get_or_create(
                nombre=ing["nombre"],
                defaults={
                    'unidad_medida': ing["unidad"],
                    'stock_actual': stock_minimo_15_pasteles,
                    'stock_critico': round(stock_minimo_15_pasteles * 0.2, 2)
                }
            )

            RecetaBOM.objects.get_or_create(
                producto=producto,
                insumo=insumo_obj,
                defaults={'cantidad_necesaria': ing["cantidad"]}
            )


# --- AUTENTICACIÓN Y REGISTRO ---

def registro_view(request):
    """Permite el registro de nuevos usuarios seleccionando su rol."""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está registrado.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password, role=role)
            login(request, user)
            messages.success(request, f'¡Bienvenido/a {username}! Registro exitoso.')
            return redirect('dashboard')
            
    return render(request, 'registro.html')


def login_view(request):
    """Inicio de sesión en el sistema Dulce Arte."""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """Cierra la sesión activa del usuario."""
    logout(request)
    return redirect('login')


# --- VISTAS PRINCIPALES CON CONTROL DE PERMISOS ---

@login_required
def dashboard_view(request):
    """Vista principal con el resumen de la pastelería."""
    return render(request, 'dashboard.html')


@login_required
def kanban_view(request):
    """Tablero Kanban para cocina y taller. Accesible para Vendedor, Cocinero, Dueño y Admin."""
    if request.user.role not in ['VENDEDOR', 'COCINERO', 'DUENO', 'ADMIN']:
        messages.error(request, 'No tienes permisos para acceder al tablero Kanban.')
        return redirect('dashboard')
        
    pedidos = Pedido.objects.exclude(estado='DESPACHADO').order_by('fecha_entrega')
    return render(request, 'kanban.html', {'pedidos': pedidos})


@login_required
def inventario_view(request):
    """Vista de stock de insumos (BOM). Accesible para Cocinero, Dueño y Admin."""
    if request.user.role not in ['COCINERO', 'DUENO', 'ADMIN']:
        messages.error(request, 'No tienes permisos para gestionar el inventario (BOM).')
        return redirect('dashboard')

    inicializar_bodega_completa()
    insumos = Insumo.objects.all().order_by('nombre')
    return render(request, 'inventario.html', {'insumos': insumos})


@login_required
def despachos_view(request):
    """Muestra las rutas activas solo para pedidos que están 'LISTO' para despacho."""
    if request.user.role not in ['REPARTIDOR', 'DUENO', 'ADMIN']:
        messages.error(request, 'No tienes permisos para acceder al módulo de despachos.')
        return redirect('dashboard')

    # Filtra los despachos mostrando solo aquellos cuyo pedido asociado esté en estado 'LISTO'
    despachos = Despacho.objects.filter(
        confirmacion_firma=False, 
        pedido__estado='LISTO'
    ).order_by('pedido__fecha_entrega')
    
    # Filtra los pedidos manuales que estén en estado 'LISTO' pero sin despacho asignado
    pedidos_sin_despacho = Pedido.objects.filter(
        despacho__isnull=True, 
        estado='LISTO'
    ).order_by('fecha_entrega')
    
    return render(request, 'despachos.html', {
        'despachos': despachos,
        'pedidos_sin_despacho': pedidos_sin_despacho
    })


@login_required
def crear_pedido_view(request):
    """Registra pedido, descuenta BOM y genera despacho. Accesible para Vendedor, Dueño y Admin."""
    if request.user.role not in ['VENDEDOR', 'DUENO', 'ADMIN']:
        messages.error(request, 'No tienes permisos para registrar nuevos pedidos.')
        return redirect('kanban')

    inicializar_bodega_completa()
    productos = Producto.objects.all()

    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        nombre_cliente = request.POST.get('nombre_cliente')
        direccion_entrega = request.POST.get('direccion_entrega', 'Retiro en tienda')
        detalles = request.POST.get('detalles_diseno')
        fecha_entrega = request.POST.get('fecha_entrega')
        
        producto = get_object_or_404(Producto, id=producto_id)
        
        pedido = Pedido.objects.create(
            cliente=request.user,
            nombre_cliente=nombre_cliente,
            producto=producto,
            detalles_diseno=detalles,
            fecha_entrega=fecha_entrega,
            estado='RECIBIDO'
        )
        
        Despacho.objects.create(
            pedido=pedido,
            repartidor=request.user,
            direccion_entrega=direccion_entrega,
            confirmacion_firma=False
        )
        
        items_receta = RecetaBOM.objects.filter(producto=producto)
        for item in items_receta:
            insumo = item.insumo
            insumo.stock_actual = max(0.0, float(insumo.stock_actual) - float(item.cantidad_necesaria))
            insumo.save()
            
        return redirect('kanban')
        
    return render(request, 'crear_pedido.html', {'productos': productos})


@login_required
def completar_despacho_view(request, despacho_id):
    """Procesa la entrega con firma digital y/o foto comprobante."""
    if request.method == 'POST':
        despacho = get_object_or_404(Despacho, id=despacho_id)
        despacho.confirmacion_firma = True
        
        if 'foto_comprobante' in request.FILES:
            despacho.foto_comprobante = request.FILES['foto_comprobante']
            
        despacho.save()
        despacho.pedido.estado = 'DESPACHADO'
        despacho.pedido.save()
        
    return redirect('despachos')


@login_required
def crear_despacho_manual_view(request):
    """Asigna la ruta de despacho al pedido seleccionado."""
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        direccion = request.POST.get('direccion_entrega')
        
        pedido = get_object_or_404(Pedido, id=pedido_id)
        
        despacho, created = Despacho.objects.get_or_create(
            pedido=pedido,
            defaults={
                'repartidor': request.user,
                'direccion_entrega': direccion,
                'confirmacion_firma': False
            }
        )
        if not created:
            despacho.direccion_entrega = direccion
            despacho.confirmacion_firma = False
            despacho.save()

    return redirect('despachos')


@login_required
def eliminar_pedido_view(request, pedido_id):
    """Vista para eliminar un pedido del sistema desde el tablero Kanban."""
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        pedido.delete()
    return redirect('kanban')


@login_required
def agregar_insumo_view(request):
    """Vista para registrar un nuevo insumo en la bodega."""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        unidad_medida = request.POST.get('unidad_medida')
        stock_actual = request.POST.get('stock_actual', 0)
        stock_critico = request.POST.get('stock_critico', 0)
        
        Insumo.objects.create(
            nombre=nombre,
            unidad_medida=unidad_medida,
            stock_actual=stock_actual,
            stock_critico=stock_critico
        )
    return redirect('inventario')


@login_required
def reabastecer_insumo_view(request, insumo_id):
    """Vista para sumar stock a un insumo existente."""
    if request.method == 'POST':
        insumo = get_object_or_404(Insumo, id=insumo_id)
        cantidad_sumar = float(request.POST.get('cantidad', 0))
        insumo.stock_actual = float(insumo.stock_actual) + cantidad_sumar
        insumo.save()
    return redirect('inventario')


@login_required
def eliminar_insumo_view(request, insumo_id):
    """Vista para eliminar un insumo de la bodega."""
    if request.method == 'POST':
        insumo = get_object_or_404(Insumo, id=insumo_id)
        insumo.delete()
    return redirect('inventario')


def error_404_view(request, exception):
    """Vista personalizada para el manejo de errores 404 (Página no encontrada)."""
    return render(request, '404.html', status=404)