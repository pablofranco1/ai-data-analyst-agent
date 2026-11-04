# AI Data Analyst Agent

Agente que responde preguntas sobre un dataset escribiendo y ejecutando su propio código Python. El código se ejecuta en un contenedor Docker aislado, así que nunca toca la máquina anfitriona.

## Cómo funciona

1. El usuario pasa un CSV y una pregunta.
2. El modelo (Claude) decide qué análisis hacer y escribe código.
3. El código se ejecuta en el sandbox y la salida vuelve al modelo.
4. Si hay un error, el agente lo lee y corrige el código.
5. Cuando tiene la respuesta, devuelve las conclusiones y los gráficos generados.

## Sandbox

Cada ejecución corre en un contenedor nuevo con:

- Sin acceso a red
- Límite de 512 MB de memoria y 1 CPU
- Timeout de 60 segundos
- Solo acceso a la carpeta de trabajo

## Ejemplo

```
python agent.py data/tips.csv "¿Qué día se dejan más propinas en proporción a la cuenta? Haz un gráfico."
```

En el primer intento el código falla por una variable no definida; el agente lee el error y lo corrige en el siguiente paso.

![Propina por día](docs/ejemplo.png)

## Instalación

Requisitos: Python 3.10+, Docker y una API key de Anthropic.

```
git clone https://github.com/pablofranco1/ai-data-analyst-agent.git
cd ai-data-analyst-agent
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
docker build -t agent-sandbox .
```

Crea un archivo `.env` con:

```
ANTHROPIC_API_KEY=tu_api_key
```

## Estructura

- `agent.py`: bucle del agente y uso de herramientas
- `sandbox.py`: ejecución aislada en Docker
- `Dockerfile`: imagen del sandbox
- `data/`: datasets de ejemplo