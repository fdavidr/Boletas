"""
Módulo de configuración de empresa
Maneja la carga y guardado de configuración de la empresa
"""

import json
import os
from datetime import datetime

class EmpresaConfig:
    def __init__(self, config_file="config/settings.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Carga la configuración desde el archivo JSON"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self.get_default_config()
    
    def get_default_config(self):
        """Retorna configuración por defecto"""
        return {
            "empresa": {
                "nombre": "Mi Empresa",
                "eslogan": "Excelencia en Servicios",
                "contabilidad": "001-2025",
                "direccion": "Av. Principal #123",
                "telefono": "591-2-1234567",
                "nit": "12345678",
                "actividad": "Servicios Generales",
                "logo_path": "static/uploads/logo.png"
            },
            "boletas": {
                "ultimo_numero": 0,
                "prefijo": "BOL"
            }
        }
    
    def save_config(self):
        """Guarda la configuración en el archivo JSON"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
    
    def get_empresa_data(self):
        """Retorna los datos de la empresa"""
        return self.config.get("empresa", {})
    
    def set_empresa_data(self, nombre, eslogan, contabilidad, direccion, telefono, nit, actividad, logo_path):
        """Actualiza los datos de la empresa"""
        self.config["empresa"] = {
            "nombre": nombre,
            "eslogan": eslogan,
            "contabilidad": contabilidad,
            "direccion": direccion,
            "telefono": telefono,
            "nit": nit,
            "actividad": actividad,
            "logo_path": logo_path
        }
        self.save_config()
    
    def get_next_numero_boleta(self):
        """Obtiene el siguiente número de boleta y lo incrementa"""
        numero = self.config["boletas"]["ultimo_numero"] + 1
        self.config["boletas"]["ultimo_numero"] = numero
        self.save_config()
        prefijo = self.config["boletas"]["prefijo"]
        return f"{prefijo}-{numero:06d}"
    
    def get_logo_path(self):
        """Retorna la ruta del logo"""
        return self.config["empresa"].get("logo_path", "static/uploads/logo.png")
    
    def logo_exists(self):
        """Verifica si existe el archivo del logo"""
        logo_path = self.get_logo_path()
        return os.path.exists(logo_path)
