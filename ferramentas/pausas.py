"""
Acha as pausas da voz em audio/<cena>.wav e sugere o `falas` da cena
(legenda sincronizada), já no tempo do VÍDEO (+ atraso_fala_ms).

O texto de reels.json > falas é quebrado na pontuação (, . : ; ! ?) e cada
trecho é casado, em ordem, com um trecho de voz entre pausas. Se a voz tiver
mais trechos que o texto, as pausas mais curtas são juntadas; se tiver menos,
trechos de texto vizinhos são juntados pelo tamanho (caracteres × tempo).

Uso (da pasta do projeto):  python <skill>/ferramentas/pausas.py <cena> [pausa_min_ms (padrão 80)]
Cole a linha "falas:" impressa no Motor.cena da cena. Trecho longo demais
pra legenda (> ~45 caracteres)? Quebre em dois na pausa interna mais próxima
(a lista de pausas mostra todas).
"""
import array
import json
import re
import sys
import wave

from comum import caminho, config

JANELA_MS = 20


def energia(arquivo):
    with wave.open(arquivo) as w:
        if w.getsampwidth() != 2:
            raise SystemExit('Esperado WAV 16 bits (o locucao.py gera assim).')
        canais, taxa = w.getnchannels(), w.getframerate()
        a = array.array('h', w.readframes(w.getnframes()))
    if canais > 1:
        a = a[::canais]
    passo = int(taxa * JANELA_MS / 1000)
    return [max(map(abs, a[i:i + passo])) for i in range(0, len(a) - passo, passo)]


def trechos_de_voz(en, pausa_min):
    limiar = max(en) * 0.04
    voz = [e >= limiar for e in en]
    trechos, i = [], 0
    while i < len(voz):
        if voz[i]:
            j = i
            while j < len(voz) and voz[j]:
                j += 1
            trechos.append([i * JANELA_MS, j * JANELA_MS])
            i = j
        else:
            i += 1
    # junta trechos separados por silêncio curto (respiração, consoante)
    juntos = []
    for t in trechos:
        if juntos and t[0] - juntos[-1][1] < pausa_min:
            juntos[-1][1] = t[1]
        else:
            juntos.append(t)
    return juntos


def agrupar(partes, voz):
    """Junta trechos de texto consecutivos pra caber nos trechos de voz,
    casando a fatia de caracteres de cada grupo com a fatia de tempo (DP)."""
    total_c = sum(len(p) for p in partes)
    total_t = sum(b - a for a, b in voz)
    n, k = len(partes), len(voz)
    acum = [0]
    for p in partes:
        acum.append(acum[-1] + len(p))
    inf = float('inf')
    custo = [[inf] * (k + 1) for _ in range(n + 1)]
    volta = [[0] * (k + 1) for _ in range(n + 1)]
    custo[0][0] = 0
    for j in range(1, k + 1):
        alvo = (voz[j - 1][1] - voz[j - 1][0]) / total_t
        for i in range(j, n - (k - j) + 1):
            for h in range(j - 1, i):
                c = custo[h][j - 1] + abs((acum[i] - acum[h]) / total_c - alvo)
                if c < custo[i][j]:
                    custo[i][j], volta[i][j] = c, h
    grupos, i = [], n
    for j in range(k, 0, -1):
        h = volta[i][j]
        grupos.append(' '.join(partes[h:i]))
        i = h
    return grupos[::-1]


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    cena = sys.argv[1]
    pausa_min = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    cfg = config()
    atraso = cfg.get('atraso_fala_ms', 300)
    acelerar = cfg.get('acelerar', {}).get(cena, 1)
    voz = trechos_de_voz(energia(caminho('audio', f'{cena}.wav')), pausa_min)
    voz = [[round(a / acelerar), round(b / acelerar)] for a, b in voz]
    voz = [v for v in voz if v[1] - v[0] >= 120] or voz

    print('Trechos de voz (ms do vídeo):')
    for a, b in voz:
        print(f'  {a + atraso:>6} – {b + atraso:<6}')
    print(f'Fim da fala: {voz[-1][1] + atraso} ms (o fecho/duração da cena deve vir depois)')

    texto = cfg.get('falas', {}).get(cena, '')
    partes = [p.strip() for p in re.findall(r'[^,.:;!?]+[,.:;!?]*', texto) if p.strip()]
    if not partes:
        return
    while len(voz) > len(partes):
        # junta o par separado pela pausa mais curta
        k = min(range(len(voz) - 1), key=lambda i: voz[i + 1][0] - voz[i][1])
        voz[k:k + 2] = [[voz[k][0], voz[k + 1][1]]]
    if len(voz) < len(partes):
        partes = agrupar(partes, voz)
    falas = [[max(0, a + atraso - 50), p] for (a, _), p in zip(voz, partes)]
    falas.append([voz[-1][1] + atraso + 300, ''])
    print('\nSugestão (cole no Motor.cena):')
    print('falas: ' + json.dumps(falas, ensure_ascii=False).replace('"', "'") + ',')


if __name__ == '__main__':
    main()
