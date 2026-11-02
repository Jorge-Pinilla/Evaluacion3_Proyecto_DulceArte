# Dulce Arte – Sistema de gestión para pastelería

Aplicación web y API REST para gestionar una pastelería: pedidos personalizados, tablero Kanban de producción, inventario de insumos con recetas (BOM) y despachos con comprobante fotográfico.

Proyecto de la Evaluación 3 de Backend.  IMPORTANTE!! (Para entrar pide superuser nombre:jorge123 contraseña:jorge123)

**URL desplegada:** `http://34.225.187.217/`
**Documentación Swagger:** `http://34.225.187.217/api/docs/`
**Panel admin:** `http://34.225.187.217/admin/`

## Tecnologías

- Python 3.12+ y Django 6.1
- Django REST Framework 3.18, SimpleJWT (autenticación por token), drf-yasg (Swagger), django-filter, django-cors-headers
- PostgreSQL (`psycopg2-binary`)
- Pillow (fotos de comprobante)
- Despliegue: AWS EC2 (Ubuntu 24.04) con Gunicorn + Nginx como proxy inverso

## Modelos principales

| Modelo | Descripción |
|---|---|
| `User` | Usuario con rol (`ADMIN`, `DUENO`, `VENDEDOR`, `COCINERO`, `REPARTIDOR`) |
| `Insumo` | Materia prima con stock actual y stock crítico |
| `Producto` | Producto del catálogo con precio base |
| `RecetaBOM` | Insumos y cantidad que consume cada producto |
| `Pedido` | Pedido de un producto con diseño, fecha de entrega y estado Kanban |
| `Despacho` | Entrega asociada a un pedido, con repartidor, dirección y foto de comprobante |

## Reglas de negocio

- **Descuento automático de inventario (BOM):** al crear un pedido por la API, se descuentan del stock los insumos de la receta del producto. La operación es atómica: si falta stock de algún insumo, se rechaza y no se descuenta nada.
- **Tablero Kanban:** los pedidos pasan por los estados `RECIBIDO`, `PREPARACION`, `HORNEADO`, `CALIDAD`, `LISTO` y `DESPACHADO`.
- **Confirmación de entrega:** solo un usuario con rol `REPARTIDOR` puede confirmarla, y es obligatorio adjuntar la foto del comprobante. Al confirmar, el pedido pasa a `DESPACHADO`.

## Roles y acceso a las vistas web

| Vista | Roles permitidos |
|---|---|
| Dashboard | Cualquier usuario autenticado |
| Kanban (`/kanban/`) | `VENDEDOR`, `COCINERO`, `DUENO`, `ADMIN` |
| Inventario (`/inventario/`) | `COCINERO`, `DUENO`, `ADMIN` |
| Despachos (`/despachos/`) | `REPARTIDOR`, `DUENO`, `ADMIN` |
| Nuevo pedido (`/pedidos/nuevo/`) | `VENDEDOR`, `DUENO`, `ADMIN` |

Otras rutas web: `/login/`, `/registro/`, `/logout/`.

## API REST

Todos los endpoints requieren autenticación.

| Endpoint | Descripción |
|---|---|
| `POST /api/token/` | Obtiene `access` y `refresh` (JWT) |
| `POST /api/token/refresh/` | Renueva el token de acceso |
| `/api/pedidos/` | CRUD de pedidos |
| `PATCH /api/pedidos/{id}/actualizar_kanban/` | Cambia el estado Kanban |
| `/api/insumos/` | CRUD de insumos |
| `/api/productos/` | CRUD de productos |
| `/api/despachos/` | CRUD de despachos |
| `PATCH /api/despachos/{id}/confirmar_entrega/` | Confirma la entrega con foto (solo `REPARTIDOR`) |
| `/api/docs/` | Documentación Swagger |

### Ejemplo de uso

```bash
# 1. Obtener token
curl -X POST http://<IP_PUBLICA_EC2>/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "cliente_test", "password": "password123"}'

# 2. Listar pedidos con el token
curl http://<IP_PUBLICA_EC2>/api/pedidos/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

# 3. Mover un pedido en el Kanban
curl -X PATCH http://<IP_PUBLICA_EC2>/api/pedidos/1/actualizar_kanban/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"estado": "HORNEADO"}'
```

En Swagger, usa **Authorize** con el valor `Bearer <ACCESS_TOKEN>`.

## Instalación local (Windows)

Requisitos: Python 3.12+ y PostgreSQL.

```bash
git clone https://github.com/Jorge-Pinilla/Evaluacion3_Proyecto_DulceArte.git
cd Evaluacion3_Proyecto_DulceArte
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Crea la base de datos `db_dulcearte` en PostgreSQL (usuario `postgres`, host `localhost`, puerto `5432`) y ajusta la contraseña en `config/settings.py` si es distinta. Luego:

```bash
python manage.py migrate
python manage.py cargar_datos_prueba
python manage.py createsuperuser
python manage.py runserver
```

`cargar_datos_prueba` crea el usuario `cliente_test` (contraseña `password123`) y datos de ejemplo.

> Después de `createsuperuser`, entra a `/admin/` y cambia el **rol** de ese usuario a `ADMIN` o `DUENO`. Por defecto queda como `VENDEDOR` y no podría acceder a Inventario ni Despachos.

## Despliegue en AWS EC2

Arquitectura: `Cliente → Nginx (puerto 80) → socket Unix → Gunicorn → Django → PostgreSQL`.

1. Instancia EC2 con Ubuntu Server 24.04 LTS (Python 3.12). Security Group: SSH (22) desde mi IP y HTTP (80) abierto.
2. Paquetes: `sudo apt install python3-pip python3-venv nginx git postgresql postgresql-contrib -y`
3. Base de datos:
   ```bash
   sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '<CLAVE>';"
   sudo -u postgres createdb db_dulcearte
   ```
4. Proyecto en `~/apps/Evaluacion3_Proyecto_DulceArte` con entorno virtual en `~/apps/venv`. El `requirements.txt` está en UTF-16, así que se convierte antes de instalar:
   ```bash
   iconv -f UTF-16 -t UTF-8 requirements.txt | tr -d '\r' > requirements_linux.txt
   pip install -r requirements_linux.txt
   ```
5. `python manage.py migrate`, `createsuperuser` y `collectstatic --noinput`.
6. Servicio `systemd` (`/etc/systemd/system/gunicorn.service`):
   ```ini
   [Service]
   User=ubuntu
   Group=www-data
   WorkingDirectory=/home/ubuntu/apps/Evaluacion3_Proyecto_DulceArte
   ExecStart=/home/ubuntu/apps/venv/bin/gunicorn --workers 3 --umask 007 --bind unix:/home/ubuntu/apps/dulcearte.sock config.wsgi:application
   ```
7. Nginx (`/etc/nginx/sites-available/dulcearte`): sirve `/static/` desde `static/` y envía el resto al socket de Gunicorn con `proxy_pass http://unix:/home/ubuntu/apps/dulcearte.sock;`. Se elimina el sitio `default` de `sites-enabled`.
8. Permisos para que Nginx (`www-data`) llegue al socket:
   ```bash
   sudo usermod -aG www-data ubuntu
   sudo usermod -aG ubuntu www-data
   sudo chmod 750 /home/ubuntu
   sudo chmod 770 /home/ubuntu/apps
   ```
9. `sudo systemctl restart gunicorn nginx`

Para actualizar tras un cambio en GitHub:

```bash
cd ~/apps/Evaluacion3_Proyecto_DulceArte
git pull
source ../venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

## Estructura del proyecto

```
config/       configuración (settings, urls, wsgi)
core/         modelos, vistas web, admin y comando cargar_datos_prueba
api/          viewsets y serializers de la API REST
templates/    plantillas HTML
static/       archivos estáticos
```

## Autor

Jorge Pinilla
