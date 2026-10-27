"""
Generates the narration for each scene (reels.json > falas) in audio/<scene>.wav
(48 kHz) and shows its duration — the narration must end before the outro.

Providers (reels.json > voz.provedor):
  - edge:   free, no account (python -m pip install edge-tts).
            Voices: edge-tts --list-voices (e.g. en-US-AvaNeural, en-US-AndrewNeural).
  - google: Google Cloud Text-to-Speech (python -m pip install google-auth requests).
            Credentials via gcloud (gcloud auth application-default login) or
            GOOGLE_APPLICATION_CREDENTIALS; project in GOOGLE_CLOUD_PROJECT or
            voz.projeto. Voices e.g. en-US-Chirp3-HD-Leda. Never store the
            credentials in the project.

Usage (from the project folder):  python <skill>/ferramentas/locucao.py [scene...]
"""
import asyncio
import base64
import os
import subprocess
import tempfile
import wave

from comum import caminho, cenas_pedidas, config, ffmpeg


def voz_google(texto, voz):
    import google.auth
    from google.auth.transport.requests import AuthorizedSession

    cred, projeto_padrao = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
    sessao = AuthorizedSession(cred)
    projeto = voz.get('projeto') or os.environ.get('GOOGLE_CLOUD_PROJECT') or projeto_padrao
    if projeto:
        sessao.headers['x-goog-user-project'] = projeto
    idioma = voz.get('idioma') or '-'.join(voz['nome'].split('-')[:2])
    r = sessao.post('https://texttospeech.googleapis.com/v1/text:synthesize', json={
        'input': {'text': texto},
        'voice': {'languageCode': idioma, 'name': voz['nome']},
        'audioConfig': {'audioEncoding': 'LINEAR16', 'sampleRateHertz': 48000},
    })
    if r.status_code != 200:
        raise RuntimeError(f'Google TTS {r.status_code}: {r.text[:300]}')
    return base64.b64decode(r.json()['audioContent'])  # ready-made WAV


def voz_edge(texto, voz):
    try:
        import edge_tts
    except ImportError:
        raise SystemExit('Missing edge-tts: python -m pip install edge-tts')
    with tempfile.TemporaryDirectory() as tmp:
        mp3, wav = os.path.join(tmp, 'fala.mp3'), os.path.join(tmp, 'fala.wav')
        asyncio.run(edge_tts.Communicate(texto, voz['nome'], rate=voz.get('velocidade', '+0%')).save(mp3))
        subprocess.run([ffmpeg(), '-y', '-loglevel', 'error', '-i', mp3, '-ar', '48000', '-ac', '1', wav], check=True)
        with open(wav, 'rb') as f:
            return f.read()


def main():
    cfg = config()
    voz = cfg['voz']
    gerar = {'google': voz_google, 'edge': voz_edge}[voz.get('provedor', 'edge')]
    os.makedirs(caminho('audio'), exist_ok=True)
    for cena in cenas_pedidas(cfg):
        texto = cfg['falas'].get(cena)
        if not texto:
            print(f'{cena}: no narration in reels.json > falas')
            continue
        arquivo = caminho('audio', f'{cena}.wav')
        with open(arquivo, 'wb') as f:
            f.write(gerar(texto, voz))
        with wave.open(arquivo) as w:
            duracao = w.getnframes() / w.getframerate()
        print(f'{cena}: audio/{cena}.wav — {duracao:.1f} s')


if __name__ == '__main__':
    main()
