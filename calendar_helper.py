# =============================================================
#  GREENPLAST - Módulo de cola de eventos de Google Calendar
#
#  Las mantenciones registradas se agregan a un archivo JSON
#  de cola. Una tarea programada de Cowork procesa esa cola
#  y crea los eventos en Google Calendar automáticamente,
#  usando el MCP de calendario ya autenticado.
#  Sin Google Cloud, sin credenciales, sin acción del usuario.
# =============================================================

import os
import json
from datetime import datetime

# Ruta del archivo de cola (en la carpeta compartida)
QUEUE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "cola_calendario.json"
)


def is_calendar_configured() -> bool:
    return True


def queue_calendar_event(data: dict, record_id: int) -> bool:
    """
    Agrega el evento a la cola JSON para que la tarea
    programada de Cowork lo procese automáticamente.
    Retorna True si se agregó con éxito.
    """
    queue_path = os.path.abspath(QUEUE_PATH)

    # Leer cola existente
    if os.path.exists(queue_path):
        try:
            with open(queue_path, "r", encoding="utf-8") as f:
                queue = json.load(f)
        except (json.JSONDecodeError, IOError):
            queue = []
    else:
        queue = []

    # Agregar nuevo evento
    entry = {
        "id":           record_id,
        "fecha":        data.get("fecha", ""),
        "hora":         data.get("hora", "08:00"),
        "maquina":      data.get("maquina", ""),
        "tipo":         data.get("tipo", ""),
        "motivo":       data.get("motivo", ""),
        "descripcion":  data.get("descripcion", ""),
        "tecnico":      data.get("tecnico", ""),
        "duracion":     data.get("duracion", "1"),
        "observaciones": data.get("observaciones", ""),
        "processed":    False,
        "queued_at":    datetime.now().isoformat(),
    }
    queue.append(entry)

    try:
        with open(queue_path, "w", encoding="utf-8") as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"[Calendar Queue] Error escribiendo cola: {e}")
        return False


# Alias para app.py
def generate_calendar_url(data: dict) -> str:
    return ""
