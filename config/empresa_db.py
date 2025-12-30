"""
Módulo de configuración de empresa usando PostgreSQL
Maneja la carga y guardado de configuración de la empresa en base de datos
"""

import os
from config.database import db
from config.models import EmpresaConfig as EmpresaConfigModel

class EmpresaConfig:
    def __init__(self):
        """Inicializa el gestor de configuración de empresa"""
        pass
    
    def get_empresa_data(self):
        """Retorna los datos de la empresa desde la base de datos"""
        config = EmpresaConfigModel.query.first()
        if config:
            return config.to_dict()
        return self.get_default_config()
    
    def get_default_config(self):
        """Retorna configuración por defecto"""
        # Usar carpeta persistente para logos
        data_dir = os.environ.get('RENDER_DISK_PATH', 'data')
        logo_path = os.path.join(data_dir, 'uploads', 'logo.png')
        
        return {
            'nombre': 'Mi Empresa',
            'eslogan': 'Excelencia en Servicios',
            'contabilidad': '001-2025',
            'direccion': 'Av. Principal #123',
            'telefono': '591-2-1234567',
            'nit': '12345678',
            'actividad': 'Servicios Generales',
            'logo_path': logo_path
        }
    
    def set_empresa_data(self, nombre, eslogan, contabilidad, direccion, telefono, nit, actividad, logo_path):
        """Actualiza los datos de la empresa en la base de datos"""
        config = EmpresaConfigModel.query.first()
        
        if config:
            # Actualizar registro existente
            config.nombre = nombre
            config.eslogan = eslogan
            config.contabilidad = contabilidad
            config.direccion = direccion
            config.telefono = telefono
            config.nit = nit
            config.actividad = actividad
            config.logo_path = logo_path
        else:
            # Crear nuevo registro
            config = EmpresaConfigModel(
                nombre=nombre,
                eslogan=eslogan,
                contabilidad=contabilidad,
                direccion=direccion,
                telefono=telefono,
                nit=nit,
                actividad=actividad,
                logo_path=logo_path
            )
            db.session.add(config)
        
        db.session.commit()
    
    def get_next_numero_boleta(self):
        """Obtiene el siguiente número de boleta y lo incrementa"""
        config = EmpresaConfigModel.query.first()
        
        if not config:
            # Crear configuración por defecto si no existe
            config = EmpresaConfigModel(
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
            db.session.add(config)
        
        config.ultimo_numero_boleta += 1
        db.session.commit()
        
        return f"{config.prefijo_boleta}-{config.ultimo_numero_boleta:06d}"
    
    def get_logo_path(self):
        """Retorna la ruta del logo"""
        config = EmpresaConfigModel.query.first()
        if config and config.logo_path:
            return config.logo_path
        
        # Ruta por defecto
        data_dir = os.environ.get('RENDER_DISK_PATH', 'data')
        return os.path.join(data_dir, 'uploads', 'logo.png')
    
    def logo_exists(self):
        """Verifica si existe el archivo del logo"""
        logo_path = self.get_logo_path()
        return os.path.exists(logo_path)
