"""Correcciones autorizadas al texto del protocolo.

Es la ÚNICA excepción a la regla «el texto se copia tal cual del documento».
Cada corrección se aplica igual en generar_contenido.py y en verificar.py, y ambos fallan
si una corrección deja de encontrarse en el documento (para que nunca se pierda en silencio).
Solo se añaden correcciones pedidas expresamente por el responsable del proyecto.

Formato: (texto en el documento, texto en la app, quién la pidió y cuándo)
"""
CORRECCIONES = [
    ('Laboratorio practico', 'Laboratorio práctico', 'Marco Stiehl, 2026-11-11 (falta la tilde)'),
]

def aplicar(texto, usadas=None):
    """Aplica las correcciones a un texto. Si se pasa `usadas` (dict), cuenta cada una."""
    for antes, despues, _ in CORRECCIONES:
        n = texto.count(antes)
        if n:
            texto = texto.replace(antes, despues)
            if usadas is not None: usadas[antes] = usadas.get(antes, 0) + n
    return texto

def comprobar(usadas):
    """Devuelve la lista de correcciones que no se encontraron en el documento."""
    return [antes for antes, _, _ in CORRECCIONES if not usadas.get(antes)]


# Imágenes que la app muestra en otro sitio (el texto no cambia; solo dónde aparece la imagen).
# Formato: (imagen, id de la sección de destino, posición dentro de esa sección, quién lo pidió y cuándo)
REUBICACIONES = [
    ('img/image3.png', 'moca-guia-de-practica-y-revision-de-la-copia', 0,
     'Marco Stiehl, 2026-11-11 (la hoja del MoCA, al final de la sección anterior en el documento, pasa al inicio de su guía)'),
]

def reubicar(secciones):
    """Mueve las imágenes de REUBICACIONES. Devuelve las que no se pudieron mover."""
    fallos = []
    for src, destino, pos, _ in REUBICACIONES:
        dst = next((s for s in secciones if s['id'] == destino), None)
        org = next((s for s in secciones for b in s['bloques'] if b.get('tipo') == 'img' and b.get('src') == src), None)
        if dst is None or org is None: fallos.append(src); continue
        bloque = next(b for b in org['bloques'] if b.get('tipo') == 'img' and b.get('src') == src)
        org['bloques'].remove(bloque)
        dst['bloques'].insert(pos, bloque)
    return fallos
