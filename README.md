# FPS Boost 1.21.11 — rendimiento puro

Modpack de **Minecraft Java 1.21.11 (Fabric)** con un único objetivo: **el mayor número de FPS posible**. Cero contenido nuevo, cero shaders, cero mods de interfaz innecesarios. Solo optimización.

> Versiones resueltas desde la API de Modrinth el **2026-11-24**. JARs con SHA-1/SHA-512 verificados en `MANIFEST.json`.

## Qué incluye (12 JARs)

| Mod | Versión | Función |
|---|---|---|
| Fabric API | 0.141.6+1.21.11 | Base necesaria |
| Sodium | 0.8.14 | Sustituye el renderizador (el mayor salto) |
| Lithium | 0.21.4 | Optimiza lógica, IA y físicas |
| Entity Culling | 1.12.2 | No dibuja entidades fuera de vista |
| More Culling | 1.6.2 | No dibuja caras de bloques ocultas |
| Cloth Config | 21.11.153 | Dependencia de More Culling |
| Cull Leaves | 4.1.1.1 | Culling de hojas |
| MidnightLib | 1.10.0 | Dependencia de Cull Leaves |
| ImmediatelyFast | 1.14.3 | Acelera GUI, inventarios y tooltips |
| NoisiumForked | 2.8.3 | Generación de terreno más rápida |
| FerriteCore | 8.2.0 | Menos RAM y menos pausas por GC |
| BadOptimizations | 2.4.1 | Microoptimizaciones del motor |

**Deliberadamente NO incluidos:** Iris (los shaders destruyen los FPS), Sodium Extra y Reese's Options (UI extra), spark (profiler), Krypton (solo red), Dynamic FPS/FPS Reducer (bajan FPS en segundo plano, no los suben), C2ME (experimental). El ZIP del Release es la versión compacta: solo los 12 JARs esenciales. Si necesitas algun extra, descárgalo de Modrinth e inclúyelo en `mods/`; el repositorio guarda los nombres y versiones en `MANIFEST.json`.

## Instalación

### Descarga directa / ZIP
1. Descarga `fps-boost-1.21.11.zip`.
2. Instala **Fabric Loader 0.20.1** para 1.21.11: https://fabricmc.net/use/installer/
3. Copia el contenido de `mods/` en `.minecraft/mods`.
4. Copia `options.txt` en `.minecraft/` (o, para **no perder tus teclas ni ajustes**, ejecuta `python3 apply_fps_options.py`, que parchea tu archivo actual y hace copia `.bak`).
5. Inicia el juego.

### Modrinth App
Arrastra `modrinth.index.json` (o el ZIP) a la Modrinth App. Instala Fabric 0.20.1 y los 12 JARs automáticamente. Los ajustes de `options.txt` debes aplicarlos aparte con el script.

## Ajustes de `options.txt` aplicados

`maxFps:260` (en 1.21.11 ese valor equivale a **sin límite**), `enableVsync:false`, `graphicsPreset:fast`, `renderDistance:8`, `simulationDistance:5`, `entityDistanceScaling:0.5`, `renderClouds:false`, `particles:2` (mínimas), `ao:false`, `mipmapLevels:0`, `textureFiltering:0`, `improvedTransparency:false`, `chunkSectionFadeInTime:0.0`, `weatherRadius:3`, efectos de cámara y viñeta desactivados.

Si quieres más margen, baja `renderDistance` a **6** y `simulationDistance` a **5**. El render distance es, con diferencia, el ajuste que más FPS cuesta.

## Argumentos JVM recomendados (8 GB de RAM)

```
-Xms4G -Xmx4G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1
```

Ajusta `-Xms`/`-Xmx` a la mitad de tu RAM física. No asignes toda la memoria al juego.

## Sobre los 500 FPS — honestidad técnica

**Ningún modpack garantiza 500 FPS**: el límite lo pone tu CPU (single-thread), GPU, resolución y escena. Este pack elimina el techo artificial de FPS y todo el overhead evitable, pero para acercarse a 500 FPS necesitas, como mínimo:

- CPU con muy buen rendimiento por núcleo (el motor del juego sigue siendo mayormente single-thread).
- GPU dedicada moderna y **resolución baja** (720p/1080p; 4K multiplica el coste por píxel).
- Render distance **6–8**, sin shaders, sin resource packs pesadas y VSync desactivada.
- Monitor de alta tasa de refresco (si el monitor va a 60 Hz, el SO limitará la experiencia útil).

Mide con F3 o activa el contador de percentiles de Sodium (p50/p98) para ver FPS reales, no solo la media. Si no llegas a 500, lo normal es que el cuello esté en la CPU o en la resolución, no en los mods.

## Solución de problemas

- **Falta `cloth-config` o `midnightlib`** → cópialos también desde `mods/` (ya vienen).
- **Crash al arrancar** → usa exactamente MC 1.21.11 + Fabric Loader 0.20.1 (no 1.21.10 ni 26.x).
- **Pocos FPS al explorar** → baja render/simulation distance; no es culpa de los mods.
- **Quieres diagnosticar** → copia `optional/spark-*.jar` a `mods/`, usa `/spark profiler`, y vuelve a quitarlo.

## Reconstruir

```bash
python3 build_modpack.py
zip -r fps-boost-1.21.11.zip mods optional modrinth.index.json MANIFEST.json README.md options.txt apply_fps_options.py build_modpack.py
```

Los mods pertenecen a sus autores (enlaces en `MANIFEST.json`). Este repo distribuye únicamente la selección y la configuración.
