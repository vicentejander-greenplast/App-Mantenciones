# =============================================================
#  GREENPLAST - App de Mantenciones (Cloud-Ready)
#  Despliegue: Railway  |  Local: http://localhost:5001
# =============================================================

import os
from datetime import datetime
from functools import wraps

from flask import (Flask, render_template, request, jsonify,
                   send_file, session, redirect, url_for)
import io
import requests as http_requests

from config import (MACHINES, TECHNICIANS, MAINTENANCE_TYPES,
                    COMMON_REASONS, APP_PORT, SECRET_KEY)
from database import init_db, insert_maintenance, get_recent, get_pending_calendar, mark_calendar_done, get_all_for_export
from excel_manager import generate_excel_bytes

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Contraseña de acceso (cámbiala en la variable de entorno APP_PASSWORD)
APP_PASSWORD = os.environ.get("APP_PASSWORD", "greenplast2024")

# Clave secreta para la API del calendario (usada por el scheduled task de Cowork)
API_SECRET   = os.environ.get("API_SECRET", "gp-cal-sync-2024")

# URL del Google Apps Script (se configura en Railway → Variables)
APPS_SCRIPT_URL = os.environ.get("APPS_SCRIPT_URL", "")

# Inicializar base de datos al arrancar
init_db()


def send_to_calendar(data: dict, record_id: int) -> bool:
    """Llama al Google Apps Script para crear el evento inmediatamente."""
    if not APPS_SCRIPT_URL:
        return False
    try:
        payload = {**data, "secret": API_SECRET}
        resp = http_requests.post(APPS_SCRIPT_URL, json=payload, timeout=15)
        result = resp.json()
        if result.get("ok"):
            mark_calendar_done(record_id)
            return True
    except Exception as e:
        print(f"[Calendar] Error: {e}")
    return False


# ── Decorador de login ───────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ── LOGIN ────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == APP_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        error = "Contraseña incorrecta."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))




# ── PÁGINA PRINCIPAL ─────────────────────────────────────────
@app.route("/")
@login_required
def index():
    records = get_recent(20)
    return render_template(
        "index.html",
        machines=MACHINES,
        technicians=TECHNICIANS,
        maintenance_types=MAINTENANCE_TYPES,
        common_reasons=COMMON_REASONS,
        records=records,
        today=datetime.now().strftime("%Y-%m-%d"),
    )


# ── REGISTRAR MANTENCIÓN ─────────────────────────────────────
@app.route("/agendar", methods=["POST"])
@login_required
def agendar():
    try:
        data = {
            "fecha":        request.form.get("fecha", "").strip(),
            "hora":         request.form.get("hora", "08:00").strip(),
            "maquina":      request.form.get("maquina", "").strip(),
            "tipo":         request.form.get("tipo", "").strip(),
            "motivo":       request.form.get("motivo", "").strip(),
            "descripcion":  request.form.get("descripcion", "").strip(),
            "tecnico":      request.form.get("tecnico", "").strip(),
            "duracion":     request.form.get("duracion", "1").strip(),
            "observaciones": request.form.get("observaciones", "").strip(),
        }

        if not data["maquina"]:
            return jsonify({"ok": False, "error": "Selecciona la máquina."}), 400
        if not data["tipo"]:
            return jsonify({"ok": False, "error": "Selecciona el tipo de mantención."}), 400
        if not data["motivo"]:
            return jsonify({"ok": False, "error": "Indica el motivo."}), 400
        if not data["tecnico"]:
            return jsonify({"ok": False, "error": "Indica el técnico responsable."}), 400
        if not data["fecha"]:
            return jsonify({"ok": False, "error": "Indica la fecha."}), 400

        record_id = insert_maintenance(data)
        send_to_calendar(data, record_id)

        return jsonify({
            "ok":      True,
            "id":      record_id,
            "message": f"Mantención #{record_id} registrada exitosamente.",
        })

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500


# ── DESCARGA EXCEL ────────────────────────────────────────────
@app.route("/descargar-excel")
@login_required
def descargar_excel():
    records = get_all_for_export()
    excel_bytes = generate_excel_bytes(records)
    filename = f"Mantenciones_Greenplast_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return send_file(
        io.BytesIO(excel_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename,
    )


# ── API: EVENTOS PENDIENTES PARA CALENDARIO ──────────────────
# Usada por el scheduled task de Cowork para crear eventos automáticamente
@app.route("/api/pending-calendar")
def api_pending_calendar():
    if request.args.get("secret") != API_SECRET:
        return jsonify({"error": "No autorizado"}), 401
    return jsonify(get_pending_calendar())


@app.route("/api/mark-processed")
def api_mark_processed():
    if request.args.get("secret") != API_SECRET:
        return jsonify({"error": "No autorizado"}), 401
    try:
        record_id = int(request.args.get("id", 0))
        mark_calendar_done(record_id)
        return jsonify({"ok": True})
    except (ValueError, TypeError) as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# ── HISTORIAL JSON ────────────────────────────────────────────
@app.route("/api/historial")
@login_required
def api_historial():
    return jsonify(get_recent(50))


# ── TODOS LOS REGISTROS (para sincronizar Excel local) ────────
@app.route("/api/todos")
def api_todos():
    if request.args.get("secret") != API_SECRET:
        return jsonify({"error": "No autorizado"}), 401
    return jsonify(get_all_for_export())


# ── MAIN ──────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", APP_PORT))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    print("=" * 60)
    print("  GREENPLAST — App de Mantenciones")
    print(f"  http://localhost:{port}")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=debug)
