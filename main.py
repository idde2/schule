from flask import Flask, render_template, request, redirect, session, make_response, jsonify
import csv
import io
import openpyxl
from datetime import datetime
from flask_socketio import SocketIO
from pyngrok import ngrok, conf
import os
from func import get_connection, set_config, get_conf, log, background_updater, register_socketio

app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading")
app.secret_key = "supersecretkey2025"
app.config['SECRET_KEY'] = 'secret'
register_socketio(socketio)


@app.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, wert FROM daten ORDER BY id DESC")
    daten = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("index.html", daten=daten)


@app.route("/tabelle")
def tabelle():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, wert FROM daten ORDER BY id DESC")
    daten = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("tabelle.html", daten=daten)


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

        log(name, wert, "eingabe")

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

    log(id, 0.0, "delete")
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

        log(name, wert, "edit")

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

    log("-", 0.0, "delete all")

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
            log("-", 0.0, "Admin pin")

            return redirect("/pin")


@app.before_request
def protect_main():
    if not request.path.startswith("/login") and not request.path.startswith("/api"):
        if session.get("main") != True:
            return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("login") == get_conf("login"):
            session["main"] = True

            log("-", 0.0, "Aufruf ok")

            return redirect("/")
        else:
            log("-", 0.0, "Aufruf falsch")
            return render_template("login.html", error=True)
    if session.get("main") != True:
        return render_template("login.html")


@app.route("/pin", methods=["GET", "POST"])
def pin():
    if request.method == "POST":
        if request.form.get("pin") == get_conf("pin"):
            session["admin_ok"] = True

            log("-", 0.0, "Admin ok")

            return redirect("/admin")
        else:
            log("-", float(request.form.get("pin")), "Admin falsch")
        return render_template("pin.html", error=True)
    return render_template("pin.html")


@app.route("/admin/logout")
def admin_logout():
    session["admin_ok"] = False
    log("", 0.0, "Admin logout")
    return redirect("/admin")


@app.route("/logout")
def logout():
    session["main"] = False
    session["admin_ok"] = False
    log("", 0.0, "logout")
    return redirect("/login")


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



@app.route("/info")
def info():
    return render_template("info.html")

@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/turnier")
def turnier():
    return render_template("turnier.html")





settings = {
    "update": False
}
@app.get("/api")
def get_settings():
    return jsonify(settings)
@app.post("/api")
def update_settings():
    data = {}

    if request.args:
        data.update(request.args)

    if request.json:
        data.update(request.json)

    for key, value in data.items():
        settings[key] = value

    return jsonify({"status": "ok", "updated": data})



@app.get("/api/var/<name>")
def get_variable(name):
    return jsonify({name: settings.get(name)})

@app.post("/api/var/<name>")
def set_variable(name):
    value = request.json.get("value")
    settings[name] = value
    return jsonify({"status": "ok", name: value})






if __name__ == "__main__":

    set_config()

    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        ngrok.kill()
        if get_conf("ngrok") == "False":
            num = input("number:")
            if num == "1":
                    conf.get_default().auth_token = "37Rwi5yWodWiErSDF3zrKEiam7x_3jaqt3R8w28zvNKNEt3Pt"
                    public_url = ngrok.connect(5000, "http")
                    print("NGROK URL:", public_url)
        if get_conf("ngrok") == "True":
            conf.get_default().auth_token = "37Rwi5yWodWiErSDF3zrKEiam7x_3jaqt3R8w28zvNKNEt3Pt"
            public_url = ngrok.connect(5000, "http")
            print("NGROK URL:", public_url)

    socketio.start_background_task(background_updater)
    socketio.run(
        app,
        host="0.0.0.0",
        port=get_conf("port"),
        debug=True,

        allow_unsafe_werkzeug=True
    )

#         ssl_context=("https/cert.pem", "https/key.pem"),
