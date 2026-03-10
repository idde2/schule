import tkinter as tk
import mysql.connector
import configparser
import os


def set_config():
    if os.path.isfile(conf):
        config.read(conf)
    else:
        config["DEFAULT"] = {
            "host": "localhost",
            "user": "py",
            "password": "py!!",
            "database": "schule"
        }
    with open(conf, "w") as f:
        config.write(f)


def get_connection():
    return mysql.connector.connect(
        host=get_conf("host"),
        user=get_conf("user"),
        password=get_conf("password"),
        database=get_conf("database")
    )


config = configparser.ConfigParser()
conf = "config.ini"



def get_conf(option, fallback=None):
    return config["DEFAULT"].get(option, fallback)


def log(name, wert, action):
    conn = get_connection()
    cursor = conn.cursor()

    user_ip = "GUI"

    cursor.execute(
        "INSERT INTO log (ip, name, wert, action) VALUES (%s, %s, %s, %s)",
        (user_ip, name, wert, action)
    )

    conn.commit()
    cursor.close()
    conn.close()


def senden():

    try:
        Wert = float(wert.get())
        Name = str((name.get()))
        msg("Gespeichert", "lightgreen")
        sql(Name, Wert)
    except ValueError:
        msg("Fehler: Keine gültige Zahl!", "red")
        wert.delete(0, tk.END)
        return
    name.delete(0, tk.END)
    wert.delete(0, tk.END)

def msg(text, color="white"):
    msg_label.config(text=text, fg=color)
    msg_label.after(2000, lambda: msg_label.config(text=""))


root = tk.Tk()
root.title("Eingabe")
root.geometry("400x200")
root.configure(bg="#1e1e1e")

msg_label = tk.Label(root, text="", bg="#1e1e1e", fg="white", font=("Arial", 14))
msg_label.grid(row=99, column=0, columnspan=2, pady=10)


label_name = tk.Label(root, text="Name:", bg="#1e1e1e", fg="white", font=("Arial", 14))
label_name.grid(row=0, column=0, padx=10, pady=5, sticky="w")

name = tk.Entry(root, bg="#2d2d2d", fg="white", insertbackground="white", highlightthickness=0, relief="flat", width=20, font=("Arial", 14))
name.grid(row=0, column=1, padx=10, pady=5, sticky="we")


label_wert = tk.Label(root, text="Wert:", bg="#1e1e1e", fg="white", font=("Arial", 14))
label_wert.grid(row=1, column=0, padx=10, pady=5, sticky="w")

wert = tk.Entry(root, bg="#2d2d2d", fg="white", insertbackground="white", highlightthickness=0, relief="flat", width=20, font=("Arial", 14))
wert.grid(row=1, column=1, padx=10, pady=5, sticky="we")

root.grid_columnconfigure(1, weight=1)


name.bind("<Return>", lambda event: senden())
wert.bind("<Return>", lambda event: senden())


button = tk.Button(root, text="Senden", command=senden, bg="#3a3a3a", fg="white", activebackground="#505050", relief="flat", padx=10, pady=5, font=("Arial", 14))
button.grid(row=2, column=0, columnspan=2, pady=10)


def sql(name_sql, wert_sql):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM daten WHERE name = %s", (name_sql,))
    (count,) = cursor.fetchone()
    if count > 0:
        conn.close()
        msg("name existiert schon!", "red")
        name.delete(0, tk.END)
        return

    cursor.execute("INSERT INTO daten (name, wert) VALUES (%s, %s)", (name_sql, wert_sql))
    conn.commit()

    name.delete(0, tk.END)
    wert.delete(0, tk.END)

    log(name_sql, wert_sql, "eingabe")
    conn.close()


if __name__ == "__main__":
    set_config()
    root.mainloop()
