import bcrypt
import requests
from flask import Flask, render_template, request, redirect, session, make_response, jsonify, Response
import csv
import subprocess
import openpyxl
from datetime import datetime
from flask_socketio import SocketIO
from pyngrok import ngrok, conf
import os


from func import get_connection, set_config, get_conf, log, background_updater, register_socketio, test_admin
from login import login
from commandline import cmd_web
from remote_webdesk import *
from api import api, register_api_socketio

app = Flask(__name__)

app.register_blueprint(login)
app.register_blueprint(cmd_web, url_prefix="/cmd")
app.register_blueprint(rdp, url_prefix="/remotedesktop")
app.register_blueprint(api, url_prefix="/api")

socketio = SocketIO(app, async_mode="threading")
app.secret_key = "supersecretkey2025"
app.config['SECRET_KEY'] = 'secret'
register_socketio(socketio)
register_api_socketio(socketio)

APACHE_BASE = "http://localhost/phpmyadmin"



#-----------------------------------------------------------------------------------------------------------------------------------------------before request--------------------------------------------------------------------------------
@app.before_request
def protect():
    path = request.path

    if path.startswith("/static"):
        return

    if path.startswith("/api"):
        return

    if path.startswith("/login"):
        return

    if path.startswith("/pin"):
        return

    if path.startswith("/admin") or path.startswith("/remotedesktop") or path.startswith("/phpmyadmin") or path.startswith("/register") or path.startswith("/register2") or path.startswith("/cmd"):
        if session.get("admin_ok") != True:
            log(session["user"],"-", 0.0, "login failed")
            return redirect("/pin")

    if session.get("main") != True:
        return redirect("/login")




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

        if wert > 100000000 or wert < 0.001:
            return jsonify({"success": False, "error": "wert_out_of_range"})

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

        log(session["user"],name, wert, "eingabe")

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

    log(session["user"], id, 0.0, "delete")
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

        log(session["user"],name, wert, "edit")

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

    log(session["user"],"-", 0.0, "delete all")

    cursor.close()
    conn.close()

    socketio.emit("rang_update", {"daten": []})
    socketio.emit("tabelle_update", {"daten": []})
    socketio.emit("admin_update", {"daten": []})

    return redirect("/admin")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = str(request.form.get("username"))
        password = str(request.form.get("password"))
        admin = 1 if request.form.get("admin") == "1" else 0
        conn = get_connection()
        cursor = conn.cursor()

        sql = "SELECT id FROM users WHERE username = %s"
        cursor.execute(sql, (name,))
        user = cursor.fetchone()
        if not user:
            password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            sql = "INSERT INTO users (username, password_hash, admin) VALUES (%s, %s,%s)"
            values = (name, password_hash,admin)

            cursor.execute(sql, values)
            conn.commit()
            return redirect("/login")
        else:
            return render_template("register.html", daten="Benutzername existiert bereits")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        username = request.form.get("username")
        password = request.form.get("password")

        sql = "SELECT * FROM users WHERE username = %s"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()

        if user:
            stored_hash = user["password_hash"].encode("utf-8")

            if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
                session["main"] = True
                log(username,"-", 0.0, "Login ok")
                session["admin_ok"] = True if test_admin(username) == 1 else False
                session["user"] = username
                return redirect("/")
            else:
                log(username,password, 0.0, "Passwort falsch")
                return render_template("login.html", daten="falsches password")
        else:
            log(username,"-", 0.0, "Nutzer nicht gefunden")
            return render_template("login.html", daten="falscher benutzername")

    if session.get("main") == True:
        return redirect("/")

    return render_template("login.html")



@app.route("/pin")
def pin():
    return render_template("pin.html")


@app.route("/admin/logout")
def admin_logout():
    session["admin_ok"] = False
    log(session["user"],"", 0.0, "Admin logout")
    return redirect("/admin")


@app.route("/logout")
def logout():
    session["main"] = False
    session["admin_ok"] = False
    log(session["user"],"", 0.0, "logout")
    session.pop("user", None)
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



@app.route("/profil")
def profil():
    conn = get_connection()
    c = conn.cursor()
    username = session["user"]
    admin = test_admin(username)
    c.execute("SELECT email FROM users WHERE username = %s", (username,))
    email = c.fetchone()
    email = email[0] if email else "Keine Email"
    daten = [username, email, admin]


    conn.close()

    return render_template("profil.html", daten=daten)

@app.route("/admin/log")
def admin_log():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT ip, username, name, wert, action, timestamp FROM log ORDER BY timestamp DESC")
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
@app.route("/test2")
def test2():
    return render_template("test2.html")

@app.route("/turnier")
def turnier():
    return render_template("turnier.html")




@app.route("/phpmyadmin", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/phpmyadmin/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/phpmyadmin/<path:path>", methods=["GET", "POST"])
def proxy(path):
    url = f"{APACHE_BASE}/{path}"

    headers = dict(request.headers)
    headers["Host"] = "localhost"

    resp = requests.request(
        method=request.method,
        url=url,
        params=request.args,
        data=request.form,
        cookies=request.cookies,
        headers=headers,
        allow_redirects=False
    )

    excluded = ["content-encoding", "transfer-encoding", "connection"]
    headers_out = [(k, v) for k, v in resp.headers.items() if k.lower() not in excluded]

    return Response(resp.content, resp.status_code, headers_out)






if __name__ == "__main__":

    set_config()
    print(subprocess.Popen(["cmd.exe","/c", "httpd"],creationflags=subprocess.CREATE_NO_WINDOW))
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        ngrok.kill()
        if get_conf("ngrok") == "False":
            num = "0"
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
