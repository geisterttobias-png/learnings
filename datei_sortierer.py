import os
import shutil

# --- LINUX KONFIGURATION ---
# "~" ist die Abkürzung für dein Home-Verzeichnis (/home/deinuser)
base_path = os.path.expanduser("~/Downloads") 

# Wohin sollen die Sachen? 
# Wir erstellen die Ordner direkt im Downloads-Ordner, um es einfach zu halten.

ziel_ordner = {
    ".pdf": "Dokumente",
    ".docx": "Dokumente",
    ".odt": "Dokumente", # OpenOffice/LibreOffice Format
    ".txt": "Dokumente",
    ".jpg": "Bilder",
    ".jpeg": "Bilder",
    ".png": "Bilder",
    ".deb": "Software",  # Linux Installationsdateien
    ".AppImage": "Software",
    ".sh": "Scripte",
    ".zip": "Archive",
    ".gz": "Archive", # Typisches Linux Archiv-Format
    ".stl": "3D-Modelle",
    ".3mf": "3D-Modelle",
    ".iso": "Images",
}

# --- LOGIK (Bleibt gleich) ---

print(f"Räume auf in: {base_path}")

# Prüfen ob der Ordner existiert
if not os.path.exists(base_path):
    print("Fehler: Der Pfad existiert nicht!")
    exit()

for datei_name in os.listdir(base_path):
    original_pfad = os.path.join(base_path, datei_name)
    
    if os.path.isfile(original_pfad):
        # Wir holen die Endung und machen sie klein (.PDF -> .pdf)
        _, endung = os.path.splitext(datei_name)
        endung = endung.lower()
        
        # Sicherheitscheck: Das Skript soll sich nicht selbst verschieben!
        if datei_name == "datei_sortierer.py":
            continue

        if endung in ziel_ordner:
            ordner_name = ziel_ordner[endung]
            ziel_pfad_komplett = os.path.join(base_path, ordner_name)
            
            # Ordner erstellen, falls nicht existent
            if not os.path.exists(ziel_pfad_komplett):
                os.makedirs(ziel_pfad_komplett)
                print(f"Ordner erstellt: {ordner_name}")
            
            # Verschieben
            try:
                neuer_dateipfad = os.path.join(ziel_pfad_komplett, datei_name)
                shutil.move(original_pfad, neuer_dateipfad)
                print(f"Verschoben: {datei_name} -> {ordner_name}")
            except Exception as e:
                print(f"Fehler bei {datei_name}: {e}")

print("Fertig!")