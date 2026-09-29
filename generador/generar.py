#!/usr/bin/env python3
"""Generador de muestras NIMBRA.

Arma cada web a partir de `clientes/<slug>/datos.json` + `clientes/<slug>/fotos/`
y la plantilla `generador/plantilla.html`. También arma el portafolio (`index.html`).

Uso:
  python3 generador/generar.py                 # genera todas las muestras + portafolio
  python3 generador/generar.py veoveo samba    # genera solo esas (y el portafolio)
  python3 generador/generar.py --nueva lagranja --desde samba
                                               # crea clientes/lagranja/ para completar
  python3 generador/generar.py --variantes     # lista las combinaciones de diseño en uso

Solo usa la librería estándar de Python 3.
"""
import argparse
import base64
import html
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
GEN = RAIZ / "generador"
CLIENTES = RAIZ / "clientes"

ORDEN_BASE = ["espacio", "incluye", "fecha", "donde"]

# ---------------------------------------------------------------- tipografías
# Cada combinación: fuente de títulos + fuente de texto (archivos en generador/fuentes/).
FUENTES = {
    "bricolage-host": {
        "desc": "Moderna y amigable (la original)",
        "titulos": ("Bricolage Grotesque", "bricolage-grotesque.woff2", "400 800", "sans-serif"),
        "texto": ("Host Grotesk", "host-grotesk.woff2", "400 700"),
        "extra": "",
    },
    "fraunces-dmsans": {
        "desc": "Serif cálida, ideal chacras y quintas",
        "titulos": ("Fraunces", "fraunces.woff2", "400 800", "serif"),
        "texto": ("DM Sans", "dm-sans.woff2", "400 700"),
        "extra": "h1,h2{letter-spacing:-.025em;font-weight:650}",
    },
    "playfair-inter": {
        "desc": "Elegante clásica, bodas y eventos de gala",
        "titulos": ("Playfair Display", "playfair-display.woff2", "400 800", "serif"),
        "texto": ("Inter", "inter.woff2", "400 700"),
        "extra": "h1,h2{letter-spacing:-.02em;font-weight:600}h1 em,h2 em{font-style:italic}",
    },
    "cormorant-manrope": {
        "desc": "Lujo editorial, estética y eventos premium",
        "titulos": ("Cormorant Garamond", "cormorant-garamond.woff2", "400 700", "serif"),
        "texto": ("Manrope", "manrope.woff2", "400 700"),
        "extra": "h1,h2{letter-spacing:-.01em;font-weight:600;line-height:1}"
                 "h1{font-size:clamp(50px,8.4vw,120px)}h2{font-size:clamp(38px,5.2vw,68px)}h1 em{font-style:italic}",
    },
    "syne-outfit": {
        "desc": "Audaz y actual, salones juveniles y fiestas",
        "titulos": ("Syne", "syne.woff2", "400 800", "sans-serif"),
        "texto": ("Outfit", "outfit.woff2", "400 700"),
        "extra": "h1,h2{letter-spacing:-.03em;font-weight:700}",
    },
    "baloo-nunito": {
        "desc": "Redondeada y divertida, cumples infantiles",
        "titulos": ("Baloo 2", "baloo-2.woff2", "400 800", "sans-serif"),
        "texto": ("Nunito", "nunito.woff2", "400 700"),
        "extra": "h1,h2{letter-spacing:-.02em;font-weight:800;line-height:.95}",
    },
}

# ---------------------------------------------------------------- portada
PORTADAS = {
    "completa": ("Foto a pantalla completa con el texto abajo (la original)", ""),
    "centrada": ("Foto a pantalla completa con el texto centrado", """
.hero{align-items:center;text-align:center}
.hero:after{background:linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,.35) 45%,rgba(0,0,0,.7))}
.hero .wrap{padding:120px 0 80px;display:flex;flex-direction:column;align-items:center}
.hero h1{margin-inline:auto;max-width:16ch}
.hero .lead{margin-inline:auto}
.hero .ctas{justify-content:center}"""),
    "dividida": ("Texto a la izquierda y foto a la derecha", """
header{position:relative;color:var(--ink);background:var(--card)}
header .btn.light{background:var(--accent);color:var(--on-accent)}
.hero{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);align-items:center;min-height:min(84vh,760px);color:var(--ink);background:var(--card)}
.hero:after{display:none}
.hero img{position:relative;inset:auto;grid-column:2;grid-row:1;height:100%;min-height:520px;animation:none;transform:none}
.hero .wrap{grid-column:1;grid-row:1;width:auto;margin:0;padding:56px clamp(24px,4vw,56px) 64px max(16px,calc((100vw - 1200px)/2))}
.hero .stars{background:var(--bg);border-color:var(--line);backdrop-filter:none}
.hero h1{font-size:clamp(40px,5.6vw,84px)}
.hero h1 em{color:var(--accent-ink)}
.hero .btn.light{background:var(--bg);color:var(--ink);border:1.5px solid var(--line)}
@media(max-width:860px){.hero{grid-template-columns:1fr;min-height:0}.hero img{grid-column:1;grid-row:1;min-height:0;height:52vh}.hero .wrap{grid-row:2;padding:36px 16px 56px}}"""),
    "enmarcada": ("Foto con bordes redondeados dentro de la página", """
header{position:relative;color:var(--ink)}
header .btn.light{background:var(--accent);color:var(--on-accent)}
.hero{width:min(1240px,100% - 24px);margin:0 auto;border-radius:32px;min-height:min(80vh,740px)}
.hero .wrap{width:auto;margin:0;padding:0 clamp(24px,5vw,64px) clamp(32px,5vw,64px)}
@media(max-width:860px){.hero{border-radius:22px;min-height:78vh}}"""),
}

# ---------------------------------------------------------------- galería
GALERIAS = {
    "mosaico": ("Mosaico con una foto grande (la original)", ""),
    "grilla": ("Grilla pareja de 3 columnas", """
.gal{grid-template-columns:repeat(3,1fr);grid-auto-rows:auto}
.gal figure:nth-child(n){grid-column:auto;grid-row:auto;aspect-ratio:4/3}
@media(max-width:860px){.gal{grid-template-columns:1fr 1fr;grid-auto-rows:auto}.gal figure:nth-child(n){grid-column:auto;grid-row:auto}}"""),
    "carrusel": ("Carrusel horizontal que se desliza", """
.gal{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;gap:14px;padding-bottom:10px;scrollbar-width:thin}
.gal figure:nth-child(n){flex:0 0 min(78%,520px);height:clamp(300px,42vw,520px);scroll-snap-align:start}"""),
    "columnas": ("Tres columnas con fotos altas y bajas", """
.gal{grid-template-columns:repeat(3,1fr);grid-auto-rows:80px}
.gal figure:nth-child(1){grid-column:1;grid-row:1/span 5}
.gal figure:nth-child(2){grid-column:1;grid-row:6/span 3}
.gal figure:nth-child(3){grid-column:2;grid-row:1/span 3}
.gal figure:nth-child(4){grid-column:2;grid-row:4/span 5}
.gal figure:nth-child(5){grid-column:3;grid-row:1/span 4}
.gal figure:nth-child(6){grid-column:3;grid-row:5/span 4}
@media(max-width:860px){.gal{grid-auto-rows:56px;gap:8px}.gal figure:nth-child(1){grid-column:1;grid-row:1/span 5}.gal figure:nth-child(2){grid-column:1;grid-row:6/span 3}.gal figure:nth-child(3){grid-column:2;grid-row:1/span 3}.gal figure:nth-child(4){grid-column:2;grid-row:4/span 5}.gal figure:nth-child(5){grid-column:3;grid-row:1/span 4}.gal figure:nth-child(6){grid-column:3;grid-row:5/span 4}}"""),
}

VARIANTES_BASE = {"portada": "completa", "galeria": "mosaico", "fuentes": "bricolage-host", "orden": ORDEN_BASE}

MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}


def data_uri(ruta: Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(ruta.read_bytes()).decode()


def foto(carpeta: Path, nombre: str) -> Path:
    for ext in MIME:
        p = carpeta / f"{nombre}{ext}"
        if p.exists():
            return p
    sys.exit(f"Falta la foto '{nombre}' en {carpeta} (jpg, png o webp)")


def fotos_galeria(carpeta: Path) -> list:
    fotos = [p for p in carpeta.iterdir() if re.fullmatch(r"galeria-\d+\.(jpe?g|png|webp)", p.name)]
    fotos.sort(key=lambda p: int(re.search(r"\d+", p.name).group()))
    if not fotos:
        sys.exit(f"No hay fotos galeria-1.jpg, galeria-2.jpg... en {carpeta}")
    return fotos


def variantes(datos: dict) -> dict:
    v = {**VARIANTES_BASE, **datos.get("variantes", {})}
    for clave, opciones in (("portada", PORTADAS), ("galeria", GALERIAS), ("fuentes", FUENTES)):
        if v[clave] not in opciones:
            sys.exit(f"Variante {clave}='{v[clave]}' no existe. Opciones: {', '.join(opciones)}")
    if sorted(v["orden"]) != sorted(ORDEN_BASE):
        sys.exit(f"'orden' tiene que tener exactamente: {', '.join(ORDEN_BASE)}")
    return v


def css_variantes(v: dict) -> str:
    css = PORTADAS[v["portada"]][1] + GALERIAS[v["galeria"]][1]
    if v["fuentes"] != "bricolage-host":
        f = FUENTES[v["fuentes"]]
        tit, txt = f["titulos"], f["texto"]
        css += (f'\nbody{{font-family:"{txt[0]}",system-ui,sans-serif}}'
                f'\n.brand,h1,h2,.list span,.loc h3{{font-family:"{tit[0]}",{tit[3]}}}')
        if f["extra"]:
            css += "\n" + f["extra"]
    return css.lstrip("\n") + ("\n" if css else "")


def ordenar_secciones(texto: str, orden: list) -> str:
    inicio = texto.index("<!--seccion-->")
    fin = texto.index("<!--fin-secciones-->\n")
    bloques = texto[inicio:fin].split("<!--seccion-->\n")[1:]
    por_id = {re.match(r'<section id="(\w+)"', b).group(1): b for b in bloques}
    if orden != ORDEN_BASE:
        # la primera sección lleva el espacio superior completo; las demás van pegadas
        for nombre, b in por_id.items():
            b = b.replace(' style="padding-top:0"', "", 1)
            if nombre != orden[0]:
                b = b.replace(f'<section id="{nombre}"', f'<section id="{nombre}" style="padding-top:0"', 1)
            por_id[nombre] = b
    return texto[:inicio] + "".join(por_id[n] for n in orden) + texto[fin + len("<!--fin-secciones-->\n"):]


def generar(slug: str) -> Path:
    carpeta = CLIENTES / slug
    datos = json.loads((carpeta / "datos.json").read_text(encoding="utf-8"))
    fotos = carpeta / "fotos"
    v = variantes(datos)
    fuente = FUENTES[v["fuentes"]]
    publicada = datos.get("publicada", False)
    textos = datos["textos"]

    valores = dict(textos)
    borrar = "\x00borrar\x00"  # marca de línea a eliminar
    valores["meta_robots"] = borrar if publicada else '<meta name="robots" content="noindex">'
    valores["aviso_muestra"] = borrar if publicada else (
        f'<div class="pv"><b>Muestra hecha por NIMBRA</b> para {textos["nombre_muestra"]} · todavía no está publicada</div>')
    valores["fuente_base_titulos"] = data_uri(GEN / "fuentes" / fuente["titulos"][1], "font/woff2")
    valores["fuente_base_texto"] = data_uri(GEN / "fuentes" / fuente["texto"][1], "font/woff2")
    portada = foto(fotos, "portada")
    avatar = foto(fotos, "avatar")
    valores["img_portada"] = data_uri(portada, MIME[portada.suffix.lower()])
    valores["img_avatar"] = data_uri(avatar, MIME[avatar.suffix.lower()])
    for k, c in datos["colores"].items():
        valores["c_" + k.replace("-", "_")] = c
    valores["css_variantes"] = css_variantes(v)

    # datos del asistente: la galería va justo después de "tags"
    galeria = [data_uri(p, MIME[p.suffix.lower()]) for p in fotos_galeria(fotos)]
    asistente = {}
    for k, val in datos["asistente"].items():
        asistente[k] = val
        if k == "tags":
            asistente["gal"] = galeria
    asistente.setdefault("gal", galeria)
    valores["asistente"] = json.dumps(asistente, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    plantilla = (GEN / "plantilla.html").read_text(encoding="utf-8")
    plantilla = plantilla.replace('font-family:"Bricolage Grotesque";src:url({{fuente_base_titulos}}) format("woff2");font-weight:400 800',
                                  f'font-family:"{fuente["titulos"][0]}";src:url({{{{fuente_base_titulos}}}}) format("woff2");font-weight:{fuente["titulos"][2]}')
    plantilla = plantilla.replace('font-family:"Host Grotesk";src:url({{fuente_base_texto}}) format("woff2");font-weight:400 700',
                                  f'font-family:"{fuente["texto"][0]}";src:url({{{{fuente_base_texto}}}}) format("woff2");font-weight:{fuente["texto"][2]}')
    plantilla = ordenar_secciones(plantilla, v["orden"])

    faltan = set(re.findall(r"{{(\w+)}}", plantilla)) - set(valores)
    if faltan:
        sys.exit(f"{slug}: faltan textos en datos.json: {', '.join(sorted(faltan))}")
    salida = re.sub(r"{{(\w+)}}", lambda m: valores[m.group(1)], plantilla)
    salida = salida.replace(borrar + "\n", "")
    destino = RAIZ / f"{slug}.html"
    destino.write_text(salida, encoding="utf-8")
    return destino


# ---------------------------------------------------------------- portafolio
def portafolio(slugs: list) -> Path:
    tarjetas = []
    for slug in slugs:
        d = json.loads((CLIENTES / slug / "datos.json").read_text(encoding="utf-8"))
        p = d.get("portafolio", {})
        portada = foto(CLIENTES / slug / "fotos", "portada")
        texto_plano = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s))
        tarjetas.append({
            "slug": slug,
            "nombre": texto_plano(d["textos"]["marca"]),
            "categoria": p.get("categoria", "Otros rubros"),
            "rubro": p.get("rubro", ""),
            "ciudad": p.get("ciudad", ""),
            "pais": p.get("pais", ""),
            "titular": texto_plano(d["textos"]["titular"]),
            "resenas": texto_plano(d["textos"]["resenas"]),
            "foto": portada.relative_to(RAIZ).as_posix(),
            "acento": d["colores"]["accent"],
            "fondo": d["colores"]["bg"],
            "tinta": d["colores"]["ink"],
            "publicada": d.get("publicada", False),
        })
    config = json.loads((GEN / "nimbra.json").read_text(encoding="utf-8"))
    t = (GEN / "portafolio.html").read_text(encoding="utf-8")
    t = t.replace("{{muestras}}", json.dumps(tarjetas, ensure_ascii=False).replace("</", "<\\/"))
    t = t.replace("{{config}}", json.dumps(config, ensure_ascii=False).replace("</", "<\\/"))
    destino = RAIZ / "index.html"
    destino.write_text(t, encoding="utf-8")
    return destino


def todos_los_clientes() -> list:
    return sorted(p.name for p in CLIENTES.iterdir() if (p / "datos.json").exists())


def clave_diseno(d: dict) -> tuple:
    v = variantes(d)
    return (v["portada"], v["galeria"], v["fuentes"], tuple(v["orden"]))


def avisar_repetidos(slugs: list) -> None:
    usados = {}
    for s in slugs:
        d = json.loads((CLIENTES / s / "datos.json").read_text(encoding="utf-8"))
        usados.setdefault((clave_diseno(d), d["colores"]["accent"].lower()), []).append(s)
    for grupo in usados.values():
        if len(grupo) > 1:
            print(f"  ! Mismo diseño y color en: {', '.join(grupo)} (cambiá alguna variante o los colores)")


def listar_variantes() -> None:
    slugs = todos_los_clientes()
    print("Opciones disponibles:")
    for nombre, opciones in (("portada", PORTADAS), ("galeria", GALERIAS)):
        print(f"  {nombre}: " + " | ".join(f"{k} ({d})" for k, (d, _) in opciones.items()))
    print("  fuentes: " + " | ".join(f"{k} ({f['desc']})" for k, f in FUENTES.items()))
    print(f"  orden: cualquier orden de {', '.join(ORDEN_BASE)}\n")
    print("En uso:")
    for s in slugs:
        d = json.loads((CLIENTES / s / "datos.json").read_text(encoding="utf-8"))
        p, g, f, o = clave_diseno(d)
        print(f"  {s:16} portada={p:10} galeria={g:9} fuentes={f:18} orden={'-'.join(o)}")
    avisar_repetidos(slugs)


def nueva(slug: str, desde: str) -> None:
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        sys.exit("El nombre tiene que ser en minúsculas, sin espacios ni tildes (ej: lagranja)")
    destino = CLIENTES / slug
    if destino.exists():
        sys.exit(f"Ya existe {destino}")
    base = json.loads((CLIENTES / desde / "datos.json").read_text(encoding="utf-8"))
    # elegir la combinación de portada/galería/fuentes menos usada
    uso = Counter()
    for s in todos_los_clientes():
        p, g, f, _ = clave_diseno(json.loads((CLIENTES / s / "datos.json").read_text(encoding="utf-8")))
        uso.update([("p", p), ("g", g), ("f", f)])
    elegir = lambda tipo, opciones: min(opciones, key=lambda k: (uso[(tipo, k)], list(opciones).index(k)))
    base["variantes"] = {"portada": elegir("p", PORTADAS), "galeria": elegir("g", GALERIAS),
                         "fuentes": elegir("f", FUENTES), "orden": ORDEN_BASE}
    base["publicada"] = False
    (destino / "fotos").mkdir(parents=True)
    (destino / "datos.json").write_text(json.dumps(base, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Creado {destino.relative_to(RAIZ)}/ a partir de '{desde}'. Falta:")
    print("  1. Editar datos.json: textos, colores, asistente (WhatsApp, preguntas) y portafolio.")
    print(f"     Variantes elegidas (las menos usadas): {base['variantes']}")
    print("  2. Poner en fotos/: portada.jpg, avatar.jpg y galeria-1.jpg ... galeria-6.jpg")
    print(f"  3. python3 generador/generar.py {slug}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Genera las muestras NIMBRA y el portafolio.")
    ap.add_argument("clientes", nargs="*", help="slugs a generar (por defecto, todos)")
    ap.add_argument("--nueva", metavar="SLUG", help="crea la carpeta de un cliente nuevo")
    ap.add_argument("--desde", default="veoveo", help="cliente a copiar como base para --nueva")
    ap.add_argument("--variantes", action="store_true", help="lista las variantes de diseño y cuáles se usan")
    a = ap.parse_args()
    if a.nueva:
        return nueva(a.nueva, a.desde)
    if a.variantes:
        return listar_variantes()
    todos = todos_los_clientes()
    for s in a.clientes or todos:
        if s not in todos:
            sys.exit(f"No existe clientes/{s}/datos.json")
        r = generar(s)
        print(f"  {r.name:22} {r.stat().st_size / 1e6:.1f} MB")
    portafolio(todos)
    print("  index.html (portafolio)")
    avisar_repetidos(todos)


if __name__ == "__main__":
    main()
