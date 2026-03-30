import os

gesamt = 0

def count(ordner):
    global gesamt
    for datei in os.listdir(ordner):
        pfad = os.path.join(ordner, datei)

        if os.path.isfile(pfad):
            with open(pfad, "r", encoding="utf-8", errors="ignore") as f:
                zeilen = sum(1 for _ in f)
                gesamt += zeilen

for i in range(4):

    if i == 0:
        ordner = "C:/Users/Eddi/PycharmProjects/PythonProject/schule/templates"
    if i == 1:
        ordner = "C:/Users/Eddi/PycharmProjects/PythonProject/schule/static/css"
    if i == 2:
        ordner = "C:/Users/Eddi/PycharmProjects/PythonProject/schule/static/js"
    if i == 3:
        ordner = "C:/Users/Eddi/PycharmProjects/PythonProject/schule/"
    count(ordner)

print("Gesamtzeilen:", gesamt)