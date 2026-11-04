import shutil
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from sandbox import run_code

load_dotenv()
client = anthropic.Anthropic()

MODEL = "claude-sonnet-5-5"
DATA_DIR = Path("workspace/data")
OUTPUT_DIR = Path("workspace/output")

SYSTEM = """Eres un analista de datos. Tienes un dataset en /data/{file} (solo lectura).
Para analizarlo, escribe código Python y ejecútalo con la herramienta run_python.
Tienes pandas y matplotlib. Guarda los gráficos como PNG en /output.
Cada ejecución empieza desde cero: carga los datos e importa las librerías en cada bloque.
Si el código falla, lee el error y corrígelo.
No menciones rutas de archivos: los gráficos se muestran al usuario automáticamente.
Cuando tengas la respuesta, explica las conclusiones en español, de forma breve."""

TOOLS = [{
    "name": "run_python",
    "description": "Ejecuta código Python en un contenedor aislado y devuelve la salida.",
    "input_schema": {
        "type": "object",
        "properties": {"code": {"type": "string"}},
        "required": ["code"],
    },
}]


def run_agent(dataset, question, max_steps=10):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    OUTPUT_DIR.mkdir(parents=True)
    filename = Path(dataset).name
    shutil.copy(dataset, DATA_DIR / filename)

    messages = [{"role": "user", "content": question}]

    for _ in range(max_steps):
        yield "thinking", None
        response = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            system=SYSTEM.format(file=filename),
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            yield "answer", "".join(b.text for b in response.content if b.type == "text")
            return

        results = []
        for block in response.content:
            if block.type == "tool_use":
                code = block.input["code"]
                yield "code", code
                output = run_code(code, DATA_DIR, OUTPUT_DIR)
                yield "output", output
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })
        messages.append({"role": "user", "content": results})

    yield "answer", "Límite de pasos alcanzado sin respuesta final."


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Uso: python agent.py datos.csv "tu pregunta"')
        sys.exit(1)

    for kind, content in run_agent(sys.argv[1], sys.argv[2]):
        if kind == "code":
            print(f"\n--- Ejecutando ---\n{content}\n")
        elif kind == "output":
            print(content[:1000])
        else:
            print("\n=== Respuesta ===\n" + content)