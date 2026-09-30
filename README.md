# muestras
Webs de muestra de NIMBRA

- **`index.html`**: portafolio con todas las muestras (filtros por rubro y país, botón para ver la web y otro para ver el asistente en acción).
- **`<nombre>.html`**: cada muestra. Son archivos generados: **no se editan a mano**, se editan sus datos y se vuelven a generar.

## Cómo está armado

```
clientes/<nombre>/datos.json     textos, colores, diseño y datos del asistente
clientes/<nombre>/fotos/         portada.jpg, avatar.jpg, galeria-1.jpg … galeria-6.jpg
generador/plantilla.html         estructura común de todas las muestras
generador/portafolio.html        plantilla del portafolio
generador/nimbra.json            WhatsApp, Instagram y email de NIMBRA (para el portafolio)
generador/fuentes/               tipografías
generador/generar.py             el generador
```

Solo hace falta Python 3 (sin instalar nada).

## Uso

```bash
python3 generador/generar.py                      # regenera todas las muestras y el portafolio
python3 generador/generar.py samba veoveo         # solo esas
python3 generador/generar.py --variantes          # opciones de diseño y cuáles usa cada muestra
python3 generador/generar.py --nueva lagranja --desde samba   # crea un cliente nuevo
```

### Muestra nueva

1. `python3 generador/generar.py --nueva lagranja --desde samba` crea `clientes/lagranja/` copiando los textos de `samba` (conviene partir de una del mismo rubro y país, por el "vos"/"tú") y elige automáticamente la combinación de diseño **menos usada**.
2. Editar `clientes/lagranja/datos.json`: textos, colores, número de WhatsApp (`asistente.wa`, con código de país y sin `+`), preguntas frecuentes y los datos de `portafolio`.
3. Poner las fotos en `clientes/lagranja/fotos/`: `portada.jpg`, `avatar.jpg` y `galeria-1.jpg` … `galeria-6.jpg` (también sirven `.png` o `.webp`). Conviene que pesen menos de 300 KB cada una.
4. `python3 generador/generar.py lagranja` genera `lagranja.html` y actualiza el portafolio.

## Que cada web sea única

En `datos.json`, la parte `variantes` define el diseño:

| Opción | Valores |
|---|---|
| `portada` | `completa` (foto a pantalla completa, texto abajo) · `centrada` · `dividida` (texto a un lado, foto al otro) · `enmarcada` (foto con bordes redondeados) |
| `galeria` | `mosaico` · `grilla` · `carrusel` · `columnas` |
| `fuentes` | `bricolage-host` (moderna) · `fraunces-dmsans` (serif cálida) · `playfair-inter` (elegante) · `cormorant-manrope` (lujo) · `syne-outfit` (audaz) · `baloo-nunito` (infantil) |
| `orden` | el orden de las secciones: `espacio`, `incluye`, `fecha`, `donde` |

Sumadas a los colores (`colores`) y los textos, dan cientos de combinaciones. Al generar, avisa si dos muestras quedaron con el mismo diseño y el mismo color.

Cada una de las 15 muestras tiene una combinación distinta, elegida según su rubro (por ejemplo: tipografía redondeada para cumples infantiles y serif elegante para bodas y estética).

## Extras opcionales por cliente

### Videos
Poner los `.mp4` en `clientes/<nombre>/videos/` (con una foto `.jpg` del mismo nombre como portada, opcional) y agregar en `datos.json`:

```json
"videos": {"etiqueta": "En video", "titulo": "…", "texto": "…",
  "lista": [{"archivo": "video-1.mp4", "titulo": "Salón Tres Cruces", "detalle": "…", "vertical": true}]}
```

Aparecen debajo de la galería, se reproducen solos (sin sonido) al verlos y se abren a pantalla completa. Los videos **no** se incrustan en el `.html`: se suben junto con la web. Conviene que pesen menos de 2 MB (720p).

Las fotos de la galería también se abren a pantalla completa con flechas.

### Presupuestador privado
Si `datos.json` tiene `calculadora`, además se genera `<nombre>-presupuesto.html`: una calculadora donde el cliente elige salón, invitados, menú, horas y adicionales y ve el total al instante (con seña, precio por invitado, PDF y envío por WhatsApp). No está enlazada desde la web y tiene `noindex`: solo entra quien recibe el link. Ver `clientes/lacomarca/datos.json` como ejemplo (precios, recargos por día, mínimos y capacidad por salón).

## Cuando un cliente compra

- Poner `"publicada": true` en su `datos.json` y regenerar: se quita el aviso "Muestra hecha por NIMBRA" y el bloqueo para Google (`noindex`).
- Si su web necesita cambios que la plantilla no permite, se copia el `.html` generado a otro lado y a partir de ahí se personaliza a mano: esa web ya no depende del generador.

## Portafolio

Completar `generador/nimbra.json` con el WhatsApp de NIMBRA (con código de país), Instagram y email, y regenerar: aparecen los botones de contacto. Si están vacíos, esos botones no se muestran.
