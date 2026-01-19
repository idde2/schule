import tkinter as tk

def process_input():
    input_text = entry.get()
    # Mock-Modell: einfache Reversal der Eingabe
    output_text = input_text[::-1]
    label.config(text=output_text)

# Hauptfenster
root = tk.Tk()
root.title("Modell-Interaktion")

# Eingabe-Box
entry = tk.Entry(root, width=50)
entry.pack(pady=10)

# Button
btn = tk.Button(root, text="Funktionieren", command=process_input)
btn.pack(pady=5)

# Ausgabe-Label
label = tk.Label(root, text="Ergebnis:", fg="blue")
label.pack()

# Start das Fenster
root.mainloop()
