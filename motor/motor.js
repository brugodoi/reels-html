/**
 * reels-html — motor das cenas (vídeo vertical 1080×1920 feito em HTML).
 *
 * Cada cena chama Motor.cena({ etiqueta, duracao, falas, fecho, montar, roteiro }):
 *   - duracao: ms totais da cena (o gravar.js lê e o montar.py usa);
 *   - falas: [[ms, 'trecho da locução'], ..., [ms, '']] — legenda da fala,
 *     sincronizada com audio/<cena>.wav (a voz entra ATRASO ms depois, ver
 *     reels.json > atraso_fala_ms); '' apaga. Use pausas.py pra achar os ms;
 *   - etiqueta (opcional): selo antes do título (ex.: '1 de 4');
 *   - fecho (opcional): HTML da chamada final (padrão: MARCA.chamada);
 *   - montar(palco): devolve o palco ao estado inicial (chamado a cada volta);
 *   - roteiro(m): agenda os passos com m.em(ms, fn) e usa os ajudantes
 *     m.titulo(), m.tocar(), m.moverDedo(), m.esconderDedo(), m.digitar(),
 *     m.trocarTela(), m.voltarTela(), m.rolar(), m.reordenar(), m.fecho().
 *
 * Marca: window.MARCA (marca.js do projeto) = { nome, logo, site, chamada }.
 *
 * Parâmetros da URL:
 *   ?gravar=1   palco 1:1; espera o gravador chamar window.iniciarCena()
 *               (quando window.cenaPronta), toca UMA vez e marca window.cenaFim;
 *   ?area=1     desenha a área segura das redes (Reels/Stories/TikTok);
 *   ?recorte=1  mostra só a faixa útil (y 230–1520) — pra embutir num site;
 *   ?t=5000     congela nesse instante (pra conferir um quadro).
 */
(function () {
    'use strict';

    var params = new URLSearchParams(location.search);
    var GRAVAR = params.get('gravar') === '1';
    var RECORTE = params.get('recorte') === '1';
    var RECORTE_TOPO = 230, RECORTE_ALTURA = 1290;
    var ESCALA_CELULAR = 1.55; // = transform da .celular em base.css
    var MARCA = window.MARCA || {};
    var palco, dedo, escala = 1, timers = [];

    function $(sel) { return typeof sel === 'string' ? palco.querySelector(sel) : sel; }

    function escapar(t) { return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;'); }

    function ajustarEscala() {
        var altura = RECORTE ? RECORTE_ALTURA : 1920;
        escala = GRAVAR ? 1 : Math.min(innerWidth / 1080, innerHeight / altura);
        palco.style.transform = 'scale(' + escala + ')';
        palco.style.left = GRAVAR ? '0' : ((innerWidth - 1080 * escala) / 2) + 'px';
        palco.style.top = RECORTE ? (-RECORTE_TOPO * escala + (innerHeight - altura * escala) / 2) + 'px' : '0';
    }

    /** Centro do elemento em coordenadas do palco (1080×1920). */
    function centro(sel) {
        var r = $(sel).getBoundingClientRect(), p = palco.getBoundingClientRect();
        return { x: (r.left + r.width / 2 - p.left) / escala, y: (r.top + r.height / 2 - p.top) / escala };
    }

    /** Reduz a fonte do título até caber na faixa de 800 px (some se vazio). */
    function caberTitulo() {
        var el = $('.titulo__texto'), etiqueta = $('.titulo__etiqueta');
        var max = 800 - (etiqueta.textContent ? etiqueta.offsetWidth + 20 : 0), t = 58;
        el.style.fontSize = t + 'px';
        while (el.scrollWidth > max && t > 36) { t -= 2; el.style.fontSize = t + 'px'; }
    }

    var m = {
        em: function (ms, fn) { timers.push(setTimeout(fn, ms)); },

        /** Troca o título do topo (com animação). */
        titulo: function (texto) {
            var el = $('.titulo__texto');
            el.classList.add('trocando');
            setTimeout(function () {
                el.textContent = texto;
                caberTitulo();
                el.classList.remove('trocando');
            }, 250);
        },

        moverDedo: function (sel) {
            var c = centro(sel);
            dedo.style.left = c.x + 'px';
            dedo.style.top = c.y + 'px';
            dedo.classList.add('dedo--visivel');
        },

        esconderDedo: function () { dedo.classList.remove('dedo--visivel'); },

        /** Toque visual no elemento (mova o dedo antes); `depois(el)` roda no fim do toque. */
        tocar: function (sel, depois) {
            var el = $(sel), c = centro(sel), onda = document.createElement('div');
            dedo.classList.add('dedo--tocando');
            el.classList.add('apertado');
            onda.className = 'toque-onda';
            onda.style.left = c.x + 'px';
            onda.style.top = c.y + 'px';
            palco.appendChild(onda);
            setTimeout(function () {
                dedo.classList.remove('dedo--tocando');
                el.classList.remove('apertado');
                if (depois) depois(el);
            }, 160);
            setTimeout(function () { onda.remove(); }, 600);
        },

        /** Digita texto num .ui-campo (troca o placeholder) em `duracao` ms. */
        digitar: function (sel, texto, duracao) {
            var el = $(sel), i = 0, passo = duracao / texto.length;
            el.classList.add('ui-campo--foco');
            (function proximo() {
                i++;
                el.innerHTML = escapar(texto.slice(0, i)) + '<span class="ui-cursor"></span>';
                if (i < texto.length) timers.push(setTimeout(proximo, passo));
            })();
        },

        /** Desliza da tela atual pra nova (seletores de .tela). */
        trocarTela: function (de, para) {
            $(de).classList.add('tela--fora-esquerda');
            $(para).classList.remove('tela--fora-direita');
        },

        /** Volta pra tela anterior (a atual sai pela direita). */
        voltarTela: function (de, para) {
            $(de).classList.add('tela--fora-direita');
            $(para).classList.remove('tela--fora-esquerda');
        },

        /** Rola o conteúdo `sel` (translateY) — y em px da tela do celular. */
        rolar: function (sel, y) { $(sel).style.transform = 'translateY(' + (-y) + 'px)'; },

        /** Move `sel` pra antes de `antesDe`, com animação (FLIP). */
        reordenar: function (sel, antesDe) {
            var el = $(sel), lista = el.parentNode, filhos = Array.prototype.slice.call(lista.children);
            var antes = filhos.map(function (f) { return f.getBoundingClientRect().top; });
            lista.insertBefore(el, $(antesDe));
            filhos.forEach(function (f, i) {
                var dy = (antes[i] - f.getBoundingClientRect().top) / escala / ESCALA_CELULAR;
                f.style.transition = 'none';
                f.style.transform = 'translateY(' + dy + 'px)';
                f.offsetHeight; // força o reflow antes de animar
                f.style.transition = 'transform .45s cubic-bezier(.4, 0, .2, 1)';
                f.style.transform = '';
            });
        },

        fecho: function () { $('.fecho').classList.add('fecho--visivel'); }
    };

    window.Motor = {
        cena: function (cfg) {
            palco = document.querySelector('.palco');
            if (params.get('area') === '1') document.documentElement.classList.add('com-area');
            if (RECORTE) document.documentElement.classList.add('modo-recorte');
            if (!$('.titulo')) {
                palco.insertAdjacentHTML('afterbegin', '<div class="titulo"><span class="titulo__etiqueta"></span><span class="titulo__texto"></span></div>');
            }
            var logo = MARCA.logo
                ? '<img class="fecho__logo" src="' + escapar(MARCA.logo) + '" alt="' + escapar(MARCA.nome || '') + '">'
                : '<div class="fecho__nome">' + escapar(MARCA.nome || '') + '</div>';
            palco.insertAdjacentHTML('beforeend',
                '<div class="area-segura"></div><div class="dedo"></div><div class="fala"><span></span></div>' +
                '<div class="fecho">' + logo +
                '<div class="fecho__chamada">' + (cfg.fecho || MARCA.chamada || '') + '</div>' +
                (MARCA.site ? '<div class="fecho__site">' + escapar(MARCA.site) + '</div>' : '') + '</div>');
            dedo = $('.dedo');
            $('.titulo__etiqueta').textContent = cfg.etiqueta || '';
            window.cenaDuracao = cfg.duracao / 1000; // gravar.js lê
            ajustarEscala();
            addEventListener('resize', ajustarEscala);

            function volta() {
                timers.forEach(clearTimeout);
                timers = [];
                $('.fecho').classList.remove('fecho--visivel');
                dedo.classList.remove('dedo--visivel');
                cfg.montar(palco);
                caberTitulo();
                $('.fala span').textContent = '';
                (cfg.falas || []).forEach(function (f) {
                    m.em(f[0], function () { $('.fala span').textContent = f[1]; });
                });
                cfg.roteiro(m);
                if (GRAVAR) m.em(cfg.duracao, function () { window.cenaFim = true; });
                else m.em(cfg.duracao + 800, volta);
            }

            document.fonts.ready.then(function () {
                var t = parseInt(params.get('t') || '', 10);
                if (t >= 0) {
                    // Congela no instante t: roda o roteiro e para os relógios depois.
                    volta();
                    setTimeout(function () { timers.forEach(clearTimeout); }, t);
                    return;
                }
                if (GRAVAR) {
                    // O gravador começa a filmar e chama iniciarCena(): o vídeo
                    // não fica com tempo morto de carregamento no começo.
                    cfg.montar(palco);
                    window.iniciarCena = volta;
                    window.cenaPronta = true;
                    return;
                }
                volta();
            });
        }
    };
})();
