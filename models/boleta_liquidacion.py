"""
Modelo para boleta de liquidación
"""

from datetime import datetime

class BoletaLiquidacion:
    def __init__(self):
        # Datos generales del trabajador
        self.nombre_completo = ""
        self.ci = ""
        self.domicilio_trabajador = ""
        self.cargo = ""
        
        # Fechas
        self.fecha_ingreso = ""  # dd/mm/yyyy
        self.fecha_retiro = ""   # dd/mm/yyyy
        
        # Remuneraciones
        self.promedio_ultimos_3_sueldos = 0.0
        self.ultimo_sueldo = 0.0
        
        # Beneficios sociales
        self.indemnizacion = 0.0
        self.aguinaldo = 0.0
        self.vacaciones = 0.0
        self.otros_beneficios = 0.0
        
        # Deducciones
        self.anticipos = 0.0
        self.prestamos = 0.0
        self.otras_deducciones = 0.0
        
        # Número de boleta
        self.numero_boleta = ""
        self.fecha_emision = datetime.now()
        self.metodo_pago = "EFECTIVO"  # Por defecto EFECTIVO
    
    def calcular_tiempo_servicio(self):
        """Calcula años, meses y días de servicio"""
        try:
            if self.fecha_ingreso and self.fecha_retiro:
                ingreso = datetime.strptime(self.fecha_ingreso, "%d/%m/%Y")
                retiro = datetime.strptime(self.fecha_retiro, "%d/%m/%Y")
                
                dias_total = (retiro - ingreso).days
                anios = dias_total // 365
                dias_restantes = dias_total % 365
                meses = dias_restantes // 30
                dias = dias_restantes % 30
                
                return {
                    "anios": anios,
                    "meses": meses,
                    "dias": dias,
                    "total_dias": dias_total
                }
        except:
            return {"anios": 0, "meses": 0, "dias": 0, "total_dias": 0}
        return {"anios": 0, "meses": 0, "dias": 0, "total_dias": 0}
    
    def calcular_total_beneficios(self):
        """Calcula el total de beneficios sociales"""
        return (self.indemnizacion + self.aguinaldo + 
                self.vacaciones + self.otros_beneficios)
    
    def calcular_total_deducciones(self):
        """Calcula el total de deducciones"""
        return (self.anticipos + self.prestamos + self.otras_deducciones)
    
    def calcular_liquido_pagable(self):
        """Calcula el líquido pagable final"""
        return self.calcular_total_beneficios() - self.calcular_total_deducciones()
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        tiempo_servicio = self.calcular_tiempo_servicio()
        return {
            "nombre_completo": self.nombre_completo,
            "ci": self.ci,
            "domicilio_trabajador": self.domicilio_trabajador,
            "cargo": self.cargo,
            "fecha_ingreso": self.fecha_ingreso,
            "fecha_retiro": self.fecha_retiro,
            "tiempo_servicio": tiempo_servicio,
            "promedio_ultimos_3_sueldos": self.promedio_ultimos_3_sueldos,
            "ultimo_sueldo": self.ultimo_sueldo,
            "indemnizacion": self.indemnizacion,
            "aguinaldo": self.aguinaldo,
            "vacaciones": self.vacaciones,
            "otros_beneficios": self.otros_beneficios,
            "total_beneficios": self.calcular_total_beneficios(),
            "anticipos": self.anticipos,
            "prestamos": self.prestamos,
            "otras_deducciones": self.otras_deducciones,
            "total_deducciones": self.calcular_total_deducciones(),
            "liquido_pagable": self.calcular_liquido_pagable(),
            "numero_boleta": self.numero_boleta,
            "fecha_emision": self.fecha_emision.strftime("%d/%m/%Y"),
            "metodo_pago": self.metodo_pago
        }
