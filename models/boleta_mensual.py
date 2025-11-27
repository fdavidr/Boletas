"""
Modelo para boleta de pago mensual
"""

from datetime import datetime

class BoletaMensual:
    def __init__(self):
        self.nombre_completo = ""
        self.ci = ""
        self.cargo = ""
        self.mes_pago = ""
        self.anio = datetime.now().year
        self.rango_fechas = ""  # Opcional: "01/01/2025 al 31/01/2025"
        
        # Ingresos
        self.haber_basico = 0.0
        self.horas_extra = 0.0
        self.bono_antiguedad = 0.0
        self.otros_ingresos = 0.0
        
        # Egresos
        self.faltas = 0.0
        self.retrasos = 0.0
        self.reposiciones = 0.0
        self.otros_egresos = 0.0
        
        # Número de boleta
        self.numero_boleta = ""
        self.fecha_emision = datetime.now()
        self.metodo_pago = "EFECTIVO"  # Por defecto EFECTIVO
    
    def calcular_total_ingresos(self):
        """Calcula el total de ingresos"""
        return (self.haber_basico + self.horas_extra + 
                self.bono_antiguedad + self.otros_ingresos)
    
    def calcular_total_egresos(self):
        """Calcula el total de egresos"""
        return (self.faltas + self.retrasos + 
                self.reposiciones + self.otros_egresos)
    
    def calcular_liquido_pagable(self):
        """Calcula el líquido pagable"""
        return self.calcular_total_ingresos() - self.calcular_total_egresos()
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "nombre_completo": self.nombre_completo,
            "ci": self.ci,
            "cargo": self.cargo,
            "mes_pago": self.mes_pago,
            "anio": self.anio,
            "rango_fechas": self.rango_fechas,
            "haber_basico": self.haber_basico,
            "horas_extra": self.horas_extra,
            "bono_antiguedad": self.bono_antiguedad,
            "otros_ingresos": self.otros_ingresos,
            "faltas": self.faltas,
            "retrasos": self.retrasos,
            "reposiciones": self.reposiciones,
            "otros_egresos": self.otros_egresos,
            "total_ingresos": self.calcular_total_ingresos(),
            "total_egresos": self.calcular_total_egresos(),
            "liquido_pagable": self.calcular_liquido_pagable(),
            "numero_boleta": self.numero_boleta,
            "fecha_emision": self.fecha_emision.strftime("%d/%m/%Y"),
            "metodo_pago": self.metodo_pago
        }
