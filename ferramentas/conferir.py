"""
Tira N quadros do mp4/<cena>.mp4 (padrão 6, espalhados do começo ao fim)
e junta numa imagem só (mp4/<cena>-quadros.png) pra conferir título,
legenda, botões e fecho sem assistir o vídeo inteiro.

Uso (da pasta do projeto):  python <skill>/ferramentas/conferir.py <cena> [n | ms,ms,...]
  ex.: conferir.py demo 8      → 8 quadros espalhados
       conferir.py demo 500,4200,9900 → nesses instantes (ms)
"""
import os
import subprocess
import sys

from comum import caminho, ffmpeg


def duracao(arquivo):
    saida = subprocess.run([ffmpeg(), '-i', arquivo], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
    h, m, s = saida.split('Duration: ')[1].split(',')[0].split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def juntar(n):
    return ''.join(f'[q{i}]' for i in range(n)) + (f'hstack=inputs={n}' if n > 1 else 'null')


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    cena = sys.argv[1]
    video = caminho('mp4', f'{cena}.mp4')
    arg = sys.argv[2] if len(sys.argv) > 2 else '6'
    if ',' in arg:
        instantes = [int(x) / 1000 for x in arg.split(',')]
    else:
        n, total = int(arg), duracao(video)
        instantes = [total * (i + 0.5) / n for i in range(n)]
    entradas = []
    for t in instantes:
        entradas += ['-ss', f'{t:.3f}', '-i', video]
    n = len(instantes)
    filtro = ''.join(f'[{i}:v]scale=270:-1,drawtext=text=\'{t:.1f}s\':x=8:y=8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6[q{i}];'
                     for i, t in enumerate(instantes))
    filtro += juntar(n)
    saida = caminho('mp4', f'{cena}-quadros.png')
    comando = [ffmpeg(), '-y', '-loglevel', 'error'] + entradas + ['-filter_complex', filtro, '-frames:v', '1', saida]
    try:
        subprocess.run(comando, check=True, stderr=subprocess.DEVNULL)  # fontconfig avisa à toa no Windows
    except subprocess.CalledProcessError:
        # ffmpeg sem drawtext (fonte): repete sem o carimbo de tempo
        filtro = ''.join(f'[{i}:v]scale=270:-1[q{i}];' for i in range(n))
        filtro += juntar(n)
        subprocess.run([ffmpeg(), '-y', '-loglevel', 'error'] + entradas + ['-filter_complex', filtro, '-frames:v', '1', saida], check=True)
    print(f'{cena}: {os.path.relpath(saida)} — instantes: ' + ', '.join(f'{t:.1f}s' for t in instantes))


if __name__ == '__main__':
    main()
