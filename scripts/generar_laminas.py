"""Genera laminas.js: casillas y campos sobre las láminas que son ejercicios.

Las coordenadas (en píxeles de cada imagen) se midieron sobre img/imageN.png: cada «[ ]» es una casilla («c»)
y cada «___» un campo («t»). No se añade texto: la capa solo marca posiciones sobre la imagen original.
Si cambia una imagen del documento, verificar.py avisa (sha256) y hay que revisar aquí sus coordenadas.

Uso:  python scripts/generar_laminas.py [--previa CARPETA]   (--previa dibuja los campos sobre cada imagen para revisarlos)
Requiere Pillow solo para --previa y para leer el tamaño de las imágenes.
"""
import hashlib, json, sys
from pathlib import Path
from PIL import Image, ImageDraw
P = Path(__file__).resolve().parent.parent
PREVIA = Path(sys.argv[sys.argv.index('--previa') + 1]) if '--previa' in sys.argv else None
def br(x, y, w=50, h=33): return ['c', x - 6, y - 4, w + 12, h + 8]
def sc(x, y): return ['t', x, y, 58, 38]   # «__/N»
moca = [
  ['t',1045,35,170,32], ['t',1035,92,180,30], ['t',1000,124,215,30], ['t',1470,58,190,32], ['t',1310,98,350,32],
  br(507,743), br(930,743), br(1093,743), br(1267,743), br(1439,743), sc(1552,744),
  br(510,1153,44), br(987,1153,40), br(1486,1153,40), sc(1552,1150),
]
cols = [744,877,1047,1191,1404,1547]
for (y0,y1) in ((1264,1298),(1300,1334)):
  for i in range(5): moca.append(['c', cols[i]+4, y0, cols[i+1]-cols[i]-8, y1-y0])
moca += [br(1214,1349,48,34), br(1214,1388,48,34), sc(1552,1385),
  br(758,1478,46,37), sc(1552,1472),
  br(574,1538,34,27), br(773,1538,34,27), br(978,1538,34,27), br(1180,1538,34,27), br(1380,1538,34,27), sc(1552,1558),
  br(891,1625,35,24), br(1418,1625,35,24), sc(1552,1615),
  br(1216,1673,56,34), ['t',1278,1666,78,34], sc(1552,1672),
  br(835,1737,48,33), br(1125,1737,47,33), sc(1552,1730),
  br(649,1844,41,33), br(797,1844,40,33), br(952,1844,40,33), br(1128,1844,39,33), br(1304,1844,40,33), sc(1552,1800)]
cols = [591,733,900,1049,1257,1396]
for (y0,y1) in ((1889,1926),(1931,1968)):
  for i in range(5): moca.append(['c', cols[i]+4, y0, cols[i+1]-cols[i]-8, y1-y0])
moca += [br(374,1994,47,33), br(578,1994,47,33), br(778,1994,47,33), br(985,1994,47,33), br(1181,1994,47,33), br(1389,1994,48,33), sc(1552,1988),
  ['t',1520,2056,78,40]]

def tmt(t, a, e): return [['t']+t, ['t']+a, ['t']+e]
tmta = tmt([148,1972,112,34],[160,2016,92,34],[566,2016,96,34])
tmtb = tmt([163,1983,114,34],[173,2028,94,34],[583,2028,96,34])

# Boston: 60 × (Correcto, Semántica, Fonológica); las columnas del escaneo están algo inclinadas
L = [68,128,186,244,304,362,421,480,539,598,657,717,775,833,892,948,1006,1064,1122,1180,1239,1296,1355,1413,1471,1531,1591,1649,1709,1768,1827,1885,1943]
R = [14,73,131,190,248,306,365,423,482,541,600,658,717,776,834,892,949,1006,1064,1122,1180,1238,1295,1353,1411,1470,1529,1589,1649]
def colx(top, bot, y): return [t + (b - t) * (y - 250) / 1200 for t, b in zip(top, bot)]
boston = []
for lines, top, bot in ((L,[333,457,579,704],[321,445,569,695]), (R,[1042,1164,1284,1405],[1036,1159,1278,1403])):
  for k in range(len(lines) - 1):
    y0, y1 = lines[k], lines[k+1]; xs = colx(top, bot, (y0 + y1) / 2)
    for i in range(3): boston.append(['c', round(xs[i]) + 6, y0 + 5, round(xs[i+1] - xs[i]) - 12, y1 - y0 - 10])
boston += [['t',742,1700,126,38], ['t',877,1700,126,38], ['t',1165,1700,126,38], ['t',896,1752,112,38]]

LAM = {'image2.png': boston, 'image3.png': moca, 'image4.png': [], 'image5.png': tmta, 'image6.png': tmtb, 'image7.png': []}
out = {}
for n, campos in LAM.items():
  f = P / 'img' / n; im = Image.open(f)
  out['img/' + n] = {'sha256': hashlib.sha256(f.read_bytes()).hexdigest(), 'w': im.width, 'h': im.height, 'campos': campos}
  if PREVIA:
    PREVIA.mkdir(parents=True, exist_ok=True); pv = im.convert('RGB'); d = ImageDraw.Draw(pv)
    for c in campos: d.rectangle([c[1], c[2], c[1]+c[3], c[2]+c[4]], outline=(220,0,0) if c[0]=='c' else (0,90,255), width=3)
    pv.save(PREVIA / n)
js = ('// Generado con scripts/generar_laminas.py: no editar a mano.\n'
      '// Campos y capa de dibujo sobre las láminas que son ejercicios (MoCA, Trail Making Test, cancelación, Boston 60 ítems).\n'
      '// Solo coordenadas en píxeles de cada imagen: no contiene texto del protocolo. «c» = casilla, «t» = campo [tipo, x, y, ancho, alto].\n'
      '// sha256 identifica la imagen: scripts/verificar.py comprueba que sigue siendo la misma.\n'
      'window.LAMINAS = {\n' + ',\n'.join('  %s: {"sha256":"%s","w":%d,"h":%d,"campos":%s}' % (json.dumps(k), v['sha256'], v['w'], v['h'], json.dumps(v['campos'], separators=(',',':'))) for k, v in out.items()) + '\n};\n')
(P / 'laminas.js').write_text(js, encoding='utf-8')
print({k: len(v['campos']) for k, v in out.items()})
