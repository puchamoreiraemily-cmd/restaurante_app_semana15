
```markdown
# Sistema de Gestión de Restaurante — Semana 15

Aplicación de escritorio modular desarrollada en Python utilizando Tkinter para la interfaz gráfica y JSON para la persistencia local de datos. En esta versión se completa la integración del módulo de ventas con actualización de stock en tiempo real e historial transaccional.

---

## Propósito de la Semana 15

El objetivo principal de la Semana 15 es consolidar la arquitectura por capas (Modelos, Servicios e Interfaz Gráfica) integrando la lógica transaccional de ventas, la vinculación entre eventos de la GUI y la capa de servicios mediante el uso de `command=` y *callbacks*, y asegurando la persistencia de datos del historial comercial en formato JSON.

---

## Evolución Realizada sobre el Proyecto Anterior

A partir del diseño base y las vistas desarrolladas previamente, en esta entrega se incorporaron las siguientes mejoras arquitectónicas y funcionales:

1. **Lógica Completa de Registro de Ventas:** Integración directa entre el catálogo de productos y el panel de ventas, garantizando la verificación de disponibilidad de inventario antes de procesar cualquier transacción.
2. **Actualización Automática de Inventario:** Descuento inmediato de unidades en el catálogo de productos al concretarse una venta.
3. **Manejo de Eventos Avanzado (`command=` y Callbacks):** Vinculación de los componentes interactivos de la GUI con funciones *callback* desacopladas que invocan la capa de servicios sin bloquear ni distorsionar la interfaz gráfica.
4. **Persistencia Transaccional:** Almacenamiento y actualización continua de las transacciones procesadas dentro de la capa de almacenamiento JSON.

---

## Estructura del Sistema

El proyecto mantiene una estructura modular por capas limpia e intuitiva:

```text
restaurante_app/
├── assets/                    # Recursos visuales (íconos, logo y recursos visuales)
│   ├── icon_product.png
│   ├── icon_sale.png
│   ├── icon_user.png
│   └── logo.png
├── datos/                     # Archivos de persistencia local en formato JSON
│   └── restaurante.json       # Documento principal de persistencia centralizada
├── modelos/                   # Entidades de dominio (Clases base de objetos)
│   ├── __init__.py
│   ├── producto.py
│   ├── usuario.py
│   └── venta.py
├── servicios/                 # Lógica de negocio y lectura/escritura JSON
│   ├── __init__.py
│   ├── archivo_servicio.py
│   └── restaurante_servicio.py
├── ui/                        # Componentes y vistas de la interfaz gráfica (Tkinter)
│   ├── __init__.py
│   ├── login_view.py
│   └── main_view.py
├── main.py                    # Punto de entrada principal de la aplicación
└── README.md                  # Documentación del proyecto

```

---

## Nueva Gestión de Ventas

El nuevo flujo transaccional implementado en el sistema funciona de la siguiente manera:

1. **Selección y Validación:** La vista de ventas permite seleccionar un producto del catálogo y especificar la cantidad requerida.
2. **Verificación de Stock:** La capa de servicios (`restaurante_servicio.py`) valida que la cantidad solicitada no supere el inventario disponible.
3. **Cálculo Transaccional:** Se calcula automáticamente el costo total de la compra multiplicando la cantidad por el precio unitario del producto.
4. **Registro y Descuento:** Se efectúa el descuento correspondiente en la cantidad disponible del producto y se genera el registro detallado con fecha, hora, producto, cantidad, total y usuario responsable.

---

## Uso de command= y Callbacks

Para mantener un desacoplamiento efectivo entre la interfaz de usuario (Tkinter) y la lógica de negocio, se implementaron controladores de eventos mediante el atributo `command=` de los botones:

* **Vinculación de Eventos (`command=`):** Los componentes visuales (como los botones "Registrar Venta", "Agregar Producto" o "Guardar Usuario") asignan sus acciones directamente a métodos locales o *callbacks* definidos dentro del controlador de la vista.
* **Controladores Callback:** Al accionarse un botón, el método *callback* recolecta los datos de los campos de entrada (`Entry` o `Combobox`), realiza las validaciones básicas de interfaz y envía la petición a `RestauranteServicio`.
* **Respuesta y Actualización:** Una vez que el servicio retorna la confirmación del proceso, el *callback* se encarga de mostrar un mensaje de notificación (`messagebox`), limpiar los campos de texto y actualizar dinámicamente las tablas (`Treeview`).

---

## Persistencia en ventas.json / restaurante.json

La persistencia de datos se gestiona a través de la capa de servicios (`servicios/archivo_servicio.py` y `servicios/restaurante_servicio.py`), la cual administra la serialización en formato JSON y el manejo de excepciones (`FileNotFoundError` y `JSONDecodeError`):

* **Almacenamiento Centralizado:** Para optimizar la consistencia de los datos y evitar archivos fragmentados, la información del sistema (usuarios, productos y el historial de ventas) se estructura y persiste centralizadamente dentro de `datos/restaurante.json` (pudiendo desglosarse o generar de forma dinámica `ventas.json`, `productos.json` y `usuarios.json` mediante el servicio de archivos).
* **Lectura Inicial:** Al iniciar la aplicación, el sistema verifica la existencia de la fuente de datos. Si no existe o está vacía, se inicializan las estructuras por defecto de forma automática.
* **Escritura Transaccional:** Cada vez que se procesa una venta, la nueva entidad se serializa y actualiza la lista de ventas en la estructura JSON utilizando codificación UTF-8 y formato indentado para garantizar la integridad de los datos.

---

## Pasos para Ejecutar main.py

### Requisitos Previos

* **Python 3.8** o superior instalado en el sistema.
* Bibliotecas estándar incluidas en Python (`tkinter`, `json`, `os`, `datetime`).
* *(Opcional)* Biblioteca **Pillow** para la carga y renderizado de imágenes/íconos en la interfaz gráfica:
```bash
pip install Pillow

```



### Instrucciones de Ejecución

1. Clonar o descargar el repositorio del proyecto:
```bash
git clone [https://github.com/puchamoreiraemily-cmd/restaurante_app.git](https://github.com/puchamoreiraemily-cmd/restaurante_app.git)
cd restaurante_app

```


2. Ejecutar el archivo principal desde la terminal o consola de comandos:
```bash
python main.py

```


3. Iniciar sesión utilizando las credenciales de administrador por defecto:
* **Usuario:** `admin`
* **Contraseña:** `1234`



---

## Autora

* **Emily Silvana Pucha Moreira**
* Carrera de Ingeniería en Tecnologías de la Información — Universidad Estatal Amazónica.

```

```