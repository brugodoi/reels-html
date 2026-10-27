---
name: reels-html
description: Produces vertical 9:16 videos (Reels, Stories, TikTok, Shorts and ads) showing an app or system in use, from an HTML scene — animated phone with taps, typing and screen transitions, title, voice-over captions synced with TTS narration (free edge-tts voice or Google TTS) and a brand outro — recorded as a 1080×1920 MP4. Use when the user asks for a product demo video/reel/video ad, a "how it works", a short tutorial, or to redo the narration/captions of such a video. Not for editing real footage or horizontal video.
---

# reels-html

Video = **one HTML scene** (`cenas/<scene>.html`) on a fixed 1080×1920 stage,
recorded frame by frame in Chrome and joined with the narration. Everything runs locally.

`<skill>` below = this skill's folder (where this file lives).

> The engine and config keys keep their original (Portuguese) names — `Motor.cena`,
> `m.tocar`, `.ui-botao`, `reels.json > falas` — so both language versions share the
> same engine. Use them exactly as documented here; write all on-screen text,
> captions and narration in the user's language.

## Workflow (follow in this order)

0. **Know the product before writing any copy.** Script, titles and
   narration come from the real product, never from assumptions.

   **a) Learn on your own first, without asking the user anything.** Gather
   everything you can already access:
   - the request and the conversation (screenshots, links, attached text);
   - the **app's code**, if Claude Code is in the project folder or a path
     was mentioned: screens/routes, components, UI text (translation files,
     buttons), theme colors;
   - the product's **public website** (from `marca.js > site`, the request, or
     a search for the name): home page, pricing, help center, app store
     page — open it in the browser (Claude in Chrome or the built-in one) and
     take screenshots of the screens shown;
   - previous videos in the project (`reels.json`, `cenas/*.html`).

   **b) Show the product sheet** with what you learned: flow, screens, exact
   text, main color, benefit, what the product does *not* do — and where each
   item came from. List separately **what is missing** to make the video.

   **c) Only then, for the gaps, suggest other sources** (best to worst):
   screenshots or a screen recording of the flow; access to the logged-in
   system (the user signs in in the browser and you navigate their session —
   never ask for or type a password, don't submit forms or change data without
   an ok); the code path; or short questions (step-by-step flow, exact button
   names, a real sample number). Learned enough on your own → go straight to
   the script and only ask to confirm the sheet.

   Don't invent screens, buttons, features or numbers; if something is missing → ask.
1. **Script first, approved by the user** before rendering anything: table
   with time · screen · what happens · title; and the narration text. Script rules:
   - 10–30 s. Hook in the first 3 seconds (strong title + something already moving).
   - Narration ~2.5 words/s; short sentences separated by commas/periods
     (each chunk becomes a caption of up to ~45 characters).
   - Never promise what the product doesn't do: screens mimic the real product
     (same labels and buttons). Plausible sample numbers.
   - Outro (logo + call to action + site) in the last 2–3 s, together with the
     brand name in the narration.
2. **Project**: if it doesn't exist yet, `python <skill>/ferramentas/novo.py <folder>`
   (creates `reels.json`, `marca.js`, `marca.css`, `motor/`, `cenas/demo.html`).
   Fill in the brand (`marca.js`: name, logo, site, call to action; `marca.css`: colors).
   Run **all** tools from inside the project folder.
3. **Narration**: text in `reels.json > falas > <scene>`, then
   `python <skill>/ferramentas/locucao.py <scene>` → `audio/<scene>.wav` and its
   duration. Narration longer than the script → trim the text (or
   `reels.json > acelerar > <scene>: 1.05`, at most ~1.1).
4. **Scene**: copy `cenas/demo.html` as a base and build the product screens
   with the components from `motor/base.css` (list below). Schedule the steps
   in `roteiro(m)` with `m.em(ms, fn)` following the script timings.
5. **Sync**: `python <skill>/ferramentas/pausas.py <scene> [min_pause_ms]`
   prints the voice chunks and a `falas: [...]` line ready to paste into
   `Motor.cena`. If it merged too many chunks into one caption, run with a
   smaller pause (e.g. 60). Adjust the script timings (screen change, outro)
   to land with the matching narration, and `duracao` = end of narration + ~1.5 s.
6. **Record and assemble**:
   `node <skill>/ferramentas/gravar.js <scene>` →
   `python <skill>/ferramentas/montar.py <scene>` → `mp4/<scene>.mp4`.
7. **Check before delivering**: `python <skill>/ferramentas/conferir.py <scene> 6`
   (or exact instants: `conferir.py <scene> 500,4200,9800`) and **look at the
   image** `mp4/<scene>-quadros.png`: title, caption, buttons, finger in the right
   place, nothing cut off, outro. Then open the MP4 for the user to watch
   (Windows: `Start-Process mp4\<scene>.mp4`; macOS: `open`).
   Only publish/upload to social media with the user's ok.

Quick browser preview (no recording): open `cenas/<scene>.html`
(`?area=1` shows the safe area; `?t=5000` freezes at 5 s).

## Installation (first run, and after each plugin update)

- Python 3.10+: `python -m pip install -r <skill>/requirements.txt`
- Node 18+: if `<skill>/ferramentas/node_modules` doesn't exist,
  `npm --prefix <skill>/ferramentas install` (playwright-core; uses the installed
  Chrome — `REELS_NAVEGADOR=msedge` to use Edge).
- Fonts and icons come from the internet (Google Fonts, Tabler Icons via jsDelivr).

## Voice (`reels.json > voz`)

- `"provedor": "edge"` (default, free, no account): voices via
  `edge-tts --list-voices` (en-US: `en-US-AvaNeural`, `en-US-AndrewNeural`,
  `en-US-EmmaMultilingualNeural`); optional `"velocidade": "+5%"`.
- `"provedor": "google"`: Google Cloud TTS (e.g. `en-US-Chirp3-HD-Leda`).
  Credentials via `gcloud auth application-default login` or
  `GOOGLE_APPLICATION_CREDENTIALS`; project in `GOOGLE_CLOUD_PROJECT` or
  `voz.projeto`. **Never** store credentials/tokens inside the project.

## Engine (`motor/motor.js`)

```js
Motor.cena({
    duracao: 11500,                 // ms (used by gravar.js and montar.py)
    etiqueta: '1 of 4',             // optional, badge before the title
    fecho: 'Try it <span>free</span>', // optional (default: MARCA.chamada); <span> = gradient
    falas: [[390, 'First chunk.'], [1930, 'Second,'], [8710, '']], // VIDEO ms; '' clears
    montar: function (palco) { /* initial state: inject the <template> into .celular and the 1st title */ },
    roteiro: function (m) { m.em(500, function () { m.moverDedo('#button'); }); }
});
```

`m` helpers: `em(ms, fn)` (at) · `titulo(text)` (title) · `moverDedo(sel)` (move finger) ·
`tocar(sel, after)` (tap with ripple; `after(el)` changes state) ·
`esconderDedo()` (hide finger) · `digitar(sel, text, ms)` (type, in `.ui-campo`) ·
`trocarTela(from, to)` / `voltarTela(from, to)` (switch/go back; `.tela` screens — those
starting off-screen get `tela--fora-direita`) · `rolar(sel, y)` (scroll) ·
`reordenar(sel, before)` (reorder) · `fecho()` (outro).

Rhythm pattern: `moverDedo` → ~400 ms → `tocar` → ~400 ms → next step.
A screen transition takes 450 ms; change the title together with the screen.

## Components (`motor/base.css`)

Stage: `.palco` (add `titulo-2-linhas` for a long hook), `.celular` (phone;
300×600 screen scaled 1.55×), `.tela` (screen), `.status-bar`.
App: `.ui-topo` (top bar), `.ui-conteudo` (content), `.ui-titulo`, `.ui-ajuda` (help text),
`.ui-cartao` (card), `.ui-rotulo` (label), `.ui-campo` (input; `.placeholder` inside),
`.ui-botao` (button: `--primario`, `--ok`, `--desativado`, `--largo`),
`.ui-opcoes`/`.ui-opcao` (choices; `--marcada` = selected), `.ui-tag` (`--ok`, `--aviso`, `--info`),
`.ui-alerta` (alert), `.ui-linha` (row; `--destaque`), `.ui-miniatura` (thumbnail), `.ui-info`,
`.ui-numeros`/`.ui-numero` (stats), `.ui-barras` (bar chart; change the `<i>` `height` to animate).
Chat: `.tela--chat`, `.chat-topo`, `.chat-avatar`, `.chat-conversa`,
`.bolha` (bubble: `--recebida` = received, `.bolha__autor`), `.chat-entrada` (input bar).
Extras: `.notificacao` (+`--visivel`), `.folha` (bottom sheet, +`--aberta`), `.surgir` (fade in).
Icons: Tabler (`<i class="ti ti-name">`). Missing component →
create it in the scene itself (`<style>`), using the color variables.

## Layout rules (social media)

- Safe area: x 60–940, y 250–1500 (`?area=1`). Top and bottom sit under the
  app's buttons/captions. Title at y ~270, phone y 400–1360, narration caption
  at y ~1380 — don't move them without a reason.
- Short title (≤ 28 characters on one line; the engine shrinks the font down to 36 px).
- Narration caption ≤ ~45 characters per chunk.
- Same video for Reels/TikTok/Shorts/9:16 ads; a short version = another
  scene (copy and cut), not a parameter.

## Common problems

- `Missing portable ffmpeg` → `python -m pip install imageio-ffmpeg`.
- `browserType.launch: Chromium distribution 'chrome' is not found` → install
  Chrome or use `REELS_NAVEGADOR=msedge`.
- Caption early/late → run `pausas.py` again after changing the text;
  `atraso_fala_ms` (default 300) is when the voice starts in the video.
- Icon/font missing in the video → no internet during recording.
- A JS error in the scene shows up in the `gravar.js` terminal (`scene error`).
