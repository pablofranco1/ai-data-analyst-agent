from pathlib import Path

import docker

IMAGE = "agent-sandbox"
client = docker.from_env()


def run_code(code, data_dir, output_dir, timeout=60):
    container = client.containers.run(
        IMAGE,
        ["python", "-c", code],
        volumes={
            str(Path(data_dir).resolve()): {"bind": "/data", "mode": "ro"},
            str(Path(output_dir).resolve()): {"bind": "/output", "mode": "rw"},
        },
        working_dir="/output",
        user="sandbox",
        network_disabled=True,
        read_only=True,
        tmpfs={"/tmp": "size=64m"},
        mem_limit="512m",
        nano_cpus=1_000_000_000,
        pids_limit=64,
        cap_drop=["ALL"],
        security_opt=["no-new-privileges"],
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