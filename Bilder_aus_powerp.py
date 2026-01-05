#!/usr/bin/env python3
"""
Bilder_aus_powerp.py

Abhängigkeitfreie Variante: Extrahiert eingebettete Bilder aus einer .pptx-Datei
in Folienreihenfolge (slide order) und speichert sie durchnummeriert ab.

Beispiel:
    python Bilder_aus_powerp.py presentation.pptx -o bilder --pad 3

Optionen:
    --no-dedup    : keine Duplikate entfernen (standard: Duplikate entfernen)
    --pad N       : Anzahl Ziffern für die Nummerierung (default 3 -> 001.png)
    --fast        : schnelle Variante: kopiert alle Dateien aus ppt/media (keine Slide-Order)

Diese Version verwendet nur die Python-Standardbibliothek (kein python-pptx, kein Pillow).
"""

import zipfile
import xml.etree.ElementTree as ET
import os
import argparse
import hashlib
import imghdr
from pathlib import Path

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'pr': 'http://schemas.openxmlformats.org/package/2006/relationships',
}


def ext_from_blob(blob: bytes) -> str:
    ext = imghdr.what(None, h=blob)
    if ext == 'jpeg':
        ext = 'jpg'
    return ext or 'bin'


def slide_number_from_path(path: str) -> int:
    # Erwartet 'ppt/slides/slideN.xml'
    name = os.path.basename(path)
    digits = ''.join(ch for ch in name if ch.isdigit())
    try:
        return int(digits)
    except Exception:
        return 0


def extract_in_slide_order(pptx_path: str, outdir: str = 'exported_images', pad: int = 3, dedup: bool = True):
    z = zipfile.ZipFile(pptx_path, 'r')
    Path(outdir).mkdir(parents=True, exist_ok=True)
    seen = set()
    counter = 1

    # Finde alle slide XMLs und sortiere nach Slide-Nummer
    slides = [name for name in z.namelist() if name.startswith('ppt/slides/slide') and name.endswith('.xml')]
    slides.sort(key=slide_number_from_path)

    for slide_idx, slide_path in enumerate(slides, start=1):
        slide_xml = ET.fromstring(z.read(slide_path))
        # Suche alle blip Elemente (Bilder in DrawingML)
        for blip in slide_xml.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
            rid = blip.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
            if not rid:
                continue
            # Lade slide rels und finde Target für dieses rId
            rels_path = os.path.join(os.path.dirname(slide_path), '_rels', os.path.basename(slide_path) + '.rels')
            try:
                rels_xml = ET.fromstring(z.read(rels_path))
            except KeyError:
                continue
            target = None
            for rel in rels_xml.findall('.//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
                if rel.attrib.get('Id') == rid:
                    target = rel.attrib.get('Target')
                    break
            if not target:
                continue
            # Normiere Zielpfad
            target_path = os.path.normpath(os.path.join(os.path.dirname(rels_path), target)).replace('\\', '/')
            target_path = target_path.lstrip('./')
            # Versuche zu lesen
            possible_paths = [target_path]
            # fallback: wenn Target mit ../ startet, entferne und prefix 'ppt/'
            if target.startswith('../'):
                possible_paths.append('ppt/' + target.lstrip('../'))
            blob = None
            for p in possible_paths:
                try:
                    blob = z.read(p)
                    break
                except KeyError:
                    continue
            if blob is None:
                continue
            h = hashlib.sha1(blob).hexdigest()
            if dedup and h in seen:
                continue
            seen.add(h)
            ext = ext_from_blob(blob)
            filename = f"{counter:0{pad}d}.{ext}"
            with open(os.path.join(outdir, filename), 'wb') as outf:
                outf.write(blob)
            print(f"Exportiert: {filename} (Folie {slide_idx})")
            counter += 1

    print(f"Fertig: {counter-1} Bilder exportiert nach '{outdir}'")


def extract_fast_copy_media(pptx_path: str, outdir: str = 'exported_images', pad: int = 3, dedup: bool = True):
    # Schnelle Variante: kopiert alle Dateien aus ppt/media ohne Folienreihenfolge
    z = zipfile.ZipFile(pptx_path, 'r')
    Path(outdir).mkdir(parents=True, exist_ok=True)
    seen = set()
    counter = 1
    media_files = [name for name in z.namelist() if name.startswith('ppt/media/')]
    for med in sorted(media_files):
        blob = z.read(med)
        h = hashlib.sha1(blob).hexdigest()
        if dedup and h in seen:
            continue
        seen.add(h)
        ext = ext_from_blob(blob)
        filename = f"{counter:0{pad}d}.{ext}"
        with open(os.path.join(outdir, filename), 'wb') as f:
            f.write(blob)
        print(f"Kopiert: {filename} (Quelle: {med})")
        counter += 1
    print(f"Fertig: {counter-1} Bilder kopiert nach '{outdir}'")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Bilder aus PPTX exportieren (nur Stdlib)')
    parser.add_argument('pptx', help='Pfad zur .pptx Datei')
    parser.add_argument('-o', '--outdir', default='exported_images', help='Zielordner')
    parser.add_argument('--no-dedup', action='store_true', help='Duplikate nicht entfernen')
    parser.add_argument('--pad', type=int, default=3, help='Anzahl Stellen für Nummerierung')
    parser.add_argument('--fast', action='store_true', help='Schnelle Variante: kopiert ppt/media ohne Slide-Order')
    args = parser.parse_args()

    if not os.path.isfile(args.pptx):
        print(f"Datei nicht gefunden: {args.pptx}")
        raise SystemExit(1)

    if args.fast:
        extract_fast_copy_media(args.pptx, args.outdir, pad=args.pad, dedup=not args.no_dedup)
    else:
        extract_in_slide_order(args.pptx, args.outdir, pad=args.pad, dedup=not args.no_dedup)
