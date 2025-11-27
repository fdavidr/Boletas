# 🚀 INICIO RÁPIDO - BOLETAS-V1

## Instalación en 3 pasos:

### 1️⃣ Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 2️⃣ (Opcional) Crear logo de ejemplo
```powershell
python crear_logo.py
```

### 3️⃣ Iniciar la aplicación
```powershell
python app.py
```

## 🌐 Abrir en el navegador

Vaya a: **http://localhost:5000**

## ✅ Primeros pasos

1. **Configure su empresa**:
   - Clic en "⚙️ Configuración"
   - Complete nombre, eslogan, número contable
   - Suba su logo (opcional)
   - Guardar

2. **Genere su primera boleta**:
   - Clic en "📄 Boleta Mensual"
   - Complete los datos
   - Los cálculos son automáticos
   - Clic en "Generar PDF"

## 📂 Archivos importantes

- **PDFs generados**: carpeta `output/`
- **Configuración**: `config/settings.json`
- **Logo**: `static/uploads/logo.png`

## ❗ Problemas comunes

**La app no inicia:**
```powershell
python --version  # Debe ser 3.8 o superior
pip install -r requirements.txt
```

**No genera PDF:**
- Configure primero los datos de empresa
- Verifique que exista la carpeta `output/`

**Sin logo:**
```powershell
python crear_logo.py
```

## 📱 Características

✅ Boletas mensuales con cálculo automático
✅ Aguinaldo con validación de 90 días mínimo
✅ Liquidación con beneficios sociales
✅ PDFs profesionales con logo
✅ Numeración automática
✅ Interfaz responsive

---

**¡Listo para usar!** 🎉
