# CLAUDE.md — Protocolo de evaluación logopédica

Manual online interativo do «Protocolo de evaluación logopédica» (Grado en Logopedia), para distribuir aos alunos. Autoria: **Alice Delgado Ramos Lima**. Projeto gerido por Marco Stiehl.

## Regras (obrigatórias)
- **Nenhuma informação do protocolo pode ser criada nem alterada.** O texto da app tem de ser exatamente igual ao do `Protocolo de evaluación.docx`, incluindo gralhas aparentes (ex.: «Laboratorio practico»). Se algo parecer errado, avisar o Marco; não corrigir.
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
| `scripts/verificar.py` | Abre a página no Edge/Chrome sem interface (servidor local) e compara o texto mostrado com o do docx, carácter a carácter; conta casillas e compara imagens |
| `sw.js`, `manifest.webmanifest`, `icons/` | App instalável e offline. **Ao publicar alterações, subir `VERSION` no `sw.js`** |

## Como o index.html transforma o texto (sem o alterar)
- `□` → casilla (`checkbox`); células só com `□0 □1 …` (EAT-10) → botões de opção.
- `____` → campo de texto; parágrafo só com `_` → caixa de texto; célula de tabela vazia → caixa de texto; célula «1.», «2.»… (fluências) → número + campo.
- Prefixos «PÁGINA DEL EVALUADOR.», «PÁGINA DEL PARTICIPANTE.», «MATERIAL DE ELABORACIÓN DOCENTE.», «MATERIAL DOCENTE, NO BETA.» → etiqueta colorida (mesmo texto).
- Índice agrupado pela primeira palavra comum dos títulos (só usa palavras dos próprios títulos).
- Tudo o que é interface e não vem do protocolo tem `data-ui` (o verificador ignora-o). Texto novo de interface tem de levar `data-ui` ou ficar fora de `#contenido`.
- Respostas em `localStorage` (`logoeval.respuestas.v1`); tema em `logoeval.tema`.

## Testar
`python -m http.server 8000` e abrir `http://localhost:8000`. Testar em telemóvel (≈390 px) e computador (≈1280 e 1920 px), temas claro e escuro. O Edge sem interface não desce abaixo de ~492 px: para 390 px usar um iframe com essa largura.

## Cuidados
- O protocolo inclui material com direitos de autor (MoCA, lâmina Cookie Theft, folha de 60 itens do Boston). Confirmar com a autora se a app pode ser pública ou se deve ficar com acesso restrito.
