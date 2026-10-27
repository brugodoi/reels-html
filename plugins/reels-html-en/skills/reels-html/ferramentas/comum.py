"""Shared helpers for the tools (run all of them from inside the video project folder)."""
import json
import os
import sys

PROJETO = os.getcwd()

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')


def config():
    arquivo = os.path.join(PROJETO, 'reels.json')
    if not os.path.exists(arquivo):
        raise SystemExit('reels.json not found: run from inside the project folder (create it with novo.py).')
    with open(arquivo, encoding='utf-8') as f:
        return json.load(f)


def caminho(*partes):
    return os.path.join(PROJETO, *partes)


def ffmpeg():
    try:
        import imageio_ffmpeg
    except ImportError:
        raise SystemExit('Missing portable ffmpeg: python -m pip install imageio-ffmpeg')
    return imageio_ffmpeg.get_ffmpeg_exe()


def cenas_pedidas(cfg):
    """Scenes from the command line or, with no argument, all of reels.json > falas."""
    return sys.argv[1:] or list(cfg.get('falas', {}))
