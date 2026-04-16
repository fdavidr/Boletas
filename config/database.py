"""
Configuración de la base de datos SQLite local
Guarda los datos en el equipo donde está instalado el programa
"""

import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Ruta de la carpeta de datos local (relativa al directorio del proyecto)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def init_db(app):
    """Inicializa la base de datos SQLite local"""

    os.makedirs(DATA_DIR, exist_ok=True)
    database_url = f'sqlite:///{os.path.join(DATA_DIR, "boletas.db")}'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    db.init_app(app)
    
    with app.app_context():
        # Importar modelos primero para que estén registrados
        import config.models  # noqa: F401
        
        # Crear todas las tablas
        db.create_all()
        
        # Inicializar datos por defecto si es necesario
        from config.models import EmpresaConfig
        if EmpresaConfig.query.count() == 0:
            config_default = EmpresaConfig(
                nombre="Mi Empresa",
                eslogan="Excelencia en Servicios",
                contabilidad="001-2025",
                direccion="Av. Principal #123",
                telefono="591-2-1234567",
                nit="12345678",
                actividad="Servicios Generales",
                ultimo_numero_boleta=0,
                prefijo_boleta="BOL"
            )
            db.session.add(config_default)
            db.session.commit()
