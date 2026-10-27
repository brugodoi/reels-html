/**
 * Records cenas/<scene>.html?gravar=1 at 1080×1920 with the installed Chrome
 * (playwright-core, doesn't download a browser), capturing frames through
 * Chrome's screencast (JPEG 95, with each frame's timestamp) — much sharper
 * than Playwright's recordVideo (VP8 blurs text).
 *
 * The duration comes from the scene itself (window.cenaDuracao, from Motor.cena).
 * Output: gravacoes/<scene>/quadro-XXXXX.jpg + lista.txt (ffmpeg "concat"
 * list with each frame's duration) + duracao.txt. montar.py joins it with
 * the voice. Browser: REELS_NAVEGADOR=chrome (default) | msedge.
 *
 * Usage (from the project folder):
 *     npm --prefix <skill>/ferramentas install   (first run)
 *     node <skill>/ferramentas/gravar.js <scene> [scene...]
 */
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');

const PROJETO = process.cwd();

(async () => {
    const cenas = process.argv.slice(2);
    if (!cenas.length) {
        console.error('Usage: node gravar.js <scene> [scene...]  (files in cenas/<scene>.html)');
        process.exit(1);
    }
    const navegador = await chromium.launch({ channel: process.env.REELS_NAVEGADOR || 'chrome' });

    for (const nome of cenas) {
        const html = path.join(PROJETO, 'cenas', `${nome}.html`);
        if (!fs.existsSync(html)) { console.error(`${nome}: ${html} not found`); continue; }
        const pasta = path.join(PROJETO, 'gravacoes', nome);
        fs.rmSync(pasta, { recursive: true, force: true });
        fs.mkdirSync(pasta, { recursive: true });

        const contexto = await navegador.newContext({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
        const pagina = await contexto.newPage();
        pagina.on('pageerror', erro => console.error(`${nome}: scene error — ${erro.message}`));
        await pagina.goto(pathToFileURL(html).href + '?gravar=1');
        await pagina.waitForFunction(() => window.cenaPronta === true, null, { timeout: 30000 });
        await pagina.waitForTimeout(500);
        const DURACAO = await pagina.evaluate(() => window.cenaDuracao);

        const cdp = await contexto.newCDPSession(pagina);
        const quadros = [];
        cdp.on('Page.screencastFrame', async ({ data, metadata, sessionId }) => {
            quadros.push({ t: metadata.timestamp, data });
            await cdp.send('Page.screencastFrameAck', { sessionId }).catch(() => {});
        });
        await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 95, maxWidth: 1080, maxHeight: 1920, everyNthFrame: 1 });
        await pagina.waitForTimeout(300); // 1st frame (initial state) before starting
        const inicio = Date.now() / 1000;
        await pagina.evaluate(() => window.iniciarCena());
        await pagina.waitForFunction(() => window.cenaFim === true, null, { timeout: (DURACAO + 20) * 1000, polling: 50 });
        await pagina.waitForTimeout(200);
        await cdp.send('Page.stopScreencast');
        await contexto.close();

        // Frame current at the start + all after it; each lasts until the next one.
        const antes = quadros.filter(q => q.t <= inicio);
        const usados = (antes.length ? [antes[antes.length - 1]] : []).concat(quadros.filter(q => q.t > inicio));
        const linhas = [];
        usados.forEach((q, i) => {
            const arquivo = `quadro-${String(i).padStart(5, '0')}.jpg`;
            fs.writeFileSync(path.join(pasta, arquivo), Buffer.from(q.data, 'base64'));
            const de = Math.max(q.t, inicio) - inicio;
            const ate = i + 1 < usados.length ? usados[i + 1].t - inicio : DURACAO;
            linhas.push(`file '${arquivo}'`, `duration ${Math.max(0.001, Math.min(ate, DURACAO) - de).toFixed(4)}`);
        });
        linhas.push(`file 'quadro-${String(usados.length - 1).padStart(5, '0')}.jpg'`); // required by concat
        fs.writeFileSync(path.join(pasta, 'lista.txt'), linhas.join('\n') + '\n');
        fs.writeFileSync(path.join(pasta, 'duracao.txt'), String(DURACAO));
        console.log(`${nome}: ${usados.length} frames (${DURACAO} s) in gravacoes/${nome}/`);
    }
    await navegador.close();
})();
