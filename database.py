# =============================================================
#  GREENPLAST - Base de datos SQLite
#  Almacenamiento primario para despliegue en la nube.
#  El Excel se genera bajo demanda como descarga.
# =============================================================

import sqlite3
import os
from datetime import datetime

# En Railway la BD queda en el volumen persistente; localmente, en la misma carpeta
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "mantenciones.db"
))


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crea la tabla si no existe."""
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mantenciones (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_registro   TEXT,
                fecha            TEXT,
                hora             TEXT,
                maquina          TEXT,
                tipo             TEXT,
                motivo           TEXT,
                descripcion      TEXT,
                tecnico          TEXT,
                duracion         REAL,
                estado           TEXT DEFAULT 'Pendiente',
                programada       TEXT,
                observaciones    TEXT,
                calendar_done    INTEGER DEFAULT 0
            )
        """)
        conn.commit()


def insert_maintenance(data: dict) -> int:
    """Inserta un registro y retorna el ID generado."""
    programada = "Sí" if data.get("tipo") == "Programada" else "No"
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO mantenciones
              (fecha_registro, fecha, hora, maquina, tipo, motivo,
               descripcion, tecnico, duracion, estado, programada,
               observaciones, calendar_done)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,0)
        """, (
            datetime.now().strftime("%d/%m/%Y %H:%M"),
            data.get("fecha", ""),
            data.get("hora", ""),
            data.get("maquina", ""),
            data.get("tipo", ""),
            data.get("motivo", ""),
            data.get("descripcion", ""),
            data.get("tecnico", ""),
            float(data.get("duracion", 1) or 1),
            "Pendiente",
            programada,
            data.get("observaciones", ""),
        ))
        conn.commit()
        return cur.lastrowid


def get_recent(n: int = 20) -> list:
    """Últimos N registros, más recientes primero."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM mantenciones ORDER BY id DESC LIMIT ?", (n,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_pending_calendar() -> list:
    """Eventos no enviados aún a Google Calendar."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM mantenciones WHERE calendar_done = 0 ORDER BY id"
        ).fetchall()
    return [dict(r) for r in rows]


def mark_calendar_done(record_id: int):
    """Marca un registro como ya agendado en el calendario."""
    with get_conn() as conn:
        conn.execute(
            "UPDATE mantenciones SET calendar_done = 1 WHERE id = ?", (record_id,)
        )
        conn.commit()


def get_all_for_export() -> list:
    """Todos los registros para exportar a Excel."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM mantenciones ORDER BY id"
        ).fetchall()
    return [dict(r) for r in rows]
