Dulce Arte — Sistema de Trazabilidad y Pedidos para Pastelería Artesanal

Este proyecto es una aplicación web fullstack desarrollada para gestionar de manera integral una pastelería artesanal. El sistema controla pedidos personalizados, administra el inventario mediante Lista de Materiales (BOM), organiza la cocina con un tablero Kanban interactivo y gestiona las rutas de despacho con firmas digitales.

Acceso al Sistema (Despliegue en AWS EC2)
- **Aplicación Web (Inicio):** `(http://100.58.108.249/)`
- **Panel de Administración (Django Admin):** `http://100.58.108.249/admin/`
- **Documentación de API (Swagger):** `http://100.58.108.249/api/docs/`

> El sistema está completamente desplegado en una instancia EC2 de AWS Academy utilizando PostgreSQL, Gunicorn y Nginx.

---

Funcionalidades Principales Implementadas
1. **Cotización y Pedidos:** Registro de órdenes personalizadas asociadas al catálogo de productos y fechas de entrega.
2. **Tablero Kanban de Cocina:** Gestión visual del flujo de trabajo (Recibido → En Preparación → Horneado/Decorado → Control de Calidad → Listo).
3. **Inventario Automatizado (BOM):** Descuento automático de insumos en bodega según la receta exacta al momento de registrar un pedido.
4. **Despachos con Evidencia:** Confirmación de rutas de entrega mediante firma digital en pantalla (Canvas HTML5) o captura fotográfica.
5. **Control de Acceso por Roles:** Permisos restringidos para Dueño, Administrador, Vendedor, Cocinero y Repartidor.

---

Stack Tecnológico
- **Backend:** Python 3, Django, Django REST Framework (DRF)
- **Base de Datos:** PostgreSQL
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript (Fetch API, Canvas API)
- **Infraestructura:** AWS EC2 (Ubuntu), Gunicorn, Nginx

---

Instrucciones de Ejecución Local

Si deseas correr este proyecto en un entorno de desarrollo local, sigue estos pasos:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/Jorge-Pinilla/DulceArte-Django.git](https://github.com/Jorge-Pinilla/DulceArte-Django.git)
   cd DulceArte-Django
