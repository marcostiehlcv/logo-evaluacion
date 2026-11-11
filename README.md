# Protocolo de evaluación logopédica

Versión web interactiva del **Protocolo de evaluación logopédica · Evaluación de las Alteraciones de Base Anatómica y Neurológica** (Grado en Logopedia · Laboratorio practico).

Autoría: **Alice Delgado Ramos Lima**.

## Qué ofrece

- Todo el contenido del protocolo, **sin cambios**: mismo texto, mismas tablas, mismas imágenes.
- Índice agrupado (Exploración orofacial, Boston, BETA, Trail Making Test, Deglución…) y búsqueda en todo el texto.
- Casillas y campos que se pueden rellenar; se guardan solo en el dispositivo y se pueden imprimir.
- «Presentar»: en las páginas del participante, el material se muestra a pantalla completa, un elemento cada vez.
- Imágenes ampliables (lámina del robo de las galletas, MoCA, Trail Making Test, cancelación…).
- Cronómetro (libre, 5 s, 60 s con marcas a los 15, 30 y 45 s, 2 min).
- Tema claro y oscuro; se puede instalar en el móvil y usar sin conexión.

## Fidelidad al protocolo

El contenido no se escribe a mano: `scripts/generar_contenido.py` lo extrae de `Protocolo de evaluación.docx` y genera `contenido.js` e `img/`.
`scripts/verificar.py` abre la página en Edge o Chrome sin interfaz y compara, carácter a carácter, el texto que se muestra con el del documento; también comprueba que cada «□» tiene su casilla y que las imágenes son idénticas.

El `.docx` no se incluye en este repositorio; para regenerar el contenido hay que colocarlo en la raíz del proyecto.

```
python scripts/generar_contenido.py   # después de cambiar el .docx
python scripts/verificar.py           # debe terminar en «RESULTADO: OK»
```

## Probar en local

```
python -m http.server 8000
```

y abrir <http://localhost:8000>.
