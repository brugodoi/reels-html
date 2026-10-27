---
name: reels-html
description: Produz vídeos verticais 9:16 (Reels, Stories, TikTok, Shorts e anúncios) mostrando um app ou sistema em uso, a partir de uma cena em HTML — celular animado com toques, digitação e troca de telas, título, legenda da fala sincronizada com locução (voz grátis edge-tts ou Google TTS) e fecho com a marca — e grava em MP4 1080×1920. Use quando o usuário pedir um vídeo/reel/anúncio em vídeo de demonstração de produto, "como funciona", tutorial curto ou refazer a locução/legenda de um vídeo desses. Não serve pra editar filmagem real nem vídeo horizontal.
---

# reels-html

Vídeo = **uma cena HTML** (`cenas/<cena>.html`) num palco fixo 1080×1920,
gravada quadro a quadro no Chrome e juntada com a locução. Tudo roda local.

`<skill>` abaixo = a pasta desta skill (onde está este arquivo).

## Fluxo (siga nesta ordem)

0. **Conhecer o produto antes de escrever qualquer copy.** Roteiro, títulos
   e locução saem do produto real, nunca de suposição.

   **a) Primeiro aprenda sozinho, sem pedir nada ao usuário.** Junte tudo o
   que já dá pra acessar:
   - o pedido e o que veio na conversa (prints, links, textos anexados);
   - o **código do app**, se o Claude Code estiver na pasta do projeto ou
     houver um caminho citado: telas/rotas, componentes, textos da
     interface (arquivos de tradução, botões), cores do tema;
   - o **site público** do produto (de `marca.js > site`, do pedido ou de
     uma busca pelo nome): página inicial, preços, central de ajuda,
     página na loja de apps — abra no navegador (Claude in Chrome ou o
     embutido) e tire prints das telas que aparecerem;
   - vídeos anteriores no projeto (`reels.json`, `cenas/*.html`).

   **b) Mostre a ficha do produto** com o que aprendeu: fluxo, telas, textos
   exatos, cor principal, benefício, o que o produto *não* faz — e de onde
   veio cada coisa. Liste à parte **o que falta** pra fazer o vídeo.

   **c) Só então, pras lacunas, sugira as outras fontes** (da melhor pra
   pior): prints ou gravação de tela do fluxo; acesso ao sistema logado
   (o usuário entra no navegador e você navega na sessão dele — nunca peça
   nem digite senha, não envie formulários nem altere dados sem ok); o
   caminho do código; ou perguntas curtas (passo a passo do fluxo, nome
   exato dos botões, um número real de exemplo). Aprendeu o suficiente
   sozinho → siga direto pro roteiro e peça só a confirmação da ficha.

   Não invente tela, botão, recurso ou número; faltou → pergunte.
1. **Roteiro primeiro, aprovado pelo usuário** antes de renderizar qualquer
   coisa: tabela com tempo · tela · o que acontece · título; e o texto da
   locução. Regras do roteiro:
   - 10–30 s. Gancho nos 3 primeiros segundos (título forte + algo já mexendo).
   - Locução ~2,5 palavras/s; frases curtas, separadas por vírgula/ponto
     (cada trecho vira uma legenda de até ~45 caracteres).
   - Nada de prometer o que o produto não faz: as telas imitam o produto
     real (rótulos e botões iguais). Números de exemplo plausíveis.
   - Fecho (logo + chamada + site) nos últimos 2–3 s, junto com o nome da
     marca na fala.
2. **Projeto**: se ainda não existe, `python <skill>/ferramentas/novo.py <pasta>`
   (cria `reels.json`, `marca.js`, `marca.css`, `motor/`, `cenas/demo.html`).
   Preencha a marca (`marca.js`: nome, logo, site, chamada; `marca.css`: cores).
   Rode **todas** as ferramentas de dentro da pasta do projeto.
3. **Locução**: texto em `reels.json > falas > <cena>`, depois
   `python <skill>/ferramentas/locucao.py <cena>` → `audio/<cena>.wav` e a
   duração. Fala mais longa que o roteiro → enxugue o texto (ou
   `reels.json > acelerar > <cena>: 1.05`, no máximo ~1.1).
4. **Cena**: copie `cenas/demo.html` como base e monte as telas do produto
   com os componentes de `motor/base.css` (lista abaixo). Agende os passos
   em `roteiro(m)` com `m.em(ms, fn)` seguindo os tempos do roteiro.
5. **Sincronia**: `python <skill>/ferramentas/pausas.py <cena> [pausa_min_ms]`
   imprime os trechos de voz e uma linha `falas: [...]` pronta pra colar no
   `Motor.cena`. Se juntou trechos demais numa legenda, rode com pausa
   menor (ex.: 60). Ajuste os tempos do roteiro (troca de tela, fecho) pra
   cair junto com a fala correspondente, e `duracao` = fim da fala + ~1,5 s.
6. **Gravar e montar**:
   `node <skill>/ferramentas/gravar.js <cena>` →
   `python <skill>/ferramentas/montar.py <cena>` → `mp4/<cena>.mp4`.
7. **Conferir antes de entregar**: `python <skill>/ferramentas/conferir.py <cena> 6`
   (ou instantes exatos: `conferir.py <cena> 500,4200,9800`) e **olhe a
   imagem** `mp4/<cena>-quadros.png`: título, legenda, botões, dedo no lugar
   certo, nada cortado, fecho. Depois abra o MP4 pro usuário assistir
   (Windows: `Start-Process mp4\<cena>.mp4`; macOS: `open`).
   Só publique/suba em rede social com o ok do usuário.

Prévia rápida no navegador (sem gravar): abra `cenas/<cena>.html`
(`?area=1` mostra a área segura; `?t=5000` congela em 5 s).

## Instalação (1ª vez e depois de cada atualização do plugin)

- Python 3.10+: `python -m pip install -r <skill>/requirements.txt`
- Node 18+: se `<skill>/ferramentas/node_modules` não existir,
  `npm --prefix <skill>/ferramentas install` (playwright-core; usa o
  Chrome instalado — `REELS_NAVEGADOR=msedge` pra usar o Edge).
- Fontes e ícones vêm da internet (Google Fonts, Tabler Icons via jsDelivr).

## Voz (`reels.json > voz`)

- `"provedor": "edge"` (padrão, grátis, sem conta): vozes em
  `edge-tts --list-voices` (pt-BR: `pt-BR-FranciscaNeural`, `pt-BR-AntonioNeural`,
  `pt-BR-ThalitaMultilingualNeural`); `"velocidade": "+5%"` opcional.
- `"provedor": "google"`: Google Cloud TTS (ex.: `pt-BR-Chirp3-HD-Leda`).
  Credencial via `gcloud auth application-default login` ou
  `GOOGLE_APPLICATION_CREDENTIALS`; projeto em `GOOGLE_CLOUD_PROJECT` ou
  `voz.projeto`. **Nunca** grave credencial/token dentro do projeto.

## Motor (`motor/motor.js`)

```js
Motor.cena({
    duracao: 11500,                 // ms (gravar.js e montar.py usam)
    etiqueta: '1 de 4',             // opcional, selo antes do título
    fecho: 'Teste <span>grátis</span>', // opcional (padrão: MARCA.chamada); <span> = degradê
    falas: [[390, 'Primeiro trecho.'], [1930, 'Segundo,'], [8710, '']], // ms do VÍDEO; '' apaga
    montar: function (palco) { /* estado inicial: injeta o <template> no .celular e o 1º título */ },
    roteiro: function (m) { m.em(500, function () { m.moverDedo('#botao'); }); }
});
```

Ajudantes do `m`: `em(ms, fn)` · `titulo(texto)` · `moverDedo(sel)` ·
`tocar(sel, depois)` (toque com onda; `depois(el)` muda o estado) ·
`esconderDedo()` · `digitar(sel, texto, ms)` (em `.ui-campo`) ·
`trocarTela(de, para)` / `voltarTela(de, para)` (telas `.tela`; as que
começam fora levam `tela--fora-direita`) · `rolar(sel, y)` ·
`reordenar(sel, antesDe)` · `fecho()`.

Padrão de ritmo: `moverDedo` → ~400 ms → `tocar` → ~400 ms → próximo passo.
Troca de tela leva 450 ms; troque o título junto com a tela.

## Componentes (`motor/base.css`)

Palco: `.palco` (adicione `titulo-2-linhas` pra gancho longo), `.celular`
(tela 300×600 ampliada 1,55×), `.tela`, `.status-bar`.
App: `.ui-topo`, `.ui-conteudo`, `.ui-titulo`, `.ui-ajuda`, `.ui-cartao`,
`.ui-rotulo`, `.ui-campo` (`.placeholder` dentro), `.ui-botao`
(`--primario`, `--ok`, `--desativado`, `--largo`), `.ui-opcoes`/`.ui-opcao`
(`--marcada`), `.ui-tag` (`--ok`, `--aviso`, `--info`), `.ui-alerta`,
`.ui-linha` (`--destaque`), `.ui-miniatura`, `.ui-info`, `.ui-numeros`/
`.ui-numero`, `.ui-barras` (mude `height` dos `<i>` pra animar).
Conversa: `.tela--chat`, `.chat-topo`, `.chat-avatar`, `.chat-conversa`,
`.bolha` (`--recebida`, `.bolha__autor`), `.chat-entrada`.
Extras: `.notificacao` (+`--visivel`), `.folha` (+`--aberta`), `.surgir`.
Ícones: Tabler (`<i class="ti ti-nome">`). Componente que não existe →
crie na própria cena (`<style>`), com as variáveis de cor.

## Regras de layout (redes sociais)

- Área segura: x 60–940, y 250–1500 (`?area=1`). Topo e base ficam sob os
  botões/legenda do app. Título em y ~270, celular y 400–1360, legenda da
  fala em y ~1380 — não mova sem motivo.
- Título curto (≤ 28 caracteres numa linha; o motor reduz a fonte até 36 px).
- Legenda da fala ≤ ~45 caracteres por trecho.
- Mesmo vídeo pra Reels/TikTok/Shorts/anúncio 9:16; versão curta = outra
  cena (copie e corte), não um parâmetro.

## Problemas comuns

- `Falta o ffmpeg portátil` → `python -m pip install imageio-ffmpeg`.
- `browserType.launch: Chromium distribution 'chrome' is not found` → instale o
  Chrome ou use `REELS_NAVEGADOR=msedge`.
- Legenda adiantada/atrasada → rode `pausas.py` de novo depois de mudar o texto;
  `atraso_fala_ms` (padrão 300) é quando a voz entra no vídeo.
- Ícone/fonte faltando no vídeo → sem internet na gravação.
- Erro de JS na cena aparece no terminal do `gravar.js` (`erro na cena`).
