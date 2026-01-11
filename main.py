from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify
import csv
import io
import openpyxl
from datetime import datetime
from collections import deque
import itertools

import threading
from flask_socketio import SocketIO, emit
import time
import mysql.connector

app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = "supersecretkey2025"
app.config['SECRET_KEY'] = 'secret'

@app.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, wert FROM daten ORDER BY id DESC")
    daten = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("index.html", daten=daten )

@app.route("/tabelle")
def tabelle():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, wert FROM daten ORDER BY id DESC")
    daten = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("tabelle.html", daten=daten )

@app.route("/rang")
def rang():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, wert FROM daten ORDER BY wert DESC")
    daten = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("rang.html", daten=daten)


@app.route("/eingabe", methods=["GET", "POST"])
def eingabe():
    if request.method == "POST":
        name = request.form["name"].strip()
        wert = float(request.form["wert"])

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM daten WHERE name = %s", (name,))
        (count,) = cursor.fetchone()
        if count > 0:
            conn.close()
            return jsonify({"success": False, "error": "name_exists"})

        cursor.execute("INSERT INTO daten (name, wert) VALUES (%s, %s)", (name, wert))
        conn.commit()
        new_id = cursor.lastrowid

        user_ip = request.remote_addr
        cursor.execute(
            "INSERT INTO log (ip, name, wert, action) VALUES (%s, %s, %s, %s)",
            (user_ip, name, wert, "eingabe")
        )
        conn.commit()

        cursor.execute("SELECT name, wert FROM daten ORDER BY wert DESC")
        rang = cursor.fetchall()

        conn.close()

        socketio.emit("update", {
            "id": new_id,
            "name": name,
            "wert": wert
        })

        socketio.emit("rang_update", {
            "daten": [{"name": n, "wert": w} for n, w in rang]
        })

        return jsonify({"success": True})

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM daten")
    namen = [row[0] for row in cursor.fetchall()]
    conn.close()

    return render_template("eingabe.html", namen=namen)




@app.route("/admin")
def admin():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, wert FROM daten ORDER BY id DESC")
    daten = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin.html", daten=daten)

@app.route("/delete/<int:id>")
def delete(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM daten WHERE id = %s", (id,))
    conn.commit()

    user_ip = request.remote_addr
    cursor.execute(
        "INSERT INTO log (ip, name, wert, action) VALUES (%s, %s, %s, %s)",
        (user_ip, id, 0.0, "delete")
    )
    conn.commit()

    cursor.close()
    conn.close()
    return redirect("/admin")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form.get("name")
        wert = request.form.get("wert")

        cursor.execute(
            "UPDATE daten SET name=%s, wert=%s WHERE id=%s",
            (name, wert, id)
        )
        conn.commit()

        user_ip = request.remote_addr
        cursor.execute(
            "INSERT INTO log (ip, name, wert, action) VALUES (%s, %s, %s, %s)",
            (user_ip, name, wert, "edit")
        )
        conn.commit()

        cursor.close()
        conn.close()
        return redirect("/admin")

    cursor.execute("SELECT id, name, wert FROM daten WHERE id=%s", (id,))
    eintrag = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template("edit.html", eintrag=eintrag)

@app.route("/delete_all")
def delete_all():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM verlauf")
    cursor.execute("DELETE FROM daten")
    cursor.execute("ALTER TABLE daten AUTO_INCREMENT = 1")
    cursor.execute("ALTER TABLE verlauf AUTO_INCREMENT = 1")
    conn.commit()

    user_ip = request.remote_addr
    cursor.execute(
        "INSERT INTO log (ip, name, wert, action) VALUES (%s, %s, %s, %s)",
        (user_ip,"-",0.0, "delete all")
    )
    conn.commit()

    cursor.close()
    conn.close()

    socketio.emit("rang_update", {"daten": []})
    socketio.emit("tabelle_update", {"daten": []})
    socketio.emit("admin_update", {"daten": []})

    return redirect("/admin")


@app.before_request
def protect_admin():
    if request.path.startswith("/admin"):
        if session.get("admin_ok") != True:
            conn = get_connection()
            cursor = conn.cursor()
            user_ip = request.remote_addr
            cursor.execute(
                "INSERT INTO log (ip, name, wert, action) VALUES (%s, %s, %s, %s)",
                (user_ip, "-", 0.0, "pin")
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect("/pin")

@app.route("/pin", methods=["GET", "POST"])
def pin():

    if request.method == "POST":
        if request.form.get("pin") == "2026":
            session["admin_ok"] = True

            conn = get_connection()
            cursor = conn.cursor()
            user_ip = request.remote_addr
            cursor.execute(
                "INSERT INTO log (ip, name, wert, action) VALUES (%s, %s, %s, %s)",
                (user_ip, "-", 0.0, "Admin ok")
            )
            conn.commit()
            cursor.close()
            conn.close()

            return redirect("/admin")
        else:
            conn = get_connection()
            cursor = conn.cursor()
            user_ip = request.remote_addr
            cursor.execute(
                "INSERT INTO log (ip, name, wert, action) VALUES (%s, %s, %s, %s)",
                (user_ip, "-", float(request.form.get("pin")), "Admin falsch")
            )
            conn.commit()
            cursor.close()
            conn.close()
        return render_template("pin.html", error=True)
    return render_template("pin.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin")


@app.route("/export/csv")
def export_csv():
    conn = get_connection()

    c = conn.cursor()
    c.execute("SELECT id, name, wert FROM daten")
    rows = c.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Wert"])
    writer.writerows(rows)

    filename = f"export_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "text/csv"
    return response


@app.route("/export/excel")
def export_excel():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, wert FROM daten")
    rows = c.fetchall()
    conn.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Daten"

    ws.append(["ID", "Name", "Wert"])
    for row in rows:
        ws.append(row)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"export_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response

@app.route("/profile")
def profile_list():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, wert FROM daten ORDER BY name ASC")
    daten = c.fetchall()
    conn.close()

    return render_template("profile_list.html", daten=daten)

@app.route("/profil/<int:teilnehmer_id>")
def profil(teilnehmer_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT id, name, wert FROM daten WHERE id = %s", (teilnehmer_id,))
    teilnehmer = c.fetchone()

    if not teilnehmer:
        conn.close()
        return "Teilnehmer nicht gefunden", 404

    c.execute("""
        SELECT wert, timestamp 
        FROM verlauf 
        WHERE teilnehmer_id = %s 
        ORDER BY timestamp DESC
    """, (teilnehmer_id,))
    verlauf = c.fetchall()

    conn.close()

    return render_template("profil.html", teilnehmer=teilnehmer, verlauf=verlauf)

@app.route("/admin/log")
def admin_log():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT ip, name, wert, action, timestamp FROM log ORDER BY timestamp DESC")
    logs = c.fetchall()
    conn.close()

    return render_template("admin_log.html", logs=logs)

@app.route("/delete_all_logs")
def delete_all_logs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM log")
    cursor.execute("ALTER TABLE log AUTO_INCREMENT = 1")
    conn.commit()
    cursor.close()
    conn.close()
    return redirect("/admin/log")








@app.route('/turnier')
def turnier():
    return render_template("turnier.html")
players = []
matches = []
cooldown_queue = deque()
max_parallel_games = 2
match_id_counter = itertools.count(1)

def serialize_state():
    return {
        'players': players,
        'matches': matches,
        'max_parallel_games': max_parallel_games
    }

def get_ready_players():
    return [p for p in players if p['status'] == 'ready']

def get_active_matches():
    return [m for m in matches if m['status'] == 'playing']

def schedule_matches():
    ready = get_ready_players()
    active = get_active_matches()
    slots = max_parallel_games - len(active)
    new_matches = []
    while len(ready) >= 2 and slots > 0:
        p1 = ready.pop(0)
        p2 = ready.pop(0)
        p1['status'] = 'playing'
        p2['status'] = 'playing'
        m = {
            'id': next(match_id_counter),
            'p1': p1['id'],
            'p2': p2['id'],
            'winner': None,
            'round': 1,
            'status': 'playing'
        }
        matches.append(m)
        new_matches.append(m)
        slots -= 1
    return new_matches

@app.route('/turnier/init', methods=['POST'])
def turnier_init():
    global players, matches, cooldown_queue, max_parallel_games, match_id_counter
    data = request.json
    num_players = int(data['num_players'])
    max_parallel_games = int(data['max_parallel_games'])
    players = [{'id': i + 1, 'name': f'Spieler {i + 1}', 'status': 'ready'} for i in range(num_players)]
    matches = []
    cooldown_queue = deque()
    match_id_counter = itertools.count(1)
    socketio.emit('state_update', serialize_state(), broadcast=True)
    return jsonify({'status': 'ok'})

@app.route('/turnier/start', methods=['POST'])
def turnier_start():
    schedule_matches()
    socketio.emit('state_update', serialize_state(), broadcast=True)
    return jsonify({'status': 'ok'})

@app.route('/turnier/result', methods=['POST'])
def turnier_result():
    data = request.json
    match_id = data['match_id']
    winner_id = data['winner_id']
    for m in matches:
        if m['id'] == match_id and m['status'] == 'playing':
            m['winner'] = winner_id
            m['status'] = 'finished'
            loser_id = m['p1'] if m['p2'] == winner_id else m['p2']
            for p in players:
                if p['id'] == winner_id:
                    p['status'] = 'cooldown'
                    cooldown_queue.append(p['id'])
                if p['id'] == loser_id:
                    p['status'] = 'out'
            break
    socketio.emit('state_update', serialize_state(), broadcast=True)
    return jsonify({'status': 'ok'})

@app.route('/turnier/cooldown', methods=['POST'])
def turnier_cooldown():
    if cooldown_queue:
        pid = cooldown_queue.popleft()
        for p in players:
            if p['id'] == pid:
                p['status'] = 'ready'
                break
    socketio.emit('state_update', serialize_state(), broadcast=True)
    return jsonify({'status': 'ok'})

@socketio.on('request_state')
def handle_request_state():
    emit('state_update', serialize_state())



@app.route("/info")
def info():
    return render_template("info.html")







def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="py",
        password="py!!",
        database="schule"
    )

def background_updater():
    while True:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, wert FROM daten ORDER BY id DESC LIMIT 1")
        latest = cursor.fetchone()

        cursor.execute("SELECT id, name, wert FROM daten ORDER BY id DESC")
        alle = cursor.fetchall()

        cursor.execute("SELECT name, wert FROM daten ORDER BY wert DESC")
        rang = cursor.fetchall()

        cursor.execute("SELECT id, name, wert FROM daten ORDER BY id DESC")
        admin = cursor.fetchall()

        cursor.close()
        conn.close()

        if latest:
            id, name, wert = latest
        else:
            id, name, wert = None, None, None

        socketio.emit("update", {
            "id": id,
            "name": name,
            "wert": wert
        })

        socketio.emit("tabelle_update", {
            "daten": [{"id": r[0], "name": r[1], "wert": r[2]} for r in alle]
        })

        socketio.emit("rang_update", {
            "daten": [{"name": r[0], "wert": r[1]} for r in rang]
        })

        socketio.emit("admin_update", {
            "daten": [{"id": r[0], "name": r[1], "wert": r[2]} for r in admin]
        })

        socketio.sleep(1)





if __name__ == "__main__":
    socketio.start_background_task(background_updater)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
