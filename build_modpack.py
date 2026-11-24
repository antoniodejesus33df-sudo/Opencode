#!/usr/bin/env python3
"""Genera un modpack Fabric de Minecraft 1.21.11 orientado a maximizar FPS.

Resuelve versiones compatibles desde la API de Modrinth, descarga los JAR,
verifica sus hashes SHA1/SHA512 y escribe modrinth.index.json + MANIFEST.json.
"""
import hashlib
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

GAME_VERSION = "1.21.11"
LOADER = "fabric"
FABRIC_LOADER = "0.20.1"
ROOT = Path(__file__).resolve().parent
MODS_DIR = ROOT / "mods"
OPTIONAL_DIR = ROOT / "optional"
API = "https://api.modrinth.com/v2"

# Pack minimo para FPS puro: solo optimizacion, sin UI extra ni perfiles.
# Cualquier mod que no aumente FPS activos se deja en optional/.
MAIN = [
    ("fabric-api", "API base requerida por otros mods"),
    ("sodium", "Motor de renderizado; el mayor salto de FPS"),
    ("lithium", "Optimizaciones de logica del juego"),
    ("entityculling", "No renderiza entidades fuera de pantalla"),
    ("moreculling", "Caras de bloques innecesarias sin renderizar"),
    ("cull-leaves", "Culling de hojas ocultas"),
    ("immediatelyfast", "Renderizado instantaneo de GUI y items"),
    ("noisiumforked", "Generacion de terreno mas rapida"),
    ("ferrite-core", "Menos memoria y menos pausas por GC"),
    ("badoptimizations", "Microoptimizaciones del motor"),
]
# Extras: comodidad/diagnostico/shaders. NO activar si el objetivo es max FPS.
OPTIONAL = [
    ("iris", "Shaders: baja mucho los FPS"),
    ("sodium-extra", "Opciones extra (ligero overhead)"),
    ("reeses-sodium-options", "Panel de opciones (solo UI)"),
    ("spark", "Profiler (solo diagnostico)"),
    ("krypton", "Red: solo util en multijugador"),
    ("dynamic-fps", "Baja FPS en segundo plano, no los aumenta"),
    ("fps-reducer", "Alternativa a dynamic-fps"),
    ("c2me-fabric", "Chunks concurrentes: experimental"),
]

FILTER = urllib.parse.urlencode({
    "loaders": json.dumps([LOADER]),
    "game_versions": json.dumps([GAME_VERSION]),
})


def get_json(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "fps-boost-modpack-builder/1.0"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(1.5 * (i + 1))


def resolve(slug):
    """Devuelve la version release mas reciente compatible."""
    versions = get_json(f"{API}/project/{slug}/version?{FILTER}")
    if not versions:
        raise RuntimeError(f"{slug}: sin version para {GAME_VERSION}/{LOADER}")
    versions.sort(key=lambda v: v["date_published"], reverse=True)
    release = [v for v in versions if v["version_type"] == "release"]
    return (release or versions)[0]


def sha(path, algo):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(version, dest_dir):
    file = next((f for f in version["files"] if f.get("primary")), version["files"][0])
    dest = dest_dir / file["filename"]
    if not dest.exists() or dest.stat().st_size != file["size"]:
        print(f"  descargando {file['filename']} ({file['size']} B)")
        req = urllib.request.Request(file["url"], headers={"User-Agent": "fps-boost-modpack-builder/1.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as out:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                out.write(chunk)
    h1, h512 = sha(dest, "sha1"), sha(dest, "sha512")
    expected = file["hashes"]
    if h1 != expected.get("sha1") or h512 != expected.get("sha512"):
        dest.unlink(missing_ok=True)
        raise RuntimeError(f"Hash incorrecto para {file['filename']}")
    return {
        "path": f"{dest_dir.name}/{dest.name}",
        "hashes": {"sha1": h1, "sha512": h512},
        "env": {"client": "required", "server": "unsupported"},
        "downloads": [file["url"]],
        "fileSize": file["size"],
    }, version


def main():
    MODS_DIR.mkdir(exist_ok=True)
    OPTIONAL_DIR.mkdir(exist_ok=True)
    # Limpieza de JARs de una compilacion anterior (el pack es reproducible).
    for d in (MODS_DIR, OPTIONAL_DIR):
        for old in d.glob("*.jar"):
            old.unlink()
    files, manifest, done = [], [], set()

    def add(slug, dest_dir, reason, depth=0):
        if slug in done:
            return
        done.add(slug)
        v = resolve(slug)
        entry, v = download(v, dest_dir)
        info = get_json(f"{API}/project/{slug}")
        print(f"  {slug:26s} {v['version_number']}")
        manifest.append({
            "slug": info.get("slug", slug),
            "name": info["title"],
            "version": v["version_number"],
            "version_type": v["version_type"],
            "file": entry["path"],
            "sha512": entry["hashes"]["sha512"],
            "source": info.get("source_url") or f"https://modrinth.com/mod/{slug}",
            "reason": reason,
            "optional": dest_dir == OPTIONAL_DIR,
        })
        if dest_dir == MODS_DIR:
            files.append(entry)
        # Dependencias obligatorias (ej. MidnightLib para Cull Leaves)
        for dep in v.get("dependencies", []):
            dep_slug = dep.get("project_id")
            if not dep_slug or dep["dependency_type"] != "required":
                continue
            if dep_slug in ("P7dR8mSH", "AANobbMI", "fabric-api", "sodium"):
                continue
            try:
                add(dep_slug, dest_dir, f"dependencia obligatoria de {slug}", depth + 1)
            except Exception as e:
                print(f"  AVISO: dependencia {dep_slug} no resuelta: {e}")

    print("Mods principales:")
    for slug, reason in MAIN:
        add(slug, MODS_DIR, reason)
    print("Extras opcionales:")
    for slug, reason in OPTIONAL:
        add(slug, OPTIONAL_DIR, reason)

    index = {
        "formatVersion": 1,
        "game": "minecraft",
        "versionId": GAME_VERSION,
        "name": "FPS Boost 1.21.11",
        "summary": "Modpack 100% orientado a maximizar FPS (Fabric)",
        "files": files,
        "dependencies": {"minecraft": GAME_VERSION, "fabric-loader": FABRIC_LOADER},
    }
    (ROOT / "modrinth.index.json").write_text(json.dumps(index, indent=2) + "\n")
    (ROOT / "MANIFEST.json").write_text(json.dumps({
        "game": GAME_VERSION,
        "loader": LOADER,
        "fabric_loader": FABRIC_LOADER,
        "mods": manifest,
    }, indent=2, ensure_ascii=False) + "\n")
    print(f"\nListo: {len(files)} mods principales, {len(manifest) - len(files)} opcionales/dependencias")


if __name__ == "__main__":
    main()
