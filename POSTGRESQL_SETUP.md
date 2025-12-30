# 🐘 PostgreSQL en Render - Guía de Configuración

## ✅ ¿Qué se implementó?

El sistema ahora usa **PostgreSQL gratuito** de Render en lugar de archivos JSON. Esto permite:

- ✅ **Datos persistentes** entre deploys
- ✅ **100% Gratuito** (plan free de Render)
- ✅ **Más rápido** que archivos
- ✅ **Más robusto** y profesional

## 📋 Pasos para Configurar PostgreSQL en Render

### **Paso 1: Agregar PostgreSQL a tu Servicio**

1. Ve a tu Dashboard de Render: https://dashboard.render.com
2. Selecciona tu servicio "boletas-v1"
3. En el menú lateral, busca **"Environment"**
4. Haz scroll hasta la sección **"Add from Gallery"**
5. Busca **PostgreSQL** y haz clic en **"Add"**
6. Configuración:
   - **Name**: `boletas-db`
   - **Database**: `boletas` (o el nombre que prefieras)
   - **User**: (se genera automáticamente)
   - **Region**: Mismo que tu servicio web
   - **Plan**: **Free** ✅
7. Haz clic en **"Create Database"**

### **Paso 2: Conectar la Base de Datos**

Render creará automáticamente la variable de entorno `DATABASE_URL` en tu servicio web.

**Verificar la conexión:**
1. En tu servicio web, ve a **Environment**
2. Busca la variable `DATABASE_URL`
3. Debería verse algo como: `postgres://user:pass@host/database`

Si no aparece automáticamente:
1. Copia la **Internal Database URL** de tu PostgreSQL
2. Agrégala manualmente como `DATABASE_URL` en tu servicio web

### **Paso 3: Hacer el Deploy**

Una vez configurada la base de datos:

1. Haz push de los nuevos cambios (ya lo hicimos)
2. Render detectará los cambios y hará deploy automáticamente
3. El sistema creará las tablas automáticamente al iniciar

### **Paso 4: Verificar que Funciona**

Después del deploy (5-10 minutos):

1. Ve a tu aplicación
2. Configura tu empresa
3. Agrega empleados
4. Haz cualquier cambio y push
5. Verifica que los datos siguen ahí ✅

## 📊 Estructura de la Base de Datos

El sistema creará automáticamente estas tablas:

### **Tabla: empresa_config**
- Configuración de la empresa (nombre, NIT, etc.)
- Contador de números de boleta
- Ruta del logo

### **Tabla: empleados**
- Datos de empleados (nombre, CI, cargo, sueldo)
- Fecha de ingreso
- Estado activo/inactivo

## 🔍 Verificar el Estado de la Base de Datos

### **Desde el Dashboard de Render:**

1. Ve a tu base de datos PostgreSQL
2. Haz clic en **"Shell"**
3. Ejecuta comandos SQL:

```sql
-- Ver todas las tablas
\dt

-- Ver empleados
SELECT * FROM empleados;

-- Ver configuración de empresa
SELECT * FROM empresa_config;
```

## 🚨 Solución de Problemas

### **Error: "DATABASE_URL not found"**

**Solución:**
1. Asegúrate de haber agregado PostgreSQL desde el dashboard
2. Verifica que `DATABASE_URL` exista en Environment
3. Si no existe, cópiala manualmente de la base de datos

### **Error: "Connection refused"**

**Solución:**
1. Espera unos minutos (la base de datos puede tardar en inicializarse)
2. Verifica que el plan de la base de datos sea "Free" y esté activo
3. Reinicia el servicio web

### **Los datos siguen borrándose**

**Causas posibles:**
1. PostgreSQL no está configurada correctamente
2. `DATABASE_URL` no está definida (el sistema usa SQLite temporal)

**Solución:**
1. Verifica que PostgreSQL esté activa en Render
2. Confirma que `DATABASE_URL` existe en Environment
3. Revisa los logs para ver si hay errores de conexión

## 💾 Archivos que AÚN se Almacenan Localmente

Nota: Los **logos** y **PDFs** todavía se guardan en el sistema de archivos temporal.

### **Para producción estable:**

Considera usar:
- **Cloudinary** o **ImgBB** para logos (gratis)
- **Amazon S3** o similar para PDFs (bajo costo)

Por ahora, los PDFs son temporales (se borran con cada deploy), pero la configuración y empleados son permanentes.

## 🎯 Resumen

- ✅ **Empleados**: Persistentes en PostgreSQL
- ✅ **Configuración**: Persistente en PostgreSQL
- ✅ **Números de boleta**: Persistentes (contador en DB)
- ⚠️ **Logos**: Temporales (se borran con deploy)
- ⚠️ **PDFs generados**: Temporales

### **Para logos permanentes:**

Puedes subir el logo después de cada deploy (toma 10 segundos) o implementar almacenamiento en la nube.

¿Necesitas ayuda implementando almacenamiento de archivos en la nube?
