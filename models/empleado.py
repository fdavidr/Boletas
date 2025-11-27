"""
Modelo de Empleado
Gestiona los datos de los empleados registrados
"""

from datetime import datetime
import json
import os

class Empleado:
    """Clase para gestionar empleados"""
    
    def __init__(self, nombre_completo, ci, cargo, fecha_ingreso, sueldo, id_empleado=None):
        """
        Inicializa un empleado
        
        Args:
            nombre_completo: Nombre completo del empleado
            ci: Cédula de identidad
            cargo: Cargo del empleado
            fecha_ingreso: Fecha de ingreso (dd/mm/aaaa)
            sueldo: Sueldo actual
            id_empleado: ID único del empleado
        """
        self.id = id_empleado or self._generar_id()
        self.nombre_completo = nombre_completo
        self.ci = ci
        self.cargo = cargo
        self.fecha_ingreso = fecha_ingreso
        self.sueldo = float(sueldo)
    
    def _generar_id(self):
        """Genera un ID único basado en timestamp"""
        return int(datetime.now().timestamp() * 1000)
    
    def to_dict(self):
        """Convierte el empleado a diccionario"""
        return {
            'id': self.id,
            'nombre_completo': self.nombre_completo,
            'ci': self.ci,
            'cargo': self.cargo,
            'fecha_ingreso': self.fecha_ingreso,
            'sueldo': self.sueldo
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea un empleado desde un diccionario"""
        return cls(
            nombre_completo=data['nombre_completo'],
            ci=data['ci'],
            cargo=data['cargo'],
            fecha_ingreso=data['fecha_ingreso'],
            sueldo=data['sueldo'],
            id_empleado=data.get('id')
        )


class EmpleadoManager:
    """Gestor de empleados"""
    
    def __init__(self, archivo='config/empleados.json'):
        """
        Inicializa el gestor
        
        Args:
            archivo: Ruta del archivo JSON para almacenar empleados
        """
        self.archivo = archivo
        self._crear_directorio()
        self.empleados = self._cargar_empleados()
    
    def _crear_directorio(self):
        """Crea el directorio si no existe"""
        directorio = os.path.dirname(self.archivo)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)
    
    def _cargar_empleados(self):
        """Carga los empleados desde el archivo"""
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [Empleado.from_dict(emp) for emp in data]
            except Exception as e:
                print(f"Error al cargar empleados: {e}")
                return []
        return []
    
    def _guardar_empleados(self):
        """Guarda los empleados en el archivo"""
        try:
            with open(self.archivo, 'w', encoding='utf-8') as f:
                data = [emp.to_dict() for emp in self.empleados]
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar empleados: {e}")
            return False
    
    def agregar_empleado(self, empleado):
        """
        Agrega un nuevo empleado
        
        Args:
            empleado: Instancia de Empleado
            
        Returns:
            bool: True si se agregó correctamente
        """
        # Verificar si ya existe un empleado con el mismo CI
        if any(emp.ci == empleado.ci for emp in self.empleados):
            return False, "Ya existe un empleado con ese C.I."
        
        self.empleados.append(empleado)
        if self._guardar_empleados():
            return True, "Empleado registrado exitosamente"
        return False, "Error al guardar el empleado"
    
    def obtener_empleados(self):
        """
        Obtiene todos los empleados
        
        Returns:
            list: Lista de diccionarios con los datos de empleados
        """
        return [emp.to_dict() for emp in self.empleados]
    
    def obtener_empleado_por_id(self, id_empleado):
        """
        Obtiene un empleado por su ID
        
        Args:
            id_empleado: ID del empleado
            
        Returns:
            dict: Datos del empleado o None si no existe
        """
        for emp in self.empleados:
            if emp.id == id_empleado:
                return emp.to_dict()
        return None
    
    def obtener_empleado_por_ci(self, ci):
        """
        Obtiene un empleado por su CI
        
        Args:
            ci: Cédula de identidad
            
        Returns:
            dict: Datos del empleado o None si no existe
        """
        for emp in self.empleados:
            if emp.ci == ci:
                return emp.to_dict()
        return None
    
    def actualizar_empleado(self, id_empleado, datos):
        """
        Actualiza los datos de un empleado
        
        Args:
            id_empleado: ID del empleado
            datos: Diccionario con los nuevos datos
            
        Returns:
            tuple: (success, message)
        """
        for i, emp in enumerate(self.empleados):
            if emp.id == id_empleado:
                # Verificar si el CI cambió y ya existe
                if datos.get('ci') != emp.ci:
                    if any(e.ci == datos.get('ci') for e in self.empleados if e.id != id_empleado):
                        return False, "Ya existe un empleado con ese C.I."
                
                # Actualizar datos
                self.empleados[i] = Empleado(
                    nombre_completo=datos.get('nombre_completo', emp.nombre_completo),
                    ci=datos.get('ci', emp.ci),
                    cargo=datos.get('cargo', emp.cargo),
                    fecha_ingreso=datos.get('fecha_ingreso', emp.fecha_ingreso),
                    sueldo=datos.get('sueldo', emp.sueldo),
                    id_empleado=id_empleado
                )
                
                if self._guardar_empleados():
                    return True, "Empleado actualizado exitosamente"
                return False, "Error al guardar los cambios"
        
        return False, "Empleado no encontrado"
    
    def eliminar_empleado(self, id_empleado):
        """
        Elimina un empleado
        
        Args:
            id_empleado: ID del empleado
            
        Returns:
            tuple: (success, message)
        """
        for i, emp in enumerate(self.empleados):
            if emp.id == id_empleado:
                self.empleados.pop(i)
                if self._guardar_empleados():
                    return True, "Empleado eliminado exitosamente"
                return False, "Error al eliminar el empleado"
        
        return False, "Empleado no encontrado"
    
    def buscar_empleados(self, termino):
        """
        Busca empleados por nombre o CI
        
        Args:
            termino: Término de búsqueda
            
        Returns:
            list: Lista de empleados que coinciden
        """
        termino = termino.lower()
        resultados = []
        
        for emp in self.empleados:
            if (termino in emp.nombre_completo.lower() or 
                termino in emp.ci.lower()):
                resultados.append(emp.to_dict())
        
        return resultados
