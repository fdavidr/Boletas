"""
Modelo para boleta de aguinaldo
"""

from datetime import datetime

class BoletaAguinaldo:
    def __init__(self):
        self.nombre_completo = ""
        self.ci = ""
        self.cargo = ""
        self.anio = datetime.now().year
        self.fecha_inicio = ""  # Formato: dd/mm/yyyy
        self.fecha_fin = ""     # Formato: dd/mm/yyyy
        self.fecha_ingreso = ""
        self.promedio_ultimos_3_pagos = 0.0
        self.otros = 0.0
        
        # Número de boleta
        self.numero_boleta = ""
        self.fecha_emision = datetime.now()
        self.metodo_pago = "EFECTIVO"  # Por defecto EFECTIVO
    
    def calcular_liquido_pagable(self):
        """Calcula el líquido pagable"""
        return self.promedio_ultimos_3_pagos + self.otros
    
    def calcular_dias_trabajados(self):
        """Calcula los días trabajados entre fecha_inicio y fecha_fin"""
        try:
            if self.fecha_inicio and self.fecha_fin:
                inicio = datetime.strptime(self.fecha_inicio, "%d/%m/%Y")
                fin = datetime.strptime(self.fecha_fin, "%d/%m/%Y")
                dias = (fin - inicio).days + 1
                return dias
        except:
            return 0
        return 0
    
    def calcular_meses_trabajados(self):
        """Calcula aproximadamente los meses trabajados"""
        dias = self.calcular_dias_trabajados()
        return round(dias / 30, 1)
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "nombre_completo": self.nombre_completo,
            "ci": self.ci,
            "cargo": self.cargo,
            "anio": self.anio,
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
            "fecha_ingreso": self.fecha_ingreso,
            "promedio_ultimos_3_pagos": self.promedio_ultimos_3_pagos,
            "otros": self.otros,
            "liquido_pagable": self.calcular_liquido_pagable(),
            "dias_trabajados": self.calcular_dias_trabajados(),
            "meses_trabajados": self.calcular_meses_trabajados(),
            "numero_boleta": self.numero_boleta,
            "fecha_emision": self.fecha_emision.strftime("%d/%m/%Y"),
            "metodo_pago": self.metodo_pago
        }
