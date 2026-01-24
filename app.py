"""
BOLETAS-V1 - Aplicación Web Flask
Sistema de Generación de Boletas de Pago
"""

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for, Response
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from datetime import datetime

# Importar base de datos
from config.database import db, init_db
from config.empresa_db import EmpresaConfig
from models.boleta_mensual import BoletaMensual
from models.boleta_aguinaldo import BoletaAguinaldo
from models.boleta_liquidacion import BoletaLiquidacion
from models.empleado_db import EmpleadoManager
from generators.pdf_generator import PDFGenerator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'boletas-v1-secret-key-2025'

# Configuración de carpetas - usar disco persistente en Render
DATA_DIR = os.environ.get('RENDER_DISK_PATH', 'data')
app.config['UPLOAD_FOLDER'] = os.path.join(DATA_DIR, 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(DATA_DIR, 'output')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

# Crear directorios necesarios
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)  # Para archivos estáticos locales
os.makedirs('output', exist_ok=True)  # Para desarrollo local

# Inicializar base de datos PostgreSQL
init_db(app)

# Configuración de empresa
empresa_config = EmpresaConfig()

# Gestor de empleados
empleado_manager = EmpleadoManager()

# Extensiones permitidas para logos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Credenciales de usuario (en producción usar base de datos)
USUARIO = "Santandera#25"
PASSWORD_HASH = generate_password_hash("Santandera#25")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """Decorador para rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET'])
def login():
    """Página de inicio de sesión"""
    if 'logged_in' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    """API para iniciar sesión"""
    try:
        data = request.json
        username = data.get('username', '')
        password = data.get('password', '')
        
        if username == USUARIO and check_password_hash(PASSWORD_HASH, password):
            session['logged_in'] = True
            session['username'] = username
            return jsonify({'success': True, 'message': 'Inicio de sesión exitoso'})
        else:
            return jsonify({'success': False, 'message': 'Usuario o contraseña incorrectos'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/config')
@login_required
def config():
    """Página de configuración"""
    return render_template('config.html')

@app.route('/mensual')
@login_required
def mensual():
    """Página de boleta mensual"""
    return render_template('mensual.html')

@app.route('/aguinaldo')
@login_required
def aguinaldo():
    """Página de boleta aguinaldo"""
    return render_template('aguinaldo.html')

@app.route('/liquidacion')
@login_required
def liquidacion():
    """Página de boleta liquidación"""
    return render_template('liquidacion.html')

@app.route('/empleados')
@login_required
def empleados():
    """Página de gestión de empleados"""
    return render_template('empleados.html')

# Ruta para servir el logo desde la base de datos
@app.route('/uploads/logo')
def serve_logo():
    """Sirve el logo desde la base de datos"""
    try:
        logo_data, logo_mimetype = empresa_config.get_logo_data()
        if logo_data:
            return Response(logo_data, mimetype=logo_mimetype or 'image/png')
        else:
            return jsonify({'error': 'Logo no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta para servir archivos del disco persistente (mantener por compatibilidad)
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Sirve archivos subidos desde el disco persistente"""
    # Si piden el logo, redirigir a la ruta correcta
    if filename.startswith('logo.'):
        return serve_logo()
    
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath)
        else:
            return jsonify({'error': 'Archivo no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API Endpoints

@app.route('/api/empresa', methods=['GET'])
@login_required
def get_empresa():
    """Obtiene los datos de la empresa"""
    empresa_data = empresa_config.get_empresa_data()
    
    # Verificar si existe logo en la base de datos
    logo_exists = empresa_config.logo_exists()
    empresa_data['logo_exists'] = logo_exists
    
    if logo_exists:
        # URL fija para el logo desde la base de datos
        empresa_data['logo_url'] = '/uploads/logo'
    else:
        empresa_data['logo_url'] = None
        empresa_data['logo_exists'] = False
    
    return jsonify(empresa_data)

@app.route('/api/empresa', methods=['POST'])
@login_required
def save_empresa():
    """Guarda los datos de la empresa"""
    try:
        data = request.form
        logo_path = empresa_config.get_logo_path()
        logo_data = None
        logo_mimetype = None
        
        # Si se subió un nuevo logo
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename and allowed_file(file.filename):
                # Leer el archivo como bytes para guardarlo en la BD
                logo_data = file.read()
                # Determinar el tipo MIME
                ext = file.filename.rsplit('.', 1)[1].lower()
                mime_types = {
                    'png': 'image/png',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'gif': 'image/gif'
                }
                logo_mimetype = mime_types.get(ext, 'image/png')
                
                # Actualizar logo_path para referencia (aunque ya no se usa para archivos)
                logo_path = f"database_logo.{ext}"
        
        empresa_config.set_empresa_data(
            nombre=data.get('nombre', ''),
            eslogan=data.get('eslogan', ''),
            contabilidad=data.get('contabilidad', ''),
            direccion=data.get('direccion', ''),
            telefono=data.get('telefono', ''),
            nit=data.get('nit', ''),
            actividad=data.get('actividad', ''),
            logo_path=logo_path,
            logo_data=logo_data,
            logo_mimetype=logo_mimetype
        )
        
        return jsonify({'success': True, 'message': 'Configuración guardada correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/boleta/mensual', methods=['POST'])
@login_required
def generar_boleta_mensual():
    """Genera una boleta de pago mensual"""
    try:
        data = request.json
        
        # Crear boleta
        boleta = BoletaMensual()
        boleta.nombre_completo = data.get('nombre_completo', '')
        boleta.ci = data.get('ci', '')
        boleta.cargo = data.get('cargo', '')
        boleta.mes_pago = data.get('mes_pago', '')
        boleta.anio = int(data.get('anio', datetime.now().year))
        boleta.rango_fechas = data.get('rango_fechas', '')
        
        # Ingresos
        boleta.haber_basico = float(data.get('haber_basico', 0))
        boleta.horas_extra = float(data.get('horas_extra', 0))
        boleta.bono_antiguedad = float(data.get('bono_antiguedad', 0))
        boleta.otros_ingresos = float(data.get('otros_ingresos', 0))
        
        # Egresos
        boleta.faltas = float(data.get('faltas', 0))
        boleta.retrasos = float(data.get('retrasos', 0))
        boleta.reposiciones = float(data.get('anticipos', data.get('reposiciones', 0)))
        boleta.otros_egresos = float(data.get('otros_egresos', 0))
        
        # Fecha, número y método de pago
        fecha_str = data.get('fecha_emision', datetime.now().strftime("%d/%m/%Y"))
        boleta.fecha_emision = datetime.strptime(fecha_str, "%d/%m/%Y")
        boleta.numero_boleta = empresa_config.get_next_numero_boleta()
        boleta.metodo_pago = data.get('metodo_pago', 'EFECTIVO')
        
        # Generar PDF
        pdf_gen = PDFGenerator(empresa_config, app.config['OUTPUT_FOLDER'])
        filename = pdf_gen.generar_boleta_mensual(boleta)
        
        return jsonify({
            'success': True,
            'message': 'Boleta generada correctamente',
            'filename': os.path.basename(filename),
            'numero_boleta': boleta.numero_boleta
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/boleta/aguinaldo', methods=['POST'])
@login_required
def generar_boleta_aguinaldo():
    """Genera una boleta de aguinaldo"""
    try:
        data = request.json
        
        # Crear boleta
        boleta = BoletaAguinaldo()
        boleta.nombre_completo = data.get('nombre_completo', '')
        boleta.ci = data.get('ci', '')
        boleta.cargo = data.get('cargo', '')
        boleta.anio = int(data.get('anio', datetime.now().year))
        boleta.fecha_ingreso = data.get('fecha_ingreso', '')
        boleta.fecha_inicio = data.get('fecha_inicio', '')
        boleta.fecha_fin = data.get('fecha_fin', '')
        boleta.promedio_ultimos_3_pagos = float(data.get('promedio_ultimos_3_pagos', 0))
        boleta.otros = float(data.get('otros', 0))
        
        # Fecha, número y método de pago
        fecha_str = data.get('fecha_emision', datetime.now().strftime("%d/%m/%Y"))
        boleta.fecha_emision = datetime.strptime(fecha_str, "%d/%m/%Y")
        boleta.numero_boleta = empresa_config.get_next_numero_boleta()
        boleta.metodo_pago = data.get('metodo_pago', 'EFECTIVO')
        
        # Generar PDF
        pdf_gen = PDFGenerator(empresa_config, app.config['OUTPUT_FOLDER'])
        filename = pdf_gen.generar_boleta_aguinaldo(boleta)
        
        return jsonify({
            'success': True,
            'message': 'Boleta generada correctamente',
            'filename': os.path.basename(filename),
            'numero_boleta': boleta.numero_boleta
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/boleta/liquidacion', methods=['POST'])
@login_required
def generar_boleta_liquidacion():
    """Genera una boleta de liquidación"""
    try:
        data = request.json
        
        # Crear boleta
        boleta = BoletaLiquidacion()
        boleta.nombre_completo = data.get('nombre_completo', '')
        boleta.ci = data.get('ci', '')
        boleta.domicilio_trabajador = data.get('domicilio_trabajador', '')
        boleta.cargo = data.get('cargo', '')
        boleta.fecha_ingreso = data.get('fecha_ingreso', '')
        boleta.fecha_retiro = data.get('fecha_retiro', '')
        
        # Remuneraciones
        boleta.ultimo_sueldo = float(data.get('ultimo_sueldo', 0))
        boleta.promedio_ultimos_3_sueldos = float(data.get('promedio_ultimos_3_sueldos', 0))
        
        # Beneficios
        boleta.indemnizacion = float(data.get('indemnizacion', 0))
        boleta.aguinaldo = float(data.get('aguinaldo', 0))
        boleta.vacaciones = float(data.get('vacaciones', 0))
        boleta.otros_beneficios = float(data.get('otros_beneficios', 0))
        
        # Deducciones
        boleta.anticipos = float(data.get('anticipos', 0))
        boleta.prestamos = float(data.get('prestamos', 0))
        boleta.otras_deducciones = float(data.get('otras_deducciones', 0))
        
        # Fecha, número y método de pago
        fecha_str = data.get('fecha_emision', datetime.now().strftime("%d/%m/%Y"))
        boleta.fecha_emision = datetime.strptime(fecha_str, "%d/%m/%Y")
        boleta.numero_boleta = empresa_config.get_next_numero_boleta()
        boleta.metodo_pago = data.get('metodo_pago', 'EFECTIVO')
        
        # Generar PDF
        pdf_gen = PDFGenerator(empresa_config, app.config['OUTPUT_FOLDER'])
        filename = pdf_gen.generar_boleta_liquidacion(boleta)
        
        return jsonify({
            'success': True,
            'message': 'Boleta generada correctamente',
            'filename': os.path.basename(filename),
            'numero_boleta': boleta.numero_boleta
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/download/<filename>')
@login_required
def download_pdf(filename):
    """Descarga un PDF generado"""
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'success': False, 'message': 'Archivo no encontrado'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# API Endpoints - Empleados

@app.route('/api/empleados', methods=['GET'])
@login_required
def get_empleados():
    """Obtiene todos los empleados"""
    try:
        empleados = empleado_manager.obtener_todos()
        return jsonify({'success': True, 'empleados': empleados})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/empleados', methods=['POST'])
@login_required
def agregar_empleado():
    """Agrega un nuevo empleado"""
    try:
        data = request.json
        
        empleado = empleado_manager.agregar_empleado(
            nombre_completo=data.get('nombre_completo', ''),
            ci=data.get('ci', ''),
            cargo=data.get('cargo', ''),
            fecha_ingreso=data.get('fecha_ingreso', ''),
            sueldo=data.get('sueldo', 0)
        )
        
        if empleado:
            return jsonify({
                'success': True,
                'message': 'Empleado agregado correctamente',
                'empleado': empleado
            })
        else:
            return jsonify({
                'success': False,
                'message': 'El empleado con ese CI ya existe'
            }), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/empleados/<int:id_empleado>', methods=['GET'])
@login_required
def get_empleado(id_empleado):
    """Obtiene un empleado por ID"""
    try:
        empleado = empleado_manager.obtener_empleado(id_empleado)
        if empleado:
            return jsonify({'success': True, 'empleado': empleado})
        return jsonify({'success': False, 'message': 'Empleado no encontrado'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/empleados/<int:id_empleado>', methods=['PUT'])
@login_required
def actualizar_empleado(id_empleado):
    """Actualiza un empleado"""
    try:
        data = request.json
        empleado = empleado_manager.actualizar_empleado(
            id_empleado,
            nombre_completo=data.get('nombre_completo', ''),
            ci=data.get('ci', ''),
            cargo=data.get('cargo', ''),
            fecha_ingreso=data.get('fecha_ingreso', ''),
            sueldo=data.get('sueldo', 0)
        )
        
        if empleado:
            return jsonify({
                'success': True,
                'message': 'Empleado actualizado correctamente',
                'empleado': empleado
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error al actualizar empleado o CI duplicado'
            }), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/empleados/<int:id_empleado>', methods=['DELETE'])
@login_required
def eliminar_empleado(id_empleado):
    """Elimina un empleado"""
    try:
        success = empleado_manager.eliminar_empleado(id_empleado)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Empleado eliminado correctamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Empleado no encontrado'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/empleados/buscar', methods=['GET'])
@login_required
def buscar_empleados():
    """Busca empleados por término"""
    try:
        termino = request.args.get('q', '')
        empleados = empleado_manager.buscar_empleados(termino)
        return jsonify({'success': True, 'empleados': empleados})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 60)
    print("🚀 BOLETAS-V1 - Sistema Web de Generación de Boletas")
    print("=" * 60)
    print(f"📍 Servidor iniciado en puerto: {port}")
    print("💡 Presiona CTRL+C para detener el servidor")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=port)
