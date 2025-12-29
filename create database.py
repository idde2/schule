import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="py",
    password="py!!"
)
cursor = conn.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS schule")
cursor.execute("USE schule")

cursor.execute("""
CREATE TABLE IF NOT EXISTS daten (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    wert FLOAT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS verlauf (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teilnehmer_id INT NOT NULL,
    wert FLOAT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teilnehmer_id) REFERENCES daten(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip VARCHAR(50),
    name VARCHAR(255),
    wert FLOAT,
    action VARCHAR(50),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("Datenbank und Tabellen wurden überprüft und sind bereit.")
