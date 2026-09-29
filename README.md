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

Las 15 muestras que ya existen quedaron con el diseño original (`completa` / `mosaico` / `bricolage-host`), así se ven igual que las que ya se mandaron.

## Cuando un cliente compra

- Poner `"publicada": true` en su `datos.json` y regenerar: se quita el aviso "Muestra hecha por NIMBRA" y el bloqueo para Google (`noindex`).
- Si su web necesita cambios que la plantilla no permite, se copia el `.html` generado a otro lado y a partir de ahí se personaliza a mano: esa web ya no depende del generador.

## Portafolio

Completar `generador/nimbra.json` con el WhatsApp de NIMBRA (con código de país), Instagram y email, y regenerar: aparecen los botones de contacto. Si están vacíos, esos botones no se muestran.
