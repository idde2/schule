import subprocess
import os
from flask import Flask, render_template, request, redirect, session, make_response, jsonify, Response, Blueprint

cmd_web = Blueprint("cmd_web", __name__)

log = []

@cmd_web.route("/")
def cmd():
    global log
    return render_template("cmd.html", daten=log, path=os.getcwd())
@cmd_web.route("/<command>")
def cmd_run(command):
    global log
    log.append(send_cmd(command) + "\n")
    return redirect("/cmd")

def send_cmd(command):
    global log

    if command.lower() in ("exit", "quit"):
        return "Beendet."

    # cd extra behandeln
    if command.startswith("cd "):
        path = command[3:].strip()
        try:
            os.chdir(path)
            return f"Pfad gewechselt zu: {os.getcwd()}"
        except FileNotFoundError:
            return "Der Pfad wurde nicht gefunden."

    if command.startswith("clear"):
        log.clear()
        return "Log geleert."

    # CMD-Befehl
    process = subprocess.Popen(
        ["cmd", "/c", command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    out, err = process.communicate()

    if out:
        return out
    if err:
        return err

    return ""  # Fallback
