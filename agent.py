import shutil
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from sandbox import run_code

load_dotenv()
client = anthropic.Anthropic()

MODEL = "claude-sonnet-5-5"
WORKSPACE = Path("workspace")

SYSTEM = """Eres un analista de datos. Tienes un dataset en /workspace/{file}.
Para analizarlo, escribe código Python y ejecútalo con la herramienta run_python.
Tienes pandas y matplotlib. Guarda los gráficos como PNG en /workspace.
Si el código falla, lee el error y corrígelo.
Cada ejecución empieza desde cero: carga los datos e importa las librerías en cada bloque.
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


def ask(dataset, question, max_steps=10):
    WORKSPACE.mkdir(exist_ok=True)
    filename = Path(dataset).name
    shutil.copy(dataset, WORKSPACE / filename)

    messages = [{"role": "user", "content": question}]

    for _ in range(max_steps):
        response = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            system=SYSTEM.format(file=filename),
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        results = []
        for block in response.content:
            if block.type == "tool_use":
                code = block.input["code"]
                print(f"\n--- Ejecutando ---\n{code}\n")
                output = run_code(code, WORKSPACE)
                print(output[:1000])
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })
        messages.append({"role": "user", "content": results})

    return "Límite de pasos alcanzado sin respuesta final."


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Uso: python agent.py datos.csv "tu pregunta"')
        sys.exit(1)
    print("\n=== Respuesta ===\n" + ask(sys.argv[1], sys.argv[2]))