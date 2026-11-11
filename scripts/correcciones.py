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
