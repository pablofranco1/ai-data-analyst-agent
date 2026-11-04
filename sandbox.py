from pathlib import Path

import docker

IMAGE = "agent-sandbox"
client = docker.from_env()


def run_code(code, workspace, timeout=60):
    workspace = Path(workspace).resolve()
    (workspace / "script.py").write_text(code, encoding="utf-8")

    container = client.containers.run(
        IMAGE,
        "python script.py",
        volumes={str(workspace): {"bind": "/workspace", "mode": "rw"}},
        working_dir="/workspace",
        network_disabled=True,
        mem_limit="512m",
        nano_cpus=1_000_000_000,
        detach=True,
    )

    try:
        container.wait(timeout=timeout)
        output = container.logs().decode("utf-8", errors="replace")
    except Exception:
        container.kill()
        output = f"Error: el código superó el límite de {timeout} segundos."
    finally:
        container.remove(force=True)

    return output[-5000:] or "(sin salida)"