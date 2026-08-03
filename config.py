# =============================================================
#  GREENPLAST - Configuración de la App de Mantenciones
#  Edita este archivo para agregar máquinas, técnicos, etc.
# =============================================================

# Lista de máquinas de la planta
MACHINES = [
    "Triturador Weima",
    "Triturador Zerma II",
    "Triturador Zerma III",
    "Molino Seco Herbold",
    "Línea Lavado Tecnofer 1400",
    "Línea Lavado Herbold",
    "Extrusora Starlinger",
    "Extursora Erema",
    "Extrusora NGR",
    "Silo I",
    "Silo II",
    "Planta Tratamiento RILes",
    "Chiller",
    "Torre de Enfriamiento",
    "Tablero Eléctrico Principal",
    "Generador",
    "Otro / Instalaciones Generales",
]

# Lista de técnicos del equipo de mantención
TECHNICIANS = [
    "Edgar Heredia",
    "Diego Navarro",
    "Guillermo Ortega",
    "Oswaldo Alvarez",
    "Cristobal Retamales",
    "Externo / Contratista",
]

# Tipos de mantención
MAINTENANCE_TYPES = [
    "Programada",
    "No Programada",
]

# Motivos frecuentes (sugerencias rápidas)
COMMON_REASONS = [
    "Cambio de cuchillas / piezas de desgaste",
    "Cambio de Cuchillos",
    "Cambio de aceite y lubricación",
    "Revisión y ajuste de correas",
    "Limpieza general de componentes",
    "Reemplazo de rodamientos",
    "Revisión eléctrica",
    "Falla mecánica inesperada",
    "Falla eléctrica inesperada",
    "Calibración y ajustes",
    "Revisión de sistema hidráulico",
    "Otro (especificar en descripción)",
]

# ---------------------------------------------------------------
# RUTA DEL ARCHIVO EXCEL MAESTRO
# Asegúrate de que esta ruta apunte a la carpeta compartida.
# ---------------------------------------------------------------
import os
EXCEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "Planilla_Maestro_Mantenciones.xlsx"
)

# ---------------------------------------------------------------
# GOOGLE CALENDAR
# Pon aquí el ID del calendario compartido del equipo.
# Para obtenerlo: en Google Calendar → Configuración del
# calendario → "Dirección del calendario" → copiar el ID
# (termina en @group.calendar.google.com o similar)
# Si usas el calendario principal, deja "primary"
# ---------------------------------------------------------------
CALENDAR_ID = "c_6ae46b3fb892d7ffcb40a7a4617358724bb89ba8ac1e30eee047be2888690d6e@group.calendar.google.com"

# Zona horaria de la planta
TIMEZONE = "America/Santiago"

# Puerto del servidor web local
APP_PORT = 5001

# Clave secreta de la app (puedes cambiarla)
SECRET_KEY = "greenplast_mantenciones_2024_clave_segura"
