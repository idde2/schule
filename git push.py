import subprocess
from datetime import datetime

GIT = r"C:\Program Files\Git\cmd\git.exe"

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

def auto_commit_push():
    ts = datetime.now().strftime("%d.%m.%y %H:%M")
    run(f'"{GIT}" add .')
    run(f'"{GIT}" commit -m "{ts}"')
    run(f'"{GIT}" push origin master')

auto_commit_push()
