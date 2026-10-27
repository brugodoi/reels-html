"""
Creates a new video project from the skill's template:

    <folder>/
      reels.json   voice, narration delay, narration text for each scene
      marca.js     brand name, logo, site and outro call to action
      marca.css    brand colors (engine variables)
      motor/       motor.js + base.css (a copy; refresh with --motor)
      cenas/       one scene = one video (demo.html as an example)
      audio/  gravacoes/  mp4/

Usage:  python <skill>/ferramentas/novo.py <folder>           create
        python <skill>/ferramentas/novo.py <folder> --motor   only refresh motor/
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
        raise SystemExit(f'{destino} is already a project (use --motor to only refresh the engine).')

    if not so_motor:
        shutil.copytree(os.path.join(SKILL, 'modelo'), destino, dirs_exist_ok=True)
        for pasta in ('audio', 'gravacoes', 'mp4'):
            os.makedirs(os.path.join(destino, pasta), exist_ok=True)
    shutil.copytree(os.path.join(SKILL, 'motor'), os.path.join(destino, 'motor'), dirs_exist_ok=True)
    print(f'{"Engine refreshed" if so_motor else "Project created"} in {destino}')


if __name__ == '__main__':
    main()
