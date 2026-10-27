"""
Finds the pauses in the voice in audio/<scene>.wav and suggests the scene's `falas`
(synced captions), already in VIDEO time (+ atraso_fala_ms).

The text in reels.json > falas is split at punctuation (, . : ; ! ?) and each
chunk is matched, in order, with a voice chunk between pauses. If the voice has
more chunks than the text, the shortest pauses are merged; if it has fewer,
neighboring text chunks are merged by size (characters × time).

Usage (from the project folder):  python <skill>/ferramentas/pausas.py <scene> [min_pause_ms (default 80)]
Paste the printed "falas:" line into the scene's Motor.cena. Chunk too long
for a caption (> ~45 characters)? Split it in two at the nearest inner pause
(the pause list shows them all).
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
            raise SystemExit('Expected a 16-bit WAV (locucao.py produces that).')
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
    # merge chunks separated by a short silence (breath, consonant)
    juntos = []
    for t in trechos:
        if juntos and t[0] - juntos[-1][1] < pausa_min:
            juntos[-1][1] = t[1]
        else:
            juntos.append(t)
    return juntos


def agrupar(partes, voz):
    """Merges consecutive text chunks to fit the voice chunks,
    matching each group's share of characters to its share of time (DP)."""
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

    print('Voice chunks (video ms):')
    for a, b in voz:
        print(f'  {a + atraso:>6} – {b + atraso:<6}')
    print(f'End of narration: {voz[-1][1] + atraso} ms (the outro/scene duration must come after it)')

    texto = cfg.get('falas', {}).get(cena, '')
    partes = [p.strip() for p in re.findall(r'[^,.:;!?]+[,.:;!?]*', texto) if p.strip()]
    if not partes:
        return
    while len(voz) > len(partes):
        # merge the pair separated by the shortest pause
        k = min(range(len(voz) - 1), key=lambda i: voz[i + 1][0] - voz[i][1])
        voz[k:k + 2] = [[voz[k][0], voz[k + 1][1]]]
    if len(voz) < len(partes):
        partes = agrupar(partes, voz)
    falas = [[max(0, a + atraso - 50), p] for (a, _), p in zip(voz, partes)]
    falas.append([voz[-1][1] + atraso + 300, ''])
    print('\nSuggestion (paste into Motor.cena):')
    print('falas: ' + json.dumps(falas, ensure_ascii=False).replace('"', "'") + ',')


if __name__ == '__main__':
    main()
