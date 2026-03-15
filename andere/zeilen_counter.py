import os

ordner = "C:/Users/Eddi/PycharmProjects/PythonProject/schule/andere"

gesamt = 0

for datei in os.listdir(ordner):
    pfad = os.path.join(ordner, datei)

    if os.path.isfile(pfad):
        with open(pfad, "r", encoding="utf-8", errors="ignore") as f:
            zeilen = sum(1 for _ in f)
            gesamt += zeilen

print("Gesamtzeilen:", gesamt)
