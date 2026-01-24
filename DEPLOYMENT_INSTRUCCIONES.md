# 📋 Instrucciones de Deployment - Solución Logo Persistente

## 🎯 Objetivo
Implementar almacenamiento permanente del logo en PostgreSQL para evitar que desaparezca con cada deploy.

---

## 📦 Pasos para Desplegar en Render

### 1. Hacer Commit y Push de los Cambios

```bash
git add .
git commit -m "Fix: Logo ahora se guarda en PostgreSQL para persistencia permanente"
git push origin main
```

### 2. Render Detectará y Desplegará Automáticamente

Render detectará el push y comenzará el proceso de build y deploy automáticamente.

### 3. Ejecutar la Migración de Base de Datos

**Opción A: Desde el Shell de Render (Recomendado)**

1. Ve a tu servicio en el Dashboard de Render
2. Click en "Shell" en el menú lateral
3. Ejecuta:
```bash
python migrate_logo_to_db.py
```

**Opción B: Migración Automática**

Agregar al archivo `render.yaml` (si lo usas):
```yaml
services:
  - type: web
    name: boletas-v1
    env: python
    buildCommand: "pip install -r requirements.txt && python migrate_logo_to_db.py"
    startCommand: "gunicorn app:app"
```

### 4. Subir el Logo Nuevamente

1. Accede a tu aplicación en la URL de Render
2. Inicia sesión
3. Ve a **Configuración** (`/config`)
4. Sube el logo de la empresa
5. Click en "Guardar Configuración"

**¡Listo!** El logo ahora está guardado en PostgreSQL y persistirá para siempre. ✅

---

## 🔍 Verificación

### Probar que el Logo Persiste:

1. ✅ Verifica que el logo aparezca en la página de configuración
2. ✅ Genera una boleta (mensual, aguinaldo o liquidación)
3. ✅ Verifica que el logo aparezca en el PDF generado
4. ✅ Haz un nuevo deploy manual o haz un cambio y push
5. ✅ Verifica que el logo **siga apareciendo** después del deploy

---

## 🚨 Si Hay Problemas

### Error al ejecutar la migración:
```
❌ Error: No module named 'psycopg2'
```
**Solución:** Asegúrate de que `psycopg2-binary` esté en `requirements.txt`

### Error de conexión a la base de datos:
```
❌ Error: connection to server failed
```
**Solución:** Verifica que la variable de entorno `DATABASE_URL` esté configurada en Render

### El logo no aparece después de subirlo:
1. Verifica que la migración se haya ejecutado correctamente
2. Revisa los logs de Render para ver si hay errores
3. Intenta subir el logo nuevamente

---

## 📝 Archivos Modificados

Los siguientes archivos fueron modificados para esta solución:

- ✅ `config/models.py` - Agregadas columnas `logo_data` y `logo_mimetype`
- ✅ `config/empresa_db.py` - Actualizado para manejar logo en BD
- ✅ `app.py` - Actualizado para guardar/servir logo desde BD
- ✅ `generators/pdf_generator.py` - Actualizado para usar logo desde BD
- ✅ `migrate_logo_to_db.py` - Script de migración (nuevo)
- ✅ `SOLUCION_LOGO_PERSISTENTE.md` - Documentación completa (nuevo)

---

## ⚙️ Variables de Entorno Requeridas

Asegúrate de tener configuradas estas variables en Render:

```
DATABASE_URL=postgresql://user:password@host:5432/database
SECRET_KEY=tu-clave-secreta-aqui
RENDER_DISK_PATH=/opt/render/project/data  # Opcional, pero recomendado
```

---

## 🎉 Beneficios de Esta Solución

- ✅ **Logo permanente** - No se borra con deploys
- ✅ **Sin archivos externos** - Todo en una base de datos
- ✅ **Backups incluidos** - El logo se respalda con la BD
- ✅ **Multi-instancia** - Funciona en arquitecturas escalables
- ✅ **Migración simple** - Un solo comando

---

## 📞 Soporte

Si encuentras algún problema:

1. Revisa los logs en Render Dashboard
2. Verifica que la migración se haya ejecutado
3. Comprueba las variables de entorno
4. Asegúrate de que PostgreSQL esté funcionando

---

**Última actualización:** Enero 2026  
**Versión:** 1.0 - Solución Logo Persistente
