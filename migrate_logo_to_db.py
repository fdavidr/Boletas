"""
Script de migración para agregar columnas de logo a la base de datos
Ejecutar este script UNA VEZ después de desplegar los cambios
"""

import os
import sys

# Agregar el directorio raíz al path para importar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config.database import db, init_db
from config.models import EmpresaConfig
from sqlalchemy import text

def migrate_logo_columns():
    """Agrega las columnas logo_data y logo_mimetype a la tabla empresa_config"""
    
    app = Flask(__name__)
    init_db(app)
    
    with app.app_context():
        try:
            # Verificar si las columnas ya existen
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('empresa_config')]
            
            if 'logo_data' not in columns:
                print("Agregando columna 'logo_data'...")
                db.session.execute(text('ALTER TABLE empresa_config ADD COLUMN logo_data BYTEA'))
                print("✓ Columna 'logo_data' agregada")
            else:
                print("✓ Columna 'logo_data' ya existe")
            
            if 'logo_mimetype' not in columns:
                print("Agregando columna 'logo_mimetype'...")
                db.session.execute(text('ALTER TABLE empresa_config ADD COLUMN logo_mimetype VARCHAR(50)'))
                print("✓ Columna 'logo_mimetype' agregada")
            else:
                print("✓ Columna 'logo_mimetype' ya existe")
            
            db.session.commit()
            print("\n✅ Migración completada exitosamente")
            print("\nAhora puedes volver a subir tu logo y se guardará permanentemente en la base de datos.")
            
        except Exception as e:
            print(f"\n❌ Error durante la migración: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("MIGRACIÓN: Agregar soporte de logo en base de datos")
    print("=" * 60)
    print()
    
    success = migrate_logo_columns()
    
    if success:
        print("\n" + "=" * 60)
        print("SIGUIENTE PASO:")
        print("1. Vuelve a la aplicación")
        print("2. Ve a Configuración")
        print("3. Sube el logo nuevamente")
        print("4. ¡El logo ahora se guardará permanentemente!")
        print("=" * 60)
    else:
        print("\nPor favor, revisa los errores y vuelve a intentar.")
        sys.exit(1)
