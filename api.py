from flask import Blueprint, jsonify, request
from func import get_connection, log, test_admin
import bcrypt

api = Blueprint("api", __name__)

socketio = None

API_KEY = "2026!"

settings = {
    "update": False
}


# ------------------------------
# SOCKETIO REGISTRIEREN
# ------------------------------

def register_api_socketio(sio):
    global socketio
    socketio = sio


# ------------------------------
# AUTH CHECK
# ------------------------------

def check_api_key():

    key = request.headers.get("X-API-KEY")

    if key != API_KEY:
        return jsonify({"error": "unauthorized"}), 401

    return None


# ==============================
# USERS API
# ==============================

@api.get("/users")
def api_get_users():

    auth = check_api_key()
    if auth:
        return auth

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, username, admin FROM users"
    )

    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(users)


@api.post("/users")
def api_create_user():

    auth = check_api_key()
    if auth:
        return auth

    data = request.json

    username = data.get("username")
    password = data.get("password")
    admin = data.get("admin", 0)

    if not username or not password:
        return jsonify({"error": "missing_data"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username=%s",
        (username,)
    )

    if cursor.fetchone():
        return jsonify({"error": "user_exists"}), 400

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    cursor.execute(
        "INSERT INTO users (username, password_hash, admin) VALUES (%s,%s,%s)",
        (username, password_hash, admin)
    )

    conn.commit()

    log("api", username, 0.0, "user_create")

    cursor.close()
    conn.close()

    return jsonify({"status": "user_created"})


# ==============================
# LOG API
# ==============================

@api.get("/logs")
def api_get_logs():

    auth = check_api_key()
    if auth:
        return auth

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT ip, username, name, wert, action, timestamp FROM log ORDER BY timestamp DESC"
    )

    logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(logs)


# ==============================
# DATEN ADMIN API
# ==============================

@api.delete("/admin/delete/<int:id>")
def api_delete_daten(id):

    auth = check_api_key()
    if auth:
        return auth

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM daten WHERE id=%s",
        (id,)
    )

    conn.commit()

    log("api", id, 0.0, "api_delete")

    cursor.close()
    conn.close()

    return jsonify({"status": "deleted"})


@api.put("/admin/edit/<int:id>")
def api_edit_daten(id):

    auth = check_api_key()
    if auth:
        return auth

    data = request.json

    name = data.get("name")
    wert = data.get("wert")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE daten SET name=%s, wert=%s WHERE id=%s",
        (name, wert, id)
    )

    conn.commit()

    log("api", name, wert, "api_edit")

    cursor.close()
    conn.close()

    return jsonify({"status": "updated"})


@api.delete("/admin/delete_all")
def api_delete_all():

    auth = check_api_key()
    if auth:
        return auth

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM daten")
    cursor.execute("DELETE FROM verlauf")

    conn.commit()

    log("api", "-", 0.0, "delete_all")

    cursor.close()
    conn.close()

    if socketio:
        socketio.emit("rang_update", {"daten": []})

    return jsonify({"status": "all_deleted"})



@api.post("/daten")
def api_create_daten():

    auth = check_api_key()
    if auth:
        return auth

    data = request.json

    name = data.get("name")
    wert = data.get("wert")

    if not name or wert is None:
        return jsonify({"error": "missing_data"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM daten WHERE name = %s", (name,))
    (count,) = cursor.fetchone()
    if count > 0:
        conn.close()
        return jsonify({"success": False, "error": "name_exists"})

    cursor.execute(
        "INSERT INTO daten (name, wert) VALUES (%s,%s)",
        (name, wert)
    )

    conn.commit()
    new_id = cursor.lastrowid

    log("api", name, wert, "api_create")

    cursor.close()
    conn.close()

    return jsonify({
        "status": "created",
        "id": new_id
    })