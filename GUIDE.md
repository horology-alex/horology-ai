# Guía del repositorio — Horology.AI

Explicación sencilla de cada archivo del proyecto para que cualquier persona del equipo entienda qué hace cada cosa.

---

## Archivos principales

### `api.py`
Es el servidor de la aplicación. Cuando alguien abre la URL de la app, este archivo es el que responde. Hace dos cosas:
- Sirve la página web (`index.html`)
- Recibe los datos de un reloj (modelo, año, estado, material, caja, papeles) y devuelve el precio estimado usando el modelo de IA

Es el único archivo Python que hay que ejecutar para que la app funcione.

### `index.html`
Es la página web que ve el usuario. Contiene todo el diseño visual (estilo terminal financiero) y la lógica del frontend. Cuando el usuario rellena el formulario y pulsa "Valorar", este archivo llama a `api.py` y muestra los resultados con gráficos.

No necesita ninguna instalación — se sirve directamente desde `api.py`.

---

## Archivos de configuración y despliegue

### `Procfile`
Una sola línea que le dice a las plataformas de hosting (Railway, Render, Heroku) cómo arrancar la aplicación. Contiene: `web: gunicorn api:app`

### `Dockerfile`
Instrucciones para construir un contenedor Docker con la aplicación. Lo usan algunas plataformas de hosting (como Railway) para empaquetar y ejecutar la app de forma estandarizada.

### `runtime.txt`
Le dice a la plataforma de hosting qué versión de Python usar (actualmente Python 3.11.9).

### `requirements.txt`
Lista de librerías Python que necesita la app para funcionar. Cuando se despliega, la plataforma las instala automáticamente leyendo este archivo.

---

## Carpeta `data/`

Contiene los archivos de datos que carga `api.py` al arrancar. No se tocan manualmente.

### `data/pricing_model.pkl`
El modelo de Machine Learning ya entrenado. Es un fichero binario (no legible por humanos). Contiene un Random Forest entrenado sobre datos de relojes Rolex. `api.py` lo carga al arrancar y lo usa para hacer predicciones de precio.

### `data/encoders.json`
Lista de todos los modelos Rolex, materiales y estados disponibles. `api.py` lo usa para poblar los desplegables del formulario.

### `data/dataset_stats.json`
Estadísticas globales del dataset original (81.725 relojes): precio medio, precio mediano, etc. Se muestran en la interfaz como referencia.

### `data/scraped_watches.json` / `data/watches_dataset.csv` / `data/watches_dataset.json` / `data/watches.csv`
Archivos intermedios generados durante el proceso de creación del dataset. Ya no se usan activamente por la app — son registros históricos del proceso de entrenamiento.

---

## Documentación

### `CLAUDE.md`
Instrucciones técnicas para Claude (la IA). Se carga automáticamente al inicio de cada conversación con Claude Code para que entienda el proyecto sin tener que leerlo todo desde cero.

### `CHANGELOG.md`
Registro de todos los cambios que se han hecho en el proyecto, con fecha y descripción. Se actualiza en cada sesión de trabajo con Claude.

### `README.md`
Descripción general del proyecto: qué es, cómo instalarlo, rendimiento del modelo, etc.

---

## Lo que se eliminó (y por qué)

En una limpieza anterior se eliminaron varios scripts que solo servían para el desarrollo local y no son necesarios para ejecutar la app:

| Archivo eliminado | Para qué servía |
|---|---|
| `scraper.py` | Descargar anuncios de Chrono24 con un navegador automatizado |
| `batch_processor.py` | Procesar anuncios con IA local (Ollama) |
| `pricing_model.py` | Entrenar una versión pequeña del modelo |
| `train_model_full.py` | Entrenar el modelo grande con el dataset completo |
| `predict_price.py` | Probar predicciones desde la línea de comandos |
| `test_api.py` | Pruebas manuales de la API |
| `src/` | Código de integración con Ollama y OpenAI para extraer datos |
