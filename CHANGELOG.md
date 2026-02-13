# Changelog — Horology.AI

Registro de todos los cambios realizados en el proyecto, ordenados del más reciente al más antiguo.

---

## 2026-02-12

### Documentación
- Creado `GUIDE.md` con explicación en lenguaje sencillo de cada archivo del repo
- Creado `CHANGELOG.md` (este archivo) para registrar cambios futuros
- Añadidos comentarios detallados en español dentro de `api.py`
- Actualizado `CLAUDE.md` con instrucción de mantener el changelog

### Despliegue
- Añadido `Dockerfile` para compatibilidad con Railway (builder Docker)
- Añadido `runtime.txt` especificando Python 3.11.9
- Corregido error de versión Python (`3.11.0` → `3.11.9`) en `runtime.txt`

### Limpieza del repo
- Eliminados todos los scripts de desarrollo local: `scraper.py`, `batch_processor.py`, `pricing_model.py`, `train_model_full.py`, `predict_price.py`, `test_api.py`, `crear.py`
- Eliminados archivos HTML de prueba: `test.html`, `index_old.html`
- Eliminado directorio `src/` (integración Ollama/OpenAI, solo usada en local)
- Limpiado `.gitignore` eliminando referencias a archivos ya inexistentes

### Backend (`api.py`)
- Reescrito completamente para usar `pricing_model.pkl` (el modelo que sí existe en el repo)
- Corregido el schema de features: el modelo original usa 9 features, no 6
- Añadido soporte para variable de entorno `PORT` (necesario para hosting en la nube)
- Eliminada dependencia de `pandas` y `rolex_dataset.csv` (ya no necesarios)

### Dependencias (`requirements.txt`)
- Reemplazadas dependencias antiguas (`openai`, `pandas`, `httpx`, `python-dotenv`) por las reales: `flask`, `gunicorn`, `scikit-learn`

### Infraestructura
- Creado `Procfile` con comando de arranque para Railway/Render/Heroku
- Creado `CLAUDE.md` con documentación técnica de arquitectura

---

## Antes de 2026-02-12 (historial previo)

Los commits anteriores están disponibles en el historial de git. Los más relevantes:

- `48b6c18` — Añadidos tooltips, botón copiar resultados, info extendida de modelos e histograma de distribución de precios
- `91ac1b7` — Añadidos tooltips, botón copiar resultados e info extendida de modelos
- `5a5f0a3` — Modo comparación completo con gráficos duales y comparación de estadísticas
- `690f309` — README profesional añadido
- `d9fde8e` — Commit inicial: terminal de precios Horology.IA
