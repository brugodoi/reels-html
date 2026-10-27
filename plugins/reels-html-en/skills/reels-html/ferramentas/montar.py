"""
Joins the recording (gravacoes/<scene>/, from gravar.js) with the narration
(audio/<scene>.wav, from locucao.py) into an MP4 ready for social media:
1080×1920, H.264 30 fps, AAC 48 kHz, in mp4/<scene>.mp4.

- The duration comes from gravacoes/<scene>/duracao.txt (= duracao in Motor.cena).
- The voice starts at reels.json > atraso_fala_ms; reels.json > acelerar
  ({"scene": 1.06}) speeds up narration that would run into the outro.
- With no audio for the scene, a silent video is produced (useful to check the visuals).
- Portable ffmpeg from the imageio-ffmpeg package.

Usage (from the project folder):  python <skill>/ferramentas/montar.py <scene> [scene...]
"""
import os
import subprocess

from comum import caminho, cenas_pedidas, config, ffmpeg


def montar(cena, cfg):
    pasta = caminho('gravacoes', cena)
    if not os.path.exists(os.path.join(pasta, 'lista.txt')):
        print(f'{cena}: record it first (gravar.js {cena})')
        return
    with open(os.path.join(pasta, 'duracao.txt'), encoding='utf-8') as f:
        duracao = float(f.read())
    audio = caminho('audio', f'{cena}.wav')
    saida = caminho('mp4', f'{cena}.mp4')
    os.makedirs(os.path.dirname(saida), exist_ok=True)

    comando = [ffmpeg(), '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', os.path.join(pasta, 'lista.txt')]
    if os.path.exists(audio):
        atraso = int(cfg.get('atraso_fala_ms', 300))
        filtro_audio = f'adelay={atraso}|{atraso},apad'
        acelerar = cfg.get('acelerar', {}).get(cena)
        if acelerar:
            filtro_audio = f'atempo={acelerar},' + filtro_audio
        comando += ['-i', audio, '-filter_complex', f'[0:v]fps=30,format=yuv420p[v];[1:a]{filtro_audio}[a]',
                    '-map', '[v]', '-map', '[a]', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000']
    else:
        print(f'{cena}: no audio/{cena}.wav — silent video')
        comando += ['-vf', 'fps=30,format=yuv420p']
    comando += ['-t', str(duracao), '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-profile:v', 'high',
                '-movflags', '+faststart', saida]
    subprocess.run(comando, check=True)
    print(f'{cena}: mp4/{cena}.mp4 ({os.path.getsize(saida) / 1024 / 1024:.1f} MB, {duracao:.1f} s)')


if __name__ == '__main__':
    cfg = config()
    for cena in cenas_pedidas(cfg):
        montar(cena, cfg)
