# Sistema de Gestión de Aerolínea

## ✈️ Descripción del Proyecto

Este es un sistema completo de gestión de aerolínea desarrollado con Django. Permite a los usuarios (clientes, empleados y administradores) interactuar con la plataforma para gestionar vuelos, reservas, pasajeros y otros aspectos operativos. El proyecto está diseñado con una arquitectura modular y cuenta con soporte para múltiples idiomas (internacionalización).

## ✨ Características Principales

* **Autenticación de Usuarios:** Sistema de inicio de sesión y registro de usuarios con perfiles diferenciados (cliente, empleado, admin).
* **Gestión de Vuelos:** Creación, edición y eliminación de vuelos por parte de empleados y administradores.
* **Gestión de Reservas:** Los clientes pueden buscar, reservar y gestionar sus propios vuelos.
* **Gestión de Pasajeros:** Los usuarios pueden agregar y editar la información de sus pasajeros.
* **Reportes:** Módulo de reportes para administradores y empleados.
* **Interfaz de Usuario (UI):** Diseño moderno y responsivo gracias a Bootstrap 5.3.3 y Font Awesome.
* **Internacionalización (i18n):** Soporte para español (es) e inglés (en), permitiendo cambiar el idioma de la interfaz fácilmente.

## 🚀 Tecnologías Utilizadas

* **Backend:** Python 3.10+ y Django 5.2.4
* **Frontend:** HTML5, CSS3, JavaScript
* **Framework CSS:** Bootstrap 5.3.3
* **Base de Datos:** SQLite (por defecto, para desarrollo)
* **Versión de Django:** 5.2.4

## 🛠️ Instalación y Configuración

Sigue estos pasos para tener una copia local del proyecto en funcionamiento.

### Requisitos Previos

* Python 3.10+
* `pip` (gestor de paquetes de Python)

### Pasos de Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone [git@github.com:OctavioVictorio/gestios_aerolineas.git]
    cd gestios_aerolineas
    ```
    ```bash
    git clone [https://github.com/OctavioVictorio/gestios_aerolineas.git]
    cd gestios_aerolineas
    ```

2.  **Crear y activar el entorno virtual:**
    ```bash
    python3 -m venv .enviroment
    source .enviroment/bin/activate
    ```

3.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar la base de datos y migrar:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  **Crear un superusuario (administrador):**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Compilar los archivos de internacionalización:**
    Este paso es crucial para que las traducciones funcionen correctamente.
    ```bash
    python manage.py compilemessages
    ```

7.  **Iniciar el servidor de desarrollo:**
    ```bash
    python manage.py runserver
    ```
    El proyecto estará disponible en `http://127.0.0.1:8000/`.

## 🌐 Internacionalización (i18n)

El proyecto solo tiene el panel del cliente y el navbar con traduccion.

### Cómo funciona

* **Configuración:** Los idiomas disponibles se definen en `settings.py` y las rutas en `urls.py` usando `i18n_patterns`.
* **Traducciones:** Los archivos de traducción se encuentran en la carpeta `locale/`.
* **Cambiar de idioma:** La barra de navegación incluye un selector de idioma que permite a los usuarios cambiar entre "Español" y "English".


## Alumno

Este proyecto fue desarrollado por [Victorio Octacio].
