class Human():
    def __init__(self, typ):
        self.size = 1.70
        self.ort = "deutschland"
        self.farbe = "rod"
        self.typ = typ

    def human(self):
        return f"größe: {self.size},\nwohnort: {self.ort },\nfarbe: {self.farbe},\ntyp: {self.typ}"




human = Human("amerikaner")
human.size = 2.0
human.ort = "berlin"

print(human.human())