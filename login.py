import random

from flask import Flask, render_template, request, redirect, session, make_response, jsonify, Response, Blueprint
from func import get_connection, set_config, get_conf, log, background_updater, register_socketio, test_admin
import bcrypt
import os
import smtplib
from email.mime.text import MIMEText
import keyring

bp = Blueprint("bp", __name__)
users = {}

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = str(request.form.get("username"))
        password = str(request.form.get("password"))
        token = (request.form.get("token"))
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

@bp.route("/register2", methods=["GET", "POST"])
def register2():
    global users

    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        token = request.form.get("token")

        try:
            token = int(token)
        except:
            return render_template("register2.html", daten="Token muss eine Zahl sein")

        # Email anhand des Tokens finden
        email = next((k for k, v in users.items() if v == token), None)

        if email is None:
            return render_template("register2.html", daten="Ungültiger Token")

        admin = 1 if request.form.get("admin") == "1" else 0

        conn = get_connection()
        cursor = conn.cursor()

        # Prüfen ob Username existiert
        cursor.execute("SELECT id FROM users WHERE username = %s", (name,))
        user = cursor.fetchone()

        if not user:
            password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            cursor.execute(
                "INSERT INTO users (username, password_hash, admin, email) VALUES (%s, %s, %s, %s)",
                (name, password_hash, admin, email)
            )
            conn.commit()

            # Token verbrauchen
            users.pop(email, None)

            return redirect("/login")

        else:
            return render_template("register2.html", daten="Benutzername existiert bereits")

    return render_template("register2.html")


@bp.route("/register2/<email>", methods=["GET", "POST"])
def register_token(email):
    global users
    users[email] = random.randint(100000, 999999)
    send_mail(email,f"token { users[email]}")
    return redirect("/register2")






def send_mail(email,msg):
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    USERNAME = "verifikation.eddi@gmail.com"
    DESTINATION = email
    APP_PASSWORD = keyring.get_password("gmail", "verifikation.eddi@gmail.com")


    msg = MIMEText(msg, "plain")
    msg["Subject"] = "verification"
    msg["From"] = USERNAME
    msg["To"] = DESTINATION

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(USERNAME, APP_PASSWORD)
        server.send_message(msg)

