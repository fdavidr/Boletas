# Datos Persistentes en Render

## ⚠️ Importante

Este sistema ahora utiliza **almacenamiento persistente** para guardar datos entre deploys.

## 📁 Estructura de Datos Persistentes

Todos los datos que necesitan persistir entre deploys se guardan en:

```
/opt/render/project/src/data/  (en Render)
data/                           (en desarrollo local)
```

### Contenido del disco persistente:

- **`settings.json`** - Configuración de la empresa
- **`empleados.json`** - Base de datos de empleados
- **`uploads/`** - Logos y archivos subidos
- **`output/`** - PDFs generados

## 🔧 Configuración en Render

El archivo `render.yaml` incluye la configuración del disco:

```yaml
disk:
  name: boletas-data
  mountPath: /opt/render/project/src/data
  sizeGB: 1
```

## 💾 Primer Deploy

En el **primer deploy** después de aplicar estos cambios:

1. ✅ Se creará el disco persistente automáticamente
2. ⚠️ Los datos anteriores (si existen) se perderán
3. 🔄 A partir de ese momento, todos los datos se mantendrán entre deploys

## 📋 Respaldo de Datos (Recomendado)

### Antes del primer deploy con persistencia:

Si ya tienes datos importantes, recomiendo hacer un respaldo manual:

1. Descarga los archivos importantes desde Render:
   - `config/settings.json`
   - `config/empleados.json`
   - Logos de `static/uploads/`

2. Después del deploy, vuelve a cargarlos usando la interfaz web

### Respaldo regular (opcional):

Puedes crear un script para respaldar periódicamente:

```bash
# Desde el shell de Render
tar -czf backup-$(date +%Y%m%d).tar.gz data/
```

## 🚀 Ventajas del Almacenamiento Persistente

- ✅ Los empleados registrados no se pierden
- ✅ La configuración de la empresa se mantiene
- ✅ Los logos subidos permanecen
- ✅ El historial de boletas (PDFs) se conserva
- ✅ El contador de números de boleta no se reinicia

## 🔍 Verificar que funciona

Después del deploy:

1. Agrega un empleado
2. Configura la empresa
3. Genera una boleta
4. Haz un nuevo deploy (cualquier cambio)
5. Verifica que los datos siguen ahí ✅

## ⚙️ Variables de Entorno

El sistema detecta automáticamente si está en Render:

- `RENDER_DISK_PATH=/opt/render/project/src/data` (en Render)
- `data/` (en desarrollo local)

## 📝 Notas Adicionales

- El disco tiene **1 GB** de capacidad (ajustable)
- Los datos persisten incluso si el servicio se detiene
- El disco es específico para este servicio en Render
- Si eliminas el servicio, el disco también se elimina
