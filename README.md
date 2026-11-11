# Protocolo de evaluación logopédica

Versión web interactiva del **Protocolo de evaluación logopédica · Evaluación de las Alteraciones de Base Anatómica y Neurológica** (Grado en Logopedia · Laboratorio práctico).

Autoría: **Alice Delgado Ramos Lima**.

## Qué ofrece

- Todo el contenido del protocolo, **sin cambios**: mismo texto, mismas tablas, mismas imágenes.
- Índice agrupado (Exploración orofacial, Boston, BETA, Trail Making Test, Deglución…) y búsqueda en todo el texto.
- Casillas y campos que se pueden rellenar; se guardan solo en el dispositivo y se pueden imprimir.
- «Presentar»: en las páginas del participante, el material se muestra a pantalla completa, un elemento cada vez.
- Imágenes ampliables (lámina del robo de las galletas, MoCA, Trail Making Test, cancelación…).
- Láminas que son ejercicios (MoCA, Trail Making Test, cancelación de letras, registro de 60 ítems del Boston): casillas y campos sobre la propia imagen, en la posición de cada «[ ]» y «___», y un lápiz a pantalla completa para unir círculos, tachar letras o dibujar el cubo y el reloj (con borrar, deshacer y ampliar).
- Cronómetro (libre, 5 s, 60 s con marcas a los 15, 30 y 45 s, 2 min).
- Tema claro y oscuro; se puede instalar en el móvil y usar sin conexión.
- Página «Cómo funciona esta app» (`#/acerca`) con el propósito de la app y una guía de uso.

## Fidelidad al protocolo

El contenido no se escribe a mano: `scripts/generar_contenido.py` lo extrae de `Protocolo de evaluación.docx` y genera `contenido.js` e `img/`.
`scripts/verificar.py` abre la página en Edge o Chrome sin interfaz y compara, carácter a carácter, el texto que se muestra con el del documento; también comprueba que cada «□» tiene su casilla y que las imágenes son idénticas.
La única excepción son las correcciones autorizadas de `scripts/correcciones.py` (por ahora, la tilde de «Laboratorio práctico»), que ambos scripts aplican por igual.

El `.docx` no se incluye en este repositorio; para regenerar el contenido hay que colocarlo en la raíz del proyecto.

Las casillas y los campos de las láminas están en `laminas.js`, generado por `scripts/generar_laminas.py`: solo son coordenadas sobre la imagen original, sin texto. `verificar.py` comprueba que cada imagen sigue siendo la misma (sha256) y que todos los campos aparecen.

```
python scripts/generar_contenido.py   # después de cambiar el .docx
python scripts/generar_laminas.py     # si cambian las coordenadas de las láminas (--previa CARPETA para revisarlas)
python scripts/verificar.py           # debe terminar en «RESULTADO: OK»
```

## Probar en local

```
python -m http.server 8000
```

y abrir <http://localhost:8000>.
