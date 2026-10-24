"""
Cria um projeto de vídeo novo a partir do modelo da skill:

    <pasta>/
      reels.json   voz, atraso da fala, texto da locução de cada cena
      marca.js     nome, logo, site e chamada do fecho
      marca.css    cores da marca (variáveis do motor)
      motor/       motor.js + base.css (cópia; atualize com --motor)
      cenas/       uma cena = um vídeo (demo.html de exemplo)
      audio/  gravacoes/  mp4/

Uso:  python <skill>/ferramentas/novo.py <pasta>           cria
      python <skill>/ferramentas/novo.py <pasta> --motor   só atualiza motor/
"""
import os
import shutil
import sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    destino = os.path.abspath(sys.argv[1])
    so_motor = '--motor' in sys.argv[2:]
    if not so_motor and os.path.exists(os.path.join(destino, 'reels.json')):
        raise SystemExit(f'{destino} já é um projeto (use --motor pra só atualizar o motor).')

    if not so_motor:
        shutil.copytree(os.path.join(SKILL, 'modelo'), destino, dirs_exist_ok=True)
        for pasta in ('audio', 'gravacoes', 'mp4'):
            os.makedirs(os.path.join(destino, pasta), exist_ok=True)
    shutil.copytree(os.path.join(SKILL, 'motor'), os.path.join(destino, 'motor'), dirs_exist_ok=True)
    print(f'{"Motor atualizado" if so_motor else "Projeto criado"} em {destino}')


if __name__ == '__main__':
    main()
