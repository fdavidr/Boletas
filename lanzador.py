"""
BOLETAS-V1 - Lanzador de aplicación
Inicia el servidor Flask local y abre el navegador automáticamente.
Este archivo es el punto de entrada para el ejecutable PyInstaller.
"""

import sys
import os

# ── Determinar directorio base según entorno ──────────────────────────────
if getattr(sys, 'frozen', False):
    # Ejecutable PyInstaller (onedir): los recursos están en sys._MEIPASS
    _BASE_APP_DIR = sys._MEIPASS
else:
    _BASE_APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Pasar la ruta a app.py antes de importarlo
os.environ['BOLETAS_BASE_DIR'] = _BASE_APP_DIR

# ── Importaciones estándar ─────────────────────────────────────────────────
import threading
import time
import webbrowser
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk, messagebox

PORT = 5000
URL  = f'http://127.0.0.1:{PORT}'


# ─────────────────────────────────────────────────────────────────────────────
def _servidor_disponible(intentos: int = 40, espera: float = 0.5) -> bool:
    """Espera hasta que Flask responda en localhost o agota los intentos."""
    for _ in range(intentos):
        try:
            urllib.request.urlopen(URL + '/login', timeout=1)
            return True
        except Exception:
            time.sleep(espera)
    return False


def _iniciar_flask() -> None:
    """Arranca el servidor Flask en un hilo separado."""
    from app import app  # noqa: PLC0415 – importación tardía intencionada
    app.run(host='127.0.0.1', port=PORT, debug=False, use_reloader=False)


# ─────────────────────────────────────────────────────────────────────────────
class VentanaBoletas:
    """Ventana de estado pequeña que permite abrir y cerrar la aplicación."""

    COLOR_FONDO   = '#2c3e50'
    COLOR_BOTON   = '#3498db'
    COLOR_CERRAR  = '#e74c3c'
    COLOR_TEXTO   = '#ffffff'
    COLOR_SUBTXT  = '#bdc3c7'

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Boletas V1')
        self.root.geometry('400x200')
        self.root.resizable(False, False)
        self.root.configure(bg=self.COLOR_FONDO)
        self.root.protocol('WM_DELETE_WINDOW', self._confirmar_cierre)

        # Icono: buscar en sys._MEIPASS (_internal/) cuando está empaquetado
        _icon = os.path.join(_BASE_APP_DIR, 'boletas.ico')
        if not os.path.exists(_icon):
            # Fallback: junto al .exe (desarrollo o instalación manual)
            _icon = os.path.join(
                os.path.dirname(sys.executable) if getattr(sys, 'frozen', False)
                else _BASE_APP_DIR,
                'boletas.ico'
            )
        if os.path.exists(_icon):
            try:
                self.root.iconbitmap(_icon)
            except Exception:
                pass

        self._construir_ui()
        self._centrar()

    # ── UI ────────────────────────────────────────────────────────────────
    def _construir_ui(self):
        pad = dict(padx=20, pady=6)

        tk.Label(
            self.root, text='Boletas V1',
            font=('Segoe UI', 16, 'bold'),
            bg=self.COLOR_FONDO, fg=self.COLOR_TEXTO
        ).pack(pady=(20, 0))

        self.lbl_estado = tk.Label(
            self.root, text='Iniciando servidor…',
            font=('Segoe UI', 10),
            bg=self.COLOR_FONDO, fg=self.COLOR_SUBTXT
        )
        self.lbl_estado.pack(**pad)

        self.barra = ttk.Progressbar(
            self.root, mode='indeterminate', length=340
        )
        self.barra.pack(pady=4)
        self.barra.start(12)

        marco_btn = tk.Frame(self.root, bg=self.COLOR_FONDO)
        marco_btn.pack(pady=12)

        self.btn_abrir = tk.Button(
            marco_btn, text='🌐  Abrir Navegador',
            command=self._abrir_navegador,
            bg=self.COLOR_BOTON, fg=self.COLOR_TEXTO,
            font=('Segoe UI', 10), padx=12, pady=6,
            relief='flat', cursor='hand2', state='disabled',
            activebackground='#2980b9', activeforeground='white'
        )
        self.btn_abrir.pack(side='left', padx=6)

        self.btn_cerrar = tk.Button(
            marco_btn, text='✖  Cerrar',
            command=self._confirmar_cierre,
            bg=self.COLOR_CERRAR, fg=self.COLOR_TEXTO,
            font=('Segoe UI', 10), padx=12, pady=6,
            relief='flat', cursor='hand2',
            activebackground='#c0392b', activeforeground='white'
        )
        self.btn_cerrar.pack(side='left', padx=6)

    def _centrar(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f'{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}')

    # ── Acciones ──────────────────────────────────────────────────────────
    def marcar_listo(self):
        """Llamado desde hilo de espera cuando Flask ya respondió."""
        self.barra.stop()
        self.barra.config(mode='determinate', value=100)
        self.lbl_estado.config(
            text=f'✔  Servidor activo — {URL}',
            fg='#2ecc71'
        )
        self.btn_abrir.config(state='normal')

    def marcar_error(self):
        self.barra.stop()
        self.lbl_estado.config(
            text='⚠  No se pudo iniciar el servidor',
            fg='#e74c3c'
        )

    def _abrir_navegador(self):
        webbrowser.open(URL)

    def _confirmar_cierre(self):
        if messagebox.askyesno(
            'Cerrar Boletas V1',
            '¿Desea cerrar Boletas V1?\nSe detendrá el servidor local.',
            icon='question'
        ):
            self.root.destroy()
            os._exit(0)

    def run(self):
        self.root.mainloop()


# ─────────────────────────────────────────────────────────────────────────────
def main():
    # 1. Arrancar Flask en un hilo de fondo
    hilo_flask = threading.Thread(target=_iniciar_flask, daemon=True)
    hilo_flask.start()

    # 2. Crear ventana de estado
    ventana = VentanaBoletas()

    # 3. Esperar a Flask y abrir el navegador (en otro hilo para no bloquear Tk)
    def _esperar_y_abrir():
        if _servidor_disponible():
            ventana.root.after(0, ventana.marcar_listo)
            ventana.root.after(300, ventana._abrir_navegador)
        else:
            ventana.root.after(0, ventana.marcar_error)

    threading.Thread(target=_esperar_y_abrir, daemon=True).start()

    # 4. Mostrar ventana (bloquea hasta que el usuario cierre)
    ventana.run()


if __name__ == '__main__':
    main()
