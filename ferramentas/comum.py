"""Funções comuns das ferramentas (rode todas de dentro da pasta do projeto de vídeo)."""
import json
import os
import sys

PROJETO = os.getcwd()

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')


def config():
    arquivo = os.path.join(PROJETO, 'reels.json')
    if not os.path.exists(arquivo):
        raise SystemExit('reels.json não encontrado: rode de dentro da pasta do projeto (crie com novo.py).')
    with open(arquivo, encoding='utf-8') as f:
        return json.load(f)


def caminho(*partes):
    return os.path.join(PROJETO, *partes)


def ffmpeg():
    try:
        import imageio_ffmpeg
    except ImportError:
        raise SystemExit('Falta o ffmpeg portátil: python -m pip install imageio-ffmpeg')
    return imageio_ffmpeg.get_ffmpeg_exe()


def cenas_pedidas(cfg):
    """Cenas da linha de comando ou, sem argumento, todas as de reels.json > falas."""
    return sys.argv[1:] or list(cfg.get('falas', {}))
