# CLAUDE.md — Protocolo de evaluación logopédica

Manual online interativo do «Protocolo de evaluación logopédica» (Grado en Logopedia), para distribuir aos alunos. Autoria: **Alice Delgado Ramos Lima**. Projeto gerido por Marco Stiehl.

## Regras (obrigatórias)
- **Nenhuma informação do protocolo pode ser criada nem alterada.** O texto da app tem de ser exatamente igual ao do `Protocolo de evaluación.docx`, incluindo gralhas aparentes. Se algo parecer errado, avisar o Marco; não corrigir.
- Única exceção: as correções que o Marco pedir expressamente vão para `scripts/correcciones.py` (texto no docx → texto na app, quem pediu e quando). O gerador e o verificador aplicam-nas da mesma forma e falham se uma deixar de existir no docx. Atual: «Laboratorio practico» → «Laboratorio práctico» (2026-11-11).
- No mesmo ficheiro, `REUBICACIONES`: imagens que a app mostra noutro sítio, sem mudar texto. Atual: a folha do MoCA (`img/image3.png`), que no docx está no fim de «Apoyo independiente comprensión de palabras y órdenes», aparece no início de «MoCA guía de práctica y revisión de la copia» (pedido do Marco, 2026-11-11). O verificador confirma que está na secção de destino.
- Todo o texto da app (conteúdo e interface) em **espanhol de Espanha (castellano)**. Responder ao Marco em português de Portugal.
- O conteúdo nunca se edita à mão: muda-se o `.docx` e corre-se `python scripts/generar_contenido.py`.
- Depois de qualquer alteração (conteúdo, `index.html` ou gerador), correr `python scripts/verificar.py` e confirmar «RESULTADO: OK».
- No rodapé: referência do protocolo e «Autoría: Alice Delgado Ramos Lima».

## Estrutura
| Ficheiro | Função |
|---|---|
| `Protocolo de evaluación.docx` | Fonte de verdade. **Não vai para o repositório** (`.gitignore`); existe só na pasta local do Marco |
| `scripts/generar_contenido.py` | Gera `contenido.js` (`window.PROTOCOLO`) e copia as imagens para `img/` |
| `contenido.js` | Gerado. Secções (uma por «Heading 1» do docx) com blocos `p`, `h2`, `tabla`, `img`, `salto`; cada texto é uma lista de `[texto, negrita, cursiva]` |
| `index.html` | A app inteira (HTML + CSS + JS). Desenha tudo a partir do `contenido.js` |
| `scripts/generar_laminas.py` → `laminas.js` | Coordenadas (px da imagem) das casillas `c` e campos `t` sobre as láminas-exercício: MoCA (image3), TMT exemplos/A/B (image4–6, só Tiempo/Aciertos/Errores), cancelación (image7, só desenho), Boston 60 itens (image2, 60×3 + totais). Medidas à mão sobre as imagens; `--previa CARPETA` desenha-as para rever. Leva o sha256 de cada imagem |
| `scripts/correcciones.py` | Lista de correções autorizadas pelo Marco (a única exceção ao texto do docx) |
| `scripts/verificar.py` | Abre a página no Edge/Chrome sem interface (servidor local) e compara o texto mostrado com o do docx, carácter a carácter; conta casillas e compara imagens |
| `sw.js`, `manifest.webmanifest`, `icons/` | App instalável e offline. **Ao publicar alterações, subir `VERSION` no `sw.js`** |

## Como o index.html transforma o texto (sem o alterar)
- `□` → casilla (`checkbox`); células só com `□0 □1 …` (EAT-10) → botões de opção.
- `____` → campo de texto; parágrafo só com `_` → caixa de texto; célula de tabela vazia → caixa de texto; célula «1.», «2.»… (fluências) → número + campo.
- Prefixos «PÁGINA DEL EVALUADOR.», «PÁGINA DEL PARTICIPANTE.», «MATERIAL DE ELABORACIÓN DOCENTE.», «MATERIAL DOCENTE, NO BETA.» → etiqueta colorida (mesmo texto).
- Índice agrupado pela primeira palavra comum dos títulos (só usa palavras dos próprios títulos).
- Tudo o que é interface e não vem do protocolo tem `data-ui` (o verificador ignora-o). Texto novo de interface tem de levar `data-ui` ou ficar fora de `#contenido`.
- Láminas-exercício (`laminaHTML`): a imagem fica intacta; por cima, uma camada `.capa` com `data-ui` (sem texto) com as casillas/campos de `laminas.js` (ids `lam.imageN.k`) e um SVG com os traços. «Rellenar y dibujar sobre la lámina» leva a mesma `.lam-hoja` para o ecrã `#rel` (Lápiz, Borrar trazo, Mover, Deshacer, Borrar dibujo, zoom com pinça/roda) e devolve-a ao fechar. O verificador conta estes campos à parte («LÁMINAS») e falha se o sha256 de uma imagem mudar.
- Respostas em `localStorage` (`logoeval.respuestas.v1`); traços em `logoeval.dibujos.v1` (`{src: [[x,y,…], …]}` em px da imagem); tema em `logoeval.tema`. «Borrar mis respuestas» apaga os dois.
- Página «Cómo funciona esta app» (`#/acerca`, secção `#s-acerca` com `data-ui`): propósito, uso de cada ferramenta, dados e autoria. Ligada no índice, na capa e no rodapé. É texto da app, não do protocolo: **quando se acrescenta ou muda uma ferramenta, atualizar esta página**.

## Testar
`python -m http.server 8000` e abrir `http://localhost:8000`. Testar em telemóvel (≈390 px) e computador (≈1280 e 1920 px), temas claro e escuro. O Edge sem interface não desce abaixo de ~492 px: para 390 px usar um iframe com essa largura. Nas capturas sem interface, as imagens grandes podem não aparecer por causa de `decoding="async"`: forçar `decoding='sync'` no script de teste (no browser real aparecem).

## Cuidados
- O protocolo inclui material com direitos de autor (MoCA, lâmina Cookie Theft, folha de 60 itens do Boston). Confirmar com a autora se a app pode ser pública ou se deve ficar com acesso restrito.
