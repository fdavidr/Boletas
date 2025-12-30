"""
Modelos de base de datos
Define las tablas y relaciones de la base de datos
"""

from config.database import db
from datetime import datetime

class EmpresaConfig(db.Model):
    """Configuración de la empresa"""
    __tablename__ = 'empresa_config'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    eslogan = db.Column(db.String(200))
    contabilidad = db.Column(db.String(100))
    direccion = db.Column(db.String(300))
    telefono = db.Column(db.String(50))
    nit = db.Column(db.String(50))
    actividad = db.Column(db.String(200))
    logo_path = db.Column(db.String(500))
    ultimo_numero_boleta = db.Column(db.Integer, default=0)
    prefijo_boleta = db.Column(db.String(20), default='BOL')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            'nombre': self.nombre,
            'eslogan': self.eslogan,
            'contabilidad': self.contabilidad,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'nit': self.nit,
            'actividad': self.actividad,
            'logo_path': self.logo_path
        }


class Empleado(db.Model):
    """Modelo de empleado"""
    __tablename__ = 'empleados'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(200), nullable=False)
    ci = db.Column(db.String(50), nullable=False, unique=True)
    cargo = db.Column(db.String(100), nullable=False)
    fecha_ingreso = db.Column(db.String(20), nullable=False)
    sueldo = db.Column(db.Float, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'nombre_completo': self.nombre_completo,
            'ci': self.ci,
            'cargo': self.cargo,
            'fecha_ingreso': self.fecha_ingreso,
            'sueldo': self.sueldo,
            'activo': self.activo
        }
    
    @staticmethod
    def from_dict(data):
        """Crea un empleado desde un diccionario"""
        return Empleado(
            nombre_completo=data['nombre_completo'],
            ci=data['ci'],
            cargo=data['cargo'],
            fecha_ingreso=data['fecha_ingreso'],
            sueldo=float(data['sueldo'])
        )
