"""
Modelo para boleta de aguinaldo
"""

from datetime import datetime, timedelta

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
    
    def calcular_meses_completos_y_dias(self):
        """
        Calcula los meses completos y días adicionales trabajados.
        Retorna: (meses_completos, dias_adicionales)
        
        Ejemplo:
        - 20-ene a 15-abr: 2 meses completos (feb, mar) + 26 días (11 de ene + 15 de abr)
        """
        try:
            if not self.fecha_inicio or not self.fecha_fin:
                return (0, 0)
            
            inicio = datetime.strptime(self.fecha_inicio, "%d/%m/%Y")
            fin = datetime.strptime(self.fecha_fin, "%d/%m/%Y")
            
            # Calcular diferencia de años y meses
            anios_diff = fin.year - inicio.year
            meses_diff = fin.month - inicio.month
            
            # Total de meses entre las fechas
            total_meses = anios_diff * 12 + meses_diff
            
            # Determinar meses completos y días adicionales
            meses_completos = 0
            dias_adicionales = 0
            
            # Si inicio es día 1 y fin es el último día del mes
            if inicio.day == 1:
                # Verificar si el último mes está completo
                ultimo_dia_mes_fin = (datetime(fin.year, fin.month % 12 + 1, 1) if fin.month < 12 
                                     else datetime(fin.year + 1, 1, 1)) - timedelta(days=1)
                
                if fin.day == ultimo_dia_mes_fin.day:
                    # Todos los meses son completos
                    meses_completos = total_meses + 1
                else:
                    # Último mes es parcial
                    meses_completos = total_meses
                    dias_adicionales = fin.day
            else:
                # Mes inicial es parcial
                # Calcular días del mes inicial
                ultimo_dia_mes_inicio = (datetime(inicio.year, inicio.month % 12 + 1, 1) if inicio.month < 12 
                                         else datetime(inicio.year + 1, 1, 1)) - timedelta(days=1)
                dias_mes_inicial = (ultimo_dia_mes_inicio - inicio).days + 1
                
                # Verificar si el último mes está completo
                if total_meses > 0:
                    # Hay meses intermedios
                    ultimo_dia_mes_fin = (datetime(fin.year, fin.month % 12 + 1, 1) if fin.month < 12 
                                         else datetime(fin.year + 1, 1, 1)) - timedelta(days=1)
                    
                    if fin.day == ultimo_dia_mes_fin.day:
                        # Último mes completo
                        meses_completos = total_meses
                        dias_adicionales = dias_mes_inicial
                    else:
                        # Último mes parcial
                        meses_completos = total_meses - 1 if total_meses > 0 else 0
                        dias_adicionales = dias_mes_inicial + fin.day
                else:
                    # Todo en el mismo mes
                    dias_adicionales = (fin - inicio).days + 1
            
            return (meses_completos, dias_adicionales)
        except Exception as e:
            print(f"Error calculando meses y días: {e}")
            return (0, 0)
    
    def calcular_aguinaldo_proporcional(self):
        """
        Calcula el aguinaldo según las reglas:
        1. Si trabajó 12 meses completos: aguinaldo = sueldo promedio
        2. Si trabajó meses completos: aguinaldo = (sueldo promedio / 12) × meses
        3. Si trabajó meses + días: aguinaldo = (sueldo/12)×meses + (sueldo/360)×días
        """
        meses_completos, dias_adicionales = self.calcular_meses_completos_y_dias()
        
        # Caso 1: 12 meses completos
        if meses_completos == 12 and dias_adicionales == 0:
            return self.promedio_ultimos_3_pagos
        
        # Caso 2 y 3: Proporcional
        aguinaldo_por_meses = (self.promedio_ultimos_3_pagos / 12) * meses_completos
        aguinaldo_por_dias = (self.promedio_ultimos_3_pagos / 360) * dias_adicionales
        
        return aguinaldo_por_meses + aguinaldo_por_dias
    
    def calcular_liquido_pagable(self):
        """Calcula el líquido pagable total (aguinaldo proporcional + otros)"""
        return self.calcular_aguinaldo_proporcional() + self.otros
    
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
