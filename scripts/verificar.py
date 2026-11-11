"""Comprueba que la app muestra exactamente el texto y las imágenes del protocolo.

1. Extrae todo el texto de «Protocolo de evaluación.docx» directamente del XML (sin usar contenido.js).
2. Sirve la carpeta en local, abre index.html en Edge o Chrome sin interfaz y lee el texto que
   muestra la página (sin los elementos de la interfaz, marcados con data-ui).
3. Compara los dos textos carácter a carácter. Solo se ignoran los espacios, las líneas «____»
   (que en la app son campos para escribir) y los «□» (que en la app son casillas).
4. Comprueba que las imágenes publicadas son idénticas a las del documento.

Uso:  python scripts/verificar.py [ruta de msedge.exe o chrome.exe]
"""
import hashlib, http.server, re, shutil, subprocess, sys, tempfile, threading, zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DOCX = RAIZ / 'Protocolo de evaluación.docx'
NAVEGADORES = [r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
               r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
               r'C:\Program Files\Google\Chrome\Application\chrome.exe']
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def texto_docx():
    z = zipfile.ZipFile(DOCX)
    body = ET.fromstring(z.read('word/document.xml')).find(W + 'body')
    partes = []
    for el in body.iter():
        if el.tag == W + 't': partes.append(el.text or '')
        elif el.tag in (W + 'tab', W + 'br', W + 'p'): partes.append(' ')
    return ''.join(partes), z

class Lector(HTMLParser):
    VACIOS = {'input', 'br', 'img', 'hr', 'meta', 'link'}
    def __init__(self):
        super().__init__(); self.pila = []; self.dentro = 0; self.texto = []; self.imgs = []
        self.casillas = 0; self.campos = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'div' and a.get('id') == 'contenido' and not self.dentro:
            self.dentro = 1; self.pila = [('div', False)]; return
        if not self.dentro: return
        if tag == 'img' and not any(s for _, s in self.pila): self.imgs.append(a.get('src'))
        if tag == 'input' and a.get('type') in ('checkbox', 'radio'): self.casillas += 1
        if (tag == 'input' and 'fill' in (a.get('class') or '')) or tag == 'textarea': self.campos += 1
        if tag in self.VACIOS: return
        saltar = 'data-ui' in a or tag in ('textarea', 'script', 'style')
        self.pila.append((tag, saltar))
    def handle_endtag(self, tag):
        if not self.dentro or tag in self.VACIOS: return
        while self.pila:
            t, _ = self.pila.pop()
            if t == tag: break
        if not self.pila: self.dentro = 0
    def handle_data(self, data):
        if self.dentro and not any(s for _, s in self.pila): self.texto.append(data)

def limpiar(s):
    return re.sub(r'[\s_□]+', '', s)

def dom_renderizado(nav):
    """Sirve la carpeta en local, abre index.html en el navegador sin interfaz y recibe el HTML ya dibujado.
    El script que devuelve el HTML se añade solo en esta respuesta; index.html no se modifica."""
    recibido = {}
    listo = threading.Event()
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k): super().__init__(*a, directory=str(RAIZ), **k)
        def log_message(self, *a): pass
        def do_GET(self):
            if self.path.split('?')[0] in ('/', '/index.html'):
                html = (RAIZ / 'index.html').read_text(encoding='utf-8').replace(
                    '</body>', "<script>fetch('/__dom',{method:'POST',body:document.documentElement.outerHTML})</script></body>")
                datos = html.encode('utf-8')
                self.send_response(200); self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(datos))); self.end_headers(); self.wfile.write(datos)
            else:
                super().do_GET()
        def do_POST(self):
            n = int(self.headers.get('Content-Length', 0))
            recibido['dom'] = self.rfile.read(n).decode('utf-8')
            self.send_response(204); self.end_headers(); listo.set()
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    perfil = tempfile.mkdtemp(prefix='verificar-')
    proc = subprocess.Popen([nav, '--headless=new', '--disable-gpu', '--no-first-run', '--user-data-dir=' + perfil,
                             'http://127.0.0.1:%d/index.html' % srv.server_address[1]],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        listo.wait(90)
    finally:
        proc.kill(); srv.shutdown()
        shutil.rmtree(perfil, ignore_errors=True)
    return recibido.get('dom', '')

def main():
    nav = sys.argv[1] if len(sys.argv) > 1 else next((n for n in NAVEGADORES if Path(n).exists()), None)
    if not nav: sys.exit('No se encontró Edge ni Chrome; indicar la ruta como argumento.')
    original, z = texto_docx()
    dom = dom_renderizado(nav)
    if 'id="contenido"' not in dom: sys.exit('No se pudo leer la página.')
    lec = Lector(); lec.feed(dom)
    app = ''.join(lec.texto)

    a, b = limpiar(original), limpiar(app)
    ok = True
    if a == b:
        print('TEXTO: idéntico (%d caracteres sin espacios ni líneas de respuesta).' % len(a))
    else:
        ok = False
        i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
        print('TEXTO: DIFERENTE en la posición %d' % i)
        print('  protocolo: …%s…' % a[max(0, i - 60):i + 60])
        print('  app:       …%s…' % b[max(0, i - 60):i + 60])

    # Cada «□» y cada «____» del documento debe tener su casilla o campo en la app
    casillas = original.count('□'); lineas = len(re.findall(r'_{3,}', original))
    n_chk, n_campos = lec.casillas, lec.campos
    print('CASILLAS: protocolo %d, app %d' % (casillas, n_chk))
    print('LÍNEAS DE RESPUESTA: protocolo %d, campos en la app %d (incluye celdas vacías de tablas)' % (lineas, n_campos))
    if n_chk != casillas: ok = False

    # Imágenes
    media = sorted(n for n in z.namelist() if n.startswith('word/media/'))
    publicadas = lec.imgs
    print('IMÁGENES: documento %d, app %d' % (len(media), len(publicadas)))
    if len(media) != len(publicadas): ok = False
    hd = {hashlib.sha256(z.read(n)).hexdigest() for n in media}
    for src in publicadas:
        h = hashlib.sha256((RAIZ / src).read_bytes()).hexdigest()
        if h not in hd: ok = False; print('  %s no coincide con ninguna imagen del documento' % src)
    if ok: print('IMÁGENES: idénticas byte a byte.')
    print('\nRESULTADO: %s' % ('OK' if ok else 'HAY DIFERENCIAS'))
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
