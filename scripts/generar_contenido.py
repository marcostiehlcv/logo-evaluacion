"""Genera contenido.js e img/ a partir de «Protocolo de evaluación.docx».

El texto se copia tal cual del documento (sin correcciones ni cambios).
Uso:  python scripts/generar_contenido.py
Solo usa la biblioteca estándar de Python 3.
"""
import json, re, shutil, sys, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DOCX = RAIZ / 'Protocolo de evaluación.docx'
SALIDA = RAIZ / 'contenido.js'
IMG = RAIZ / 'img'

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
def q(t, ns=W): return '{%s}%s' % (ns, t)

def on(el):
    return el is not None and el.get(q('val')) not in ('0', 'false', 'none')

def main():
    z = zipfile.ZipFile(DOCX)
    doc = ET.fromstring(z.read('word/document.xml'))
    rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('word/_rels/document.xml.rels'))}
    estilos = {}
    for s in ET.fromstring(z.read('word/styles.xml')).iter(q('style')):
        n = s.find(q('name'))
        estilos[s.get(q('styleId'))] = (n.get(q('val')) if n is not None else '').lower()

    imagenes = {}  # destino en el docx -> nombre publicado

    def runs_de(p):
        """Devuelve (runs, imagenes) de un párrafo. run = [texto, negrita, cursiva]."""
        out, imgs = [], []
        for r in p.iter(q('r')):
            rpr = r.find(q('rPr'))
            b = on(rpr.find(q('b'))) if rpr is not None else False
            i = on(rpr.find(q('i'))) if rpr is not None else False
            t = []
            for ch in r:
                if ch.tag == q('t'): t.append(ch.text or '')
                elif ch.tag == q('tab'): t.append('\t')
                elif ch.tag in (q('br'), q('cr')):
                    if ch.get(q('type')) != 'page': t.append('\n')
                elif ch.tag == q('noBreakHyphen'): t.append('‑')
                elif ch.tag == q('drawing'):
                    for bl in ch.iter(q('blip', A)):
                        destino = rels[bl.get(q('embed', R))]
                        dp = next(ch.iter(q('docPr', WP)), None)
                        alt = (dp.get('descr') or dp.get('title') or '') if dp is not None else ''
                        imgs.append({'src': destino, 'alt': alt})
                elif ch.tag == q('sym') or ch.tag.endswith('}pict') or ch.tag == q('object'):
                    sys.exit('Elemento no soportado en el documento: %s' % ch.tag)
            texto = ''.join(t)
            if not texto: continue
            if out and out[-1][1] == b and out[-1][2] == i:
                out[-1][0] += texto
            else:
                out.append([texto, b, i])
        return out, imgs

    def info_parrafo(p):
        ppr = p.find(q('pPr'))
        estilo, salto, lista, centrado = '', False, False, False
        if ppr is not None:
            ps = ppr.find(q('pStyle'))
            if ps is not None: estilo = estilos.get(ps.get(q('val')), '')
            salto = on(ppr.find(q('pageBreakBefore'))) if ppr.find(q('pageBreakBefore')) is not None else False
            lista = ppr.find(q('numPr')) is not None
            jc = ppr.find(q('jc'))
            centrado = jc is not None and jc.get(q('val')) == 'center'
        if any(br.get(q('type')) == 'page' for br in p.iter(q('br'))): salto = True
        return estilo, salto, lista, centrado

    secciones = [{'id': 'portada', 'titulo': None, 'bloques': []}]
    ids = set()

    def nueva_seccion(titulo):
        base = re.sub(r'[^a-z0-9]+', '-', titulo.lower()
                      .translate(str.maketrans('áéíóúüñ', 'aeiouun'))).strip('-') or 'seccion'
        sid, n = base, 2
        while sid in ids: sid, n = '%s-%d' % (base, n), n + 1
        ids.add(sid)
        secciones.append({'id': sid, 'titulo': titulo, 'bloques': []})

    def publicar(img):
        destino = img['src']
        if destino not in imagenes:
            imagenes[destino] = 'img/' + Path(destino).name
        return {'tipo': 'img', 'src': imagenes[destino], 'alt': img['alt']}

    def celda(tc):
        tcpr = tc.find(q('tcPr'))
        span = 1
        if tcpr is not None and tcpr.find(q('gridSpan')) is not None:
            span = int(tcpr.find(q('gridSpan')).get(q('val')))
        if tcpr is not None and tcpr.find(q('vMerge')) is not None:
            sys.exit('Celdas combinadas verticalmente no soportadas')
        parrafos = []
        for p in tc.findall(q('p')):
            runs, imgs = runs_de(p)
            if imgs: sys.exit('Imagen dentro de una tabla no soportada')
            parrafos.append(runs)
        return {'span': span, 'p': parrafos}

    for el in doc.find(q('body')):
        sec = secciones[-1]
        if el.tag == q('p'):
            estilo, salto, lista, centrado = info_parrafo(el)
            runs, imgs = runs_de(el)
            texto = ''.join(r[0] for r in runs)
            if estilo == 'heading 1':
                nueva_seccion(texto)
                continue
            if salto and sec['bloques']:
                sec['bloques'].append({'tipo': 'salto'})
            for img in imgs:
                sec['bloques'].append(publicar(img))
            if not texto.strip():
                continue
            b = {'tipo': 'h2' if estilo == 'heading 2' else 'p', 'runs': runs}
            if estilo and estilo not in ('heading 2', 'normal'): b['estilo'] = estilo
            if lista: b['lista'] = True
            if centrado: b['centrado'] = True
            sec['bloques'].append(b)
        elif el.tag == q('tbl'):
            filas = [[celda(tc) for tc in tr.findall(q('tc'))] for tr in el.findall(q('tr'))]
            sec['bloques'].append({'tipo': 'tabla', 'filas': filas})
        elif el.tag == q('sectPr'):
            pass
        else:
            sys.exit('Elemento no soportado en el cuerpo: %s' % el.tag)

    # Metadatos del documento
    core = ET.fromstring(z.read('docProps/core.xml'))
    meta = {c.tag.split('}')[1]: (c.text or '') for c in core}

    IMG.mkdir(exist_ok=True)
    for destino, nombre in imagenes.items():
        with z.open('word/' + destino) as src, open(RAIZ / nombre, 'wb') as dst:
            shutil.copyfileobj(src, dst)

    datos = {'documento': DOCX.name, 'modificado': meta.get('modified', ''), 'secciones': secciones}
    SALIDA.write_text(
        '// Generado automáticamente desde «%s» con scripts/generar_contenido.py.\n'
        '// No editar a mano: el texto debe coincidir exactamente con el protocolo.\n'
        'window.PROTOCOLO = %s;\n' % (DOCX.name, json.dumps(datos, ensure_ascii=False, separators=(',', ':'))),
        encoding='utf-8')
    print('%d secciones, %d imágenes -> %s' % (len(secciones), len(imagenes), SALIDA.name))

if __name__ == '__main__':
    main()
