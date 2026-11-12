import os
from pathlib import Path

import pytest

from sandbox import run_code

DATA = Path("workspace/data")
OUTPUT = Path("workspace/output")


@pytest.fixture(autouse=True)
def carpetas():
    for d in (DATA, OUTPUT):
        d.mkdir(parents=True, exist_ok=True)
        os.chmod(d, 0o777)


def test_ejecuta_codigo():
    assert run_code("print(2 + 2)", DATA, OUTPUT).strip() == "4"


def test_sin_red():
    out = run_code("import urllib.request; urllib.request.urlopen('https://google.com', timeout=5)", DATA, OUTPUT)
    assert "URLError" in out


def test_datos_solo_lectura():
    out = run_code("open('/data/hack.txt', 'w').write('x')", DATA, OUTPUT)
    assert "Read-only file system" in out


def test_sistema_solo_lectura():
    out = run_code("open('/etc/hack.txt', 'w').write('x')", DATA, OUTPUT)
    assert "Read-only file system" in out


def test_usuario_sin_privilegios():
    assert run_code("import os; print(os.getuid())", DATA, OUTPUT).strip() == "1000"


def test_puede_escribir_en_output():
    run_code("open('/output/ok.txt', 'w').write('ok')", DATA, OUTPUT)
    assert (OUTPUT / "ok.txt").read_text() == "ok"


def test_timeout():
    out = run_code("while True: pass", DATA, OUTPUT, timeout=3)
    assert "límite" in out