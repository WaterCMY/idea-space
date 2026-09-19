import os, shutil, subprocess, sys
from pathlib import Path
root = Path(__file__).resolve().parent
for command in [[sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v']]:
    result = subprocess.run(command, cwd=root)
    if result.returncode: sys.exit(result.returncode)
print('All regression checks passed.')
