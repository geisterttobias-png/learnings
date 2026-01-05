import datetime # aktuelles Datum erhalten
import os  # Betriebssystemfunktionen
import platform  # Betriebssystem erkennen
import subprocess  # zum Öffnen der Datei mit Systemaufruf

print(" --- Maschine anlegen ---   ")

maschine = input("Maschinenname eingeben: ")  # Maschinenname eingeben
ort = input("Ort der Maschine eingeben: ")  # Ort der Maschine eingeben
bereich = input("Bereich der Maschine eingeben: ")  # Bereich der Maschine eingeben5

date = datetime.datetime.now()  # aktuelles Datum

erstellt = date.strftime("%d.%m.%Y")  # Datum als String im Format TT.MM.JJJJ

speicher_zeile = f"{maschine},{ort},{bereich},{erstellt}\n"  # Zeile zum Speichern vorbereiten

with open("maschinen.csv", "a") as datei:  # Datei im Anhangsmodus öffnen
    datei.write(speicher_zeile)  # Zeile in die Datei schreiben

print("Maschine wurde erfolgreich angelegt.")
print("Datei öffnen und überprüfen?")

answer = input("Ja (j) / Nein (n): ").lower()


def open_file(path: str) -> None:
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":
            subprocess.run(["open", path], check=True)
        else:
            subprocess.run(["xdg-open", path], check=True)
    except Exception as e:
        print(f"Datei konnte nicht geöffnet werden: {e}. Bitte manuell öffnen.")


if answer == "j":
    open_file("maschinen.csv")
else:
    print("Das Skript kann geschlossen werden.")
