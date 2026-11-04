from pathlib import Path

from sandbox import run_code

data = Path("workspace/data")
output = Path("workspace/output")
data.mkdir(parents=True, exist_ok=True)
output.mkdir(parents=True, exist_ok=True)

attacks = {
    "Acceso a internet": "import urllib.request; urllib.request.urlopen('https://google.com', timeout=5)",
    "Modificar los datos": "open('/data/hack.txt', 'w').write('x')",
    "Escribir en el sistema": "open('/etc/hack.txt', 'w').write('x')",
    "Usuario (0 = root)": "import os; print(os.getuid())",
}

for name, code in attacks.items():
    print(f"--- {name} ---")
    print(run_code(code, data, output)[-200:])