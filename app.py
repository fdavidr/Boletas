"""
BOLETAS-V1 - Aplicación Web Flask
Sistema de Generación de Boletas de Pago
"""

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for, Response
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import json
import base64
import io
import zipfile
from datetime import datetime

# Importar base de datos
from config.database import db, init_db
from config.empresa_db import EmpresaConfig
from config.models import UsuarioSistema
from models.boleta_mensual import BoletaMensual
from models.boleta_aguinaldo import BoletaAguinaldo
from models.boleta_liquidacion import BoletaLiquidacion
from models.empleado_db import EmpleadoManager
from generators.pdf_generator import PDFGenerator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'boletas-v1-secret-key-2025'

# Carpeta de datos local (dentro del directorio del proyecto)
from config.database import DATA_DIR
app.config['UPLOAD_FOLDER'] = os.path.join(DATA_DIR, 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(DATA_DIR, 'output')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max (para importar archivos)

# Crear directorios necesarios
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Inicializar base de datos PostgreSQL
init_db(app)

# Configuración de empresa
empresa_config = EmpresaConfig()

# Gestor de empleados
empleado_manager = EmpleadoManager()

# Extensiones permitidas para logos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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

@app.before_request
def check_first_time_setup():
    """Redirige a /setup si aún no se ha creado el usuario del sistema"""
    rutas_exentas = {'setup', 'api_setup', 'static'}
    if request.endpoint in rutas_exentas or request.endpoint is None:
        return None
    try:
        usuario = UsuarioSistema.query.first()
        if not usuario:
            return redirect(url_for('setup'))
    except Exception:
        return redirect(url_for('setup'))

# ── Configuración inicial ─────────────────────────────────────────────────
@app.route('/setup', methods=['GET'])
def setup():
    """Página de configuración inicial (primer uso)"""
    try:
        if UsuarioSistema.query.first():
            return redirect(url_for('login'))
    except Exception:
        pass
    return render_template('setup.html')

@app.route('/api/setup', methods=['POST'])
def api_setup():
    """Crea el usuario y preguntas de seguridad en el primer uso"""
    try:
        if UsuarioSistema.query.first():
            return jsonify({'success': False, 'message': 'El sistema ya fue configurado'}), 400

        data = request.json
        username  = data.get('username', '').strip()
        password  = data.get('password', '').strip()
        preguntas = data.get('preguntas', [])  # lista de {pregunta, respuesta}

        if not username or not password:
            return jsonify({'success': False, 'message': 'Usuario y contraseña son obligatorios'}), 400
        if len(preguntas) != 5:
            return jsonify({'success': False, 'message': 'Se requieren exactamente 5 preguntas'}), 400
        for p in preguntas:
            if not p.get('pregunta','').strip() or not p.get('respuesta','').strip():
                return jsonify({'success': False, 'message': 'Completa todas las preguntas y respuestas'}), 400

        nuevo = UsuarioSistema(
            username       = username,
            password_hash  = generate_password_hash(password),
            password_plain = password,
            pregunta_1     = preguntas[0]['pregunta'].strip(),
            respuesta_1    = preguntas[0]['respuesta'].strip().lower(),
            pregunta_2     = preguntas[1]['pregunta'].strip(),
            respuesta_2    = preguntas[1]['respuesta'].strip().lower(),
            pregunta_3     = preguntas[2]['pregunta'].strip(),
            respuesta_3    = preguntas[2]['respuesta'].strip().lower(),
            pregunta_4     = preguntas[3]['pregunta'].strip(),
            respuesta_4    = preguntas[3]['respuesta'].strip().lower(),
            pregunta_5     = preguntas[4]['pregunta'].strip(),
            respuesta_5    = preguntas[4]['respuesta'].strip().lower(),
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ── Login / Logout ─────────────────────────────────────────────────────────
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
        data     = request.json
        username = data.get('username', '')
        password = data.get('password', '')

        usuario = UsuarioSistema.query.first()
        if usuario and username == usuario.username and check_password_hash(usuario.password_hash, password):
            session['logged_in'] = True
            session['username']  = username
            return jsonify({'success': True, 'message': 'Inicio de sesión exitoso'})
        return jsonify({'success': False, 'message': 'Usuario o contraseña incorrectos'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    return redirect(url_for('login'))

# ── Recuperación de contraseña ─────────────────────────────────────────────
@app.route('/recuperar', methods=['GET'])
def recuperar():
    """Página de recuperación de contraseña"""
    return render_template('recuperar.html')

@app.route('/api/preguntas', methods=['GET'])
def api_preguntas():
    """Devuelve las 5 preguntas de seguridad (sin las respuestas)"""
    try:
        usuario = UsuarioSistema.query.first()
        if not usuario:
            return jsonify({'success': False}), 404
        return jsonify({'success': True, 'preguntas': [
            usuario.pregunta_1, usuario.pregunta_2, usuario.pregunta_3,
            usuario.pregunta_4, usuario.pregunta_5
        ]})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/recuperar', methods=['POST'])
def api_recuperar():
    """Verifica respuestas y devuelve credenciales si al menos 3 son correctas"""
    try:
        data      = request.json
        respuestas = data.get('respuestas', [])  # lista de 5 strings

        usuario = UsuarioSistema.query.first()
        if not usuario:
            return jsonify({'success': False}), 404

        correctas_db = [
            usuario.respuesta_1, usuario.respuesta_2, usuario.respuesta_3,
            usuario.respuesta_4, usuario.respuesta_5
        ]
        aciertos = sum(
            1 for db_r, user_r in zip(correctas_db, respuestas)
            if db_r.strip() == str(user_r).strip().lower()
        )
        if aciertos >= 3:
            return jsonify({'success': True, 'username': usuario.username,
                            'password': usuario.password_plain, 'aciertos': aciertos})
        return jsonify({'success': False, 'aciertos': aciertos,
                        'message': f'Solo {aciertos} de 5 respuestas correctas. Se necesitan al menos 3.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

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
        
        # Nota adicional (máx 300 chars por seguridad)
        boleta.nota = str(data.get('nota', ''))[:300]
        
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

# ── Exportar / Importar datos ──────────────────────────────────────────────────

@app.route('/api/exportar', methods=['GET'])
@login_required
def exportar_datos():
    """Exporta todos los datos (empresa + empleados) a un archivo JSON descargable"""
    try:
        from config.models import EmpresaConfig as EmpresaModel, Empleado as EmpleadoModel

        # Datos de empresa
        empresa = EmpresaModel.query.first()
        empresa_dict = {}
        if empresa:
            empresa_dict = {
                'nombre': empresa.nombre,
                'eslogan': empresa.eslogan,
                'contabilidad': empresa.contabilidad,
                'direccion': empresa.direccion,
                'telefono': empresa.telefono,
                'nit': empresa.nit,
                'actividad': empresa.actividad,
                'logo_path': empresa.logo_path,
                'ultimo_numero_boleta': empresa.ultimo_numero_boleta,
                'prefijo_boleta': empresa.prefijo_boleta,
                'logo_mimetype': empresa.logo_mimetype,
                # Logo como base64 para poder transferirlo
                'logo_data_b64': base64.b64encode(empresa.logo_data).decode('utf-8') if empresa.logo_data else None,
            }

        # Datos de empleados (todos, incluso inactivos, para respaldo completo)
        empleados = EmpleadoModel.query.all()
        empleados_list = []
        for emp in empleados:
            empleados_list.append({
                'id': emp.id,
                'nombre_completo': emp.nombre_completo,
                'ci': emp.ci,
                'cargo': emp.cargo,
                'fecha_ingreso': emp.fecha_ingreso,
                'sueldo': emp.sueldo,
                'activo': emp.activo,
            })

        exportacion = {
            'version': '1.0',
            'fecha_exportacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'empresa': empresa_dict,
            'empleados': empleados_list,
        }

        json_bytes = json.dumps(exportacion, ensure_ascii=False, indent=2).encode('utf-8')
        nombre_archivo = f"boletas_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        return send_file(
            io.BytesIO(json_bytes),
            mimetype='application/json',
            as_attachment=True,
            download_name=nombre_archivo
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/importar', methods=['POST'])
@login_required
def importar_datos():
    """Importa datos desde un archivo JSON exportado previamente"""
    try:
        if 'archivo' not in request.files:
            return jsonify({'success': False, 'message': 'No se recibió ningún archivo'}), 400

        archivo = request.files['archivo']
        if not archivo.filename or not archivo.filename.endswith('.json'):
            return jsonify({'success': False, 'message': 'El archivo debe ser un .json exportado por este programa'}), 400

        contenido = archivo.read()
        datos = json.loads(contenido.decode('utf-8'))

        if 'version' not in datos or 'empresa' not in datos or 'empleados' not in datos:
            return jsonify({'success': False, 'message': 'Archivo no válido o de versión incompatible'}), 400

        from config.models import EmpresaConfig as EmpresaModel, Empleado as EmpleadoModel
        from config.database import db

        # Restaurar empresa
        empresa_data = datos.get('empresa', {})
        if empresa_data:
            logo_data = None
            if empresa_data.get('logo_data_b64'):
                logo_data = base64.b64decode(empresa_data['logo_data_b64'])

            empresa = EmpresaModel.query.first()
            if empresa:
                empresa.nombre = empresa_data.get('nombre', empresa.nombre)
                empresa.eslogan = empresa_data.get('eslogan', empresa.eslogan)
                empresa.contabilidad = empresa_data.get('contabilidad', empresa.contabilidad)
                empresa.direccion = empresa_data.get('direccion', empresa.direccion)
                empresa.telefono = empresa_data.get('telefono', empresa.telefono)
                empresa.nit = empresa_data.get('nit', empresa.nit)
                empresa.actividad = empresa_data.get('actividad', empresa.actividad)
                empresa.logo_path = empresa_data.get('logo_path', empresa.logo_path)
                empresa.ultimo_numero_boleta = empresa_data.get('ultimo_numero_boleta', empresa.ultimo_numero_boleta)
                empresa.prefijo_boleta = empresa_data.get('prefijo_boleta', empresa.prefijo_boleta)
                if logo_data is not None:
                    empresa.logo_data = logo_data
                    empresa.logo_mimetype = empresa_data.get('logo_mimetype', 'image/png')
            else:
                empresa = EmpresaModel(
                    nombre=empresa_data.get('nombre', 'Mi Empresa'),
                    eslogan=empresa_data.get('eslogan', ''),
                    contabilidad=empresa_data.get('contabilidad', ''),
                    direccion=empresa_data.get('direccion', ''),
                    telefono=empresa_data.get('telefono', ''),
                    nit=empresa_data.get('nit', ''),
                    actividad=empresa_data.get('actividad', ''),
                    logo_path=empresa_data.get('logo_path', ''),
                    ultimo_numero_boleta=empresa_data.get('ultimo_numero_boleta', 0),
                    prefijo_boleta=empresa_data.get('prefijo_boleta', 'BOL'),
                    logo_data=logo_data,
                    logo_mimetype=empresa_data.get('logo_mimetype', 'image/png'),
                )
                db.session.add(empresa)

        # Restaurar empleados: actualizar existentes por CI, insertar nuevos
        empleados_importados = 0
        empleados_actualizados = 0
        for emp_data in datos.get('empleados', []):
            ci = emp_data.get('ci', '')
            existente = EmpleadoModel.query.filter_by(ci=ci).first()
            if existente:
                existente.nombre_completo = emp_data.get('nombre_completo', existente.nombre_completo)
                existente.cargo = emp_data.get('cargo', existente.cargo)
                existente.fecha_ingreso = emp_data.get('fecha_ingreso', existente.fecha_ingreso)
                existente.sueldo = float(emp_data.get('sueldo', existente.sueldo))
                existente.activo = emp_data.get('activo', existente.activo)
                empleados_actualizados += 1
            else:
                nuevo = EmpleadoModel(
                    nombre_completo=emp_data.get('nombre_completo', ''),
                    ci=ci,
                    cargo=emp_data.get('cargo', ''),
                    fecha_ingreso=emp_data.get('fecha_ingreso', ''),
                    sueldo=float(emp_data.get('sueldo', 0)),
                    activo=emp_data.get('activo', True),
                )
                db.session.add(nuevo)
                empleados_importados += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Importación completada: {empleados_importados} empleados nuevos, {empleados_actualizados} actualizados.',
        })
    except json.JSONDecodeError:
        return jsonify({'success': False, 'message': 'El archivo no es un JSON válido'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 60)
    print("🚀 BOLETAS-V1 - Sistema Web de Generación de Boletas")
    print("=" * 60)
    print(f"📍 Servidor iniciado en puerto: {port}")
    print("💡 Presiona CTRL+C para detener el servidor")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=port)
