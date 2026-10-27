<img src="../../docs/icone.png" width="96" align="right" alt="">

# reels-html-en

[Claude Code](https://claude.com/claude-code) plugin that produces **vertical 9:16
videos** (Reels, Stories, TikTok, Shorts and ads) showing an app or system in use,
from an HTML scene:

- animated phone with finger, taps, typing and screen transitions;
- title at the top and captions synced with the narration;
- free narration (edge-tts) or Google Cloud TTS;
- outro with logo, call to action and site;
- sharp frame-by-frame recording in Chrome and a 1080×1920 MP4 ready to post.

![Frames from the sample video](../../docs/demo-quadros.png)

## Install

In Claude Code:

```
/plugin marketplace add brugodoi/reels-html
/plugin install reels-html-en@reels-html
```

Requires Python 3.10+, Node 18+ and Google Chrome (or Edge, with
`REELS_NAVEGADOR=msedge`). On first use the skill installs its Python and
Node dependencies.

## Use

In Claude Code, ask for something like *"make a 20 s reel showing how a
customer books an appointment in my app"*. The skill drafts the script (you
approve it), builds the scene, generates the voice, syncs the captions,
records, assembles the MP4 and checks the frames before handing it over.

### How the skill learns your app

The video mimics your product's screens and the narration describes what it
really does. Before writing the script, the skill needs to **see the app
working**, and it does that in three steps:

1. **Learns on its own first**, without asking you anything: it reads the
   request and what you attached, the app's code (if Claude Code is open in
   the project folder) and the product's public website (home page, pricing,
   help, app store).
2. **Shows you a product sheet** with what it learned (flow, screens, text,
   color, main benefit, what the app does *not* do and where each item came
   from) and what is still missing for the video.
3. **Only then asks for what's missing**, suggesting the most useful source:

| Source | How to send it | What the skill gets from it |
|---|---|---|
| **Screenshots or screen recording** | drag the images into the chat or point to the folder | screens, labels, buttons, colors, flow order |
| **Logged-in system** | sign in to your Chrome and let it know; it browses your session | walks through the flow, takes screenshots and copies the exact text |
| **App code** | point to the folder path | screen names, buttons and UI text |
| **Short answers** | answer the skill's questions | step by step, button names, a sample number |

If it already learned enough on its own, it goes straight to the script and
only asks you to confirm the sheet. You fix anything wrong before any
recording; when in doubt, it asks instead of inventing screens or features.

> The skill never asks for your password. For systems with a login, sign in
> yourself in the browser and it uses the open session, without submitting
> forms or changing data without your ok. Prefer a test account or sample
> data in screenshots.

Example request: *"make a 20 s reel showing how a customer books an
appointment in my app, the site is `yoursite.com`"*. No need to attach
anything: the skill investigates on its own and only asks for screenshots or
access if something is missing.

By hand, from inside the video project folder (`<skill>` = the skill folder
inside the plugin, at `~/.claude/plugins/cache/reels-html/reels-html-en/<version>/skills/reels-html`):

```bash
python <skill>/ferramentas/novo.py my-video && cd my-video
python <skill>/ferramentas/locucao.py demo     # audio/demo.wav
python <skill>/ferramentas/pausas.py demo      # suggests the captions
node   <skill>/ferramentas/gravar.js demo      # frames
python <skill>/ferramentas/montar.py demo      # mp4/demo.mp4
python <skill>/ferramentas/conferir.py demo 6  # mp4/demo-quadros.png
```

The full walkthrough, the engine API and the components are in
[`SKILL.md`](skills/reels-html/SKILL.md).

## Layout

```
skills/reels-html/
  SKILL.md        skill instructions (workflow, engine, components, rules)
  motor/          engine: motor.js + base.css (stage, phone, components, finger, captions, outro)
  modelo/         template project copied by novo.py (fictional "Salonia" app)
  ferramentas/    tools: novo · locucao · pausas · gravar · montar · conferir
```

File, folder and API names keep their original Portuguese names so both
language versions share the same engine.

## License

[MIT](../../LICENSE). The "Salonia" example is fictional.
