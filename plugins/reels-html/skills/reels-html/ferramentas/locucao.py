"""
Gera a locução de cada cena (reels.json > falas) em audio/<cena>.wav
(48 kHz) e mostra a duração — a fala precisa terminar antes do fecho.

Provedores (reels.json > voz.provedor):
  - edge:   grátis, sem conta (python -m pip install edge-tts).
            Vozes: edge-tts --list-voices (ex.: pt-BR-FranciscaNeural, pt-BR-AntonioNeural).
  - google: Google Cloud Text-to-Speech (python -m pip install google-auth requests).
            Credencial pelo gcloud (gcloud auth application-default login) ou
            GOOGLE_APPLICATION_CREDENTIALS; projeto em GOOGLE_CLOUD_PROJECT ou
            voz.projeto. Vozes ex.: pt-BR-Chirp3-HD-Leda. Nunca grave a
            credencial no projeto.

Uso (da pasta do projeto):  python <skill>/ferramentas/locucao.py [cena...]
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
    return base64.b64decode(r.json()['audioContent'])  # WAV pronto


def voz_edge(texto, voz):
    try:
        import edge_tts
    except ImportError:
        raise SystemExit('Falta o edge-tts: python -m pip install edge-tts')
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
            print(f'{cena}: sem fala em reels.json > falas')
            continue
        arquivo = caminho('audio', f'{cena}.wav')
        with open(arquivo, 'wb') as f:
            f.write(gerar(texto, voz))
        with wave.open(arquivo) as w:
            duracao = w.getnframes() / w.getframerate()
        print(f'{cena}: audio/{cena}.wav — {duracao:.1f} s')


if __name__ == '__main__':
    main()
