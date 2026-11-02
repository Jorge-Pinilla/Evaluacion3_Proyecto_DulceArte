# Registro de Prompts e Interacción con IA — Proyecto Dulce Arte

## 1. Diseño de Arquitectura y Base de Datos
-Consulta:Definir modelos en Django para pastelería artesanal con usuarios por rol, inventario BOM, tablero Kanban y rutas de despacho.*
-Resultado: Modelos `User`, `Insumo`, `Producto`, `RecetaBOM`, `Pedido` y `Despacho`.

## 2. Lógica del Descuento Automático de Inventario (BOM)
-Consulta:Implementar la reducción automática de insumos en bodega al guardar un pedido según su RecetaBOM.*
-Resultado:Integración en la vista `crear_pedido_view` iterando sobre los insumos asociados al producto.

## 3. Interfaz del Tablero Kanban y Navegación
-Consulta:Diseñar un tablero Kanban estilizado como whiteboard con post-its e imanes, modal de eliminación y desplazamiento lateral con flechas.*
-Resultado:Plantilla `kanban.html` interactiva con Bootstrap Icons y JavaScript de scroll horizontal.

## 4. Firma Digital y Evidencia Fotográfica en Despachos
-Consulta:Módulo de despacho con firma digital táctil en Canvas HTML5 y carga de imagen de comprobante.*
-Resultado:Formulario dinámico en modal con captura de trazos táctiles y gestión de archivo fotográfico.

## 5. Personalización y Manejo de Errores
-Consulta:Configuración de handler404 personalizado en Django manteniendo estáticos activos con DEBUG=False.*
-Resultado:Plantilla `404.html` estilizada y mapeo en `config/urls.py`.