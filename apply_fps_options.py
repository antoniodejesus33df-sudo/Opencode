#!/usr/bin/env python3
"""Aplica los ajustes de options.txt del pack sin borrar teclas ni datos del usuario.

Uso:
    python3 apply_fps_options.py [ruta/a/options.txt]

Si no se indica ruta, detecta .minecraft/options.txt segun el sistema operativo.
Se crea una copia de seguridad con extension .bak antes de modificar nada.
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "options.txt"

# Estos se copian tal cual; 'version' se respeta del archivo destino.
OVERRIDE = {}
for line in SOURCE.read_text(encoding="utf-8").splitlines():
    if ":" in line and not line.startswith("version:"):
        key, value = line.split(":", 1)
        OVERRIDE[key.strip()] = value.strip()


def default_target():
    if sys.platform == "win32":
        return Path.home() / "AppData" / "Roaming" / ".minecraft" / "options.txt"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "minecraft" / "options.txt"
    return Path.home() / ".minecraft" / "options.txt"


def main():
    target = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else default_target()
    if not target.exists():
        print(f"No existe {target}. Inicia Minecraft una vez y vuelve a ejecutar este script.")
        return 1
    shutil.copy2(target, target.with_suffix(target.suffix + ".bak"))

    lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    seen = set()
    out = []
    for line in lines:
        if ":" in line:
            key = line.split(":", 1)[0].strip()
            if key in OVERRIDE:
                out.append(f"{key}:{OVERRIDE[key]}")
                seen.add(key)
                continue
        out.append(line)
    for key, value in OVERRIDE.items():
        if key not in seen:
            out.append(f"{key}:{value}")

    target.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Aplicados {len(OVERRIDE)} ajustes de FPS a {target}")
    print(f"Copia de seguridad: {target}.bak")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
