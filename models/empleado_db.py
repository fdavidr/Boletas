"""
Modelo de Empleado usando PostgreSQL
Gestiona los datos de los empleados en base de datos
"""

from config.database import db

class EmpleadoManager:
    """Gestor de empleados usando PostgreSQL"""
    
    def __init__(self):
        """Inicializa el gestor"""
        pass
    
    def agregar_empleado(self, nombre_completo, ci, cargo, fecha_ingreso, sueldo):
        """
        Agrega un nuevo empleado a la base de datos
        
        Returns:
            dict: Empleado creado o None si hay error
        """
        from config.models import Empleado as EmpleadoDB
        try:
            # Verificar si ya existe un empleado con ese CI
            existe = EmpleadoDB.query.filter_by(ci=ci).first()
            if existe:
                return None
            
            empleado = EmpleadoDB(
                nombre_completo=nombre_completo,
                ci=ci,
                cargo=cargo,
                fecha_ingreso=fecha_ingreso,
                sueldo=float(sueldo)
            )
            db.session.add(empleado)
            db.session.commit()
            return empleado.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"Error al agregar empleado: {e}")
            return None
    
    def obtener_empleado(self, id_empleado):
        """
        Obtiene un empleado por su ID
        
        Args:
            id_empleado: ID del empleado
            
        Returns:
            dict: Datos del empleado o None si no existe
        """
        from config.models import Empleado as EmpleadoDB
        empleado = EmpleadoDB.query.get(id_empleado)
        return empleado.to_dict() if empleado else None
    
    def obtener_todos(self):
        """
        Obtiene todos los empleados activos
        
        Returns:
            list: Lista de empleados
        """
        from config.models import Empleado as EmpleadoDB
        empleados = EmpleadoDB.query.filter_by(activo=True).all()
        return [emp.to_dict() for emp in empleados]
    
    def actualizar_empleado(self, id_empleado, nombre_completo, ci, cargo, fecha_ingreso, sueldo):
        """
        Actualiza un empleado existente
        
        Returns:
            dict: Empleado actualizado o None si hay error
        """
        from config.models import Empleado as EmpleadoDB
        try:
            empleado = EmpleadoDB.query.get(id_empleado)
            if not empleado:
                return None
            
            # Verificar si el nuevo CI ya existe en otro empleado
            if ci != empleado.ci:
                existe = EmpleadoDB.query.filter_by(ci=ci).first()
                if existe:
                    return None
            
            empleado.nombre_completo = nombre_completo
            empleado.ci = ci
            empleado.cargo = cargo
            empleado.fecha_ingreso = fecha_ingreso
            empleado.sueldo = float(sueldo)
            
            db.session.commit()
            return empleado.to_dict()
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar empleado: {e}")
            return None
    
    def eliminar_empleado(self, id_empleado):
        """
        Marca un empleado como inactivo (eliminación lógica)
        
        Returns:
            bool: True si se eliminó correctamente, False si no
        """
        from config.models import Empleado as EmpleadoDB
        try:
            empleado = EmpleadoDB.query.get(id_empleado)
            if not empleado:
                return False
            
            empleado.activo = False
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al eliminar empleado: {e}")
            return False
    
    def buscar_empleados(self, termino):
        """
        Busca empleados por nombre o CI
        
        Args:
            termino: Término de búsqueda
            
        Returns:
            list: Lista de empleados que coinciden
        """
        from config.models import Empleado as EmpleadoDB
        termino_lower = f"%{termino.lower()}%"
        empleados = EmpleadoDB.query.filter(
            db.and_(
                EmpleadoDB.activo == True,
                db.or_(
                    EmpleadoDB.nombre_completo.ilike(termino_lower),
                    EmpleadoDB.ci.ilike(termino_lower),
                    EmpleadoDB.cargo.ilike(termino_lower)
                )
            )
        ).all()
        return [emp.to_dict() for emp in empleados]
    
    def obtener_por_ci(self, ci):
        """
        Obtiene un empleado por su CI
        
        Args:
            ci: Cédula de identidad
            
        Returns:
            dict: Datos del empleado o None si no existe
        """
        from config.models import Empleado as EmpleadoDB
        empleado = EmpleadoDB.query.filter_by(ci=ci, activo=True).first()
        return empleado.to_dict() if empleado else None


# Mantener compatibilidad con el modelo anterior
class Empleado:
    """Clase de compatibilidad con el modelo anterior"""
    
    @staticmethod
    def from_dict(data):
        """Crea un empleado desde un diccionario"""
        return {
            'id': data.get('id'),
            'nombre_completo': data['nombre_completo'],
            'ci': data['ci'],
            'cargo': data['cargo'],
            'fecha_ingreso': data['fecha_ingreso'],
            'sueldo': float(data['sueldo'])
        }
    
    @staticmethod
    def to_dict(empleado):
        """Convierte un empleado a diccionario"""
        return empleado
