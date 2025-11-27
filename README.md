# BOLETAS-V1 - Sistema Web de Generación de Boletas de Pago

Sistema web profesional para la generación de boletas de pago mensual, aguinaldo y liquidación.

## 🚀 Características

- ✅ **Aplicación Web** - Accesible desde cualquier navegador
- ✅ **Boletas de pago mensual** con cálculos automáticos
- ✅ **Boletas de aguinaldo** con validación de períodos
- ✅ **Boletas de liquidación** con cálculo de beneficios sociales
- ✅ **Configuración de empresa** (logo, datos, numeración)
- ✅ **Generación de PDFs profesionales** con diseño moderno
- ✅ **Interfaz responsive** y amigable
- ✅ **Numeración automática** de boletas
- ✅ **Descarga directa** de PDFs

## 📋 Requisitos Previos

- Python 3.8 o superior
- Navegador web moderno (Chrome, Firefox, Edge)

## 🔧 Instalación

1. **Clonar o descargar el proyecto**

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Crear logo de ejemplo (opcional)**
```bash
python crear_logo.py
```

## ▶️ Ejecutar la Aplicación

### Windows (PowerShell):
```powershell
python app.py
```

### Linux/Mac:
```bash
python app.py
```

La aplicación estará disponible en: **http://localhost:5000**

## 📁 Estructura del Proyecto

```
BOLETAS-V1/
├── app.py                      # Aplicación Flask principal
├── config/
│   ├── __init__.py
│   ├── empresa.py             # Configuración de empresa
│   └── settings.json          # Archivo de configuración
├── models/
│   ├── __init__.py
│   ├── boleta_mensual.py      # Modelo boleta mensual
│   ├── boleta_aguinaldo.py    # Modelo boleta aguinaldo
│   └── boleta_liquidacion.py  # Modelo boleta liquidación
├── generators/
│   ├── __init__.py
│   └── pdf_generator.py       # Generador de PDFs
├── static/
│   ├── css/
│   │   └── style.css          # Estilos CSS
│   ├── js/
│   │   └── main.js            # JavaScript principal
│   └── uploads/               # Logos subidos
├── templates/
│   ├── index.html             # Página principal
│   ├── config.html            # Configuración
│   ├── mensual.html           # Formulario mensual
│   ├── aguinaldo.html         # Formulario aguinaldo
│   └── liquidacion.html       # Formulario liquidación
├── output/                     # PDFs generados
├── requirements.txt           # Dependencias Python
├── crear_logo.py              # Script crear logo
└── README.md                  # Este archivo
```

## 📖 Guía de Uso

### 1️⃣ Primera Configuración

Al iniciar por primera vez:

1. Abrir http://localhost:5000
2. Ir a **"⚙️ Configuración de Empresa"**
3. Completar datos de la empresa
4. Subir logo (opcional)
5. Guardar configuración

### 2️⃣ Generar Boleta Mensual

1. Click en **"Boleta de Pago Mensual"**
2. Completar datos del empleado
3. Ingresar montos de ingresos y egresos
4. Click en **"Generar PDF"**
5. Descargar el PDF generado

### 3️⃣ Generar Boleta de Aguinaldo

1. Click en **"Boleta de Aguinaldo"**
2. Completar datos del empleado
3. Ingresar fechas (mínimo 90 días)
4. Ingresar promedio de pagos
5. Click en **"Generar PDF"**

### 4️⃣ Generar Boleta de Liquidación

1. Click en **"Boleta de Liquidación"**
2. Completar datos del trabajador
3. Ingresar fechas de ingreso y retiro
4. Completar beneficios y deducciones
5. Click en **"Generar PDF"**

## 🎨 Características de Diseño

- **Interfaz moderna** con diseño responsive
- **Colores profesionales** y fácil navegación
- **Formularios intuitivos** con validación
- **PDFs de alta calidad** con formato profesional
- **Cálculos automáticos** en tiempo real
- **Vista previa** de totales antes de generar

## 📄 Ubicación de PDFs

Los PDFs generados se guardan en la carpeta **`output/`**

Formato del nombre:
- `BOL-000001_Mensual_Juan_Perez.pdf`
- `BOL-000002_Aguinaldo_Maria_Lopez.pdf`
- `BOL-000003_Liquidacion_Carlos_Gomez.pdf`

## 🔐 Seguridad

- Validación de datos en cliente y servidor
- Sanitización de nombres de archivo
- Límite de tamaño para logos (5MB)
- Formatos de imagen permitidos: PNG, JPG, JPEG, GIF

## 🐛 Solución de Problemas

### El servidor no inicia
```bash
# Verificar que el puerto 5000 no esté en uso
# En Windows PowerShell:
Get-NetTCPConnection -LocalPort 5000

# Cambiar el puerto en app.py si es necesario
app.run(debug=True, port=8080)
```

### Error al instalar dependencias
```bash
# Actualizar pip primero
python -m pip install --upgrade pip

# Instalar nuevamente
pip install -r requirements.txt
```

### Los PDFs no se generan
- Verificar permisos de escritura en carpeta `output/`
- Revisar logs en la consola del servidor
- Verificar que todos los campos obligatorios estén completos

## 🔄 Actualización

Para actualizar el sistema:
1. Respaldar carpeta `output/` y `config/settings.json`
2. Descargar nueva versión
3. Restaurar archivos respaldados
4. Ejecutar `pip install -r requirements.txt`

## 📞 Soporte

Para reportar problemas o sugerencias, contacte al administrador del sistema.

## 📜 Licencia

Uso privado - Todos los derechos reservados © 2025

---

**BOLETAS-V1** - Sistema Web de Gestión de Boletas de Pago
