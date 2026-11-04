from pathlib import Path

import pandas as pd
import streamlit as st

from agent import OUTPUT_DIR, run_agent

UPLOAD_DIR = Path("workspace/uploads")

st.set_page_config(page_title="AI Data Analyst Agent", layout="wide")
st.title("AI Data Analyst Agent")
st.caption("Sube un CSV y haz una pregunta. El agente escribe y ejecuta código en un sandbox Docker aislado.")

file = st.file_uploader("Dataset (CSV)", type="csv")
if file:
    st.dataframe(pd.read_csv(file).head())

question = st.text_input("Pregunta")

if file and question and st.button("Analizar"):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    path = UPLOAD_DIR / file.name
    path.write_bytes(file.getvalue())

    steps = []
    answer = ""
    with st.status("Pensando...", expanded=True) as status:
        for kind, content in run_agent(path, question):
            if kind == "thinking":
                status.update(label=f"Pensando... ({len(steps)} pasos hechos)")
            elif kind == "code":
                steps.append({"code": content, "output": ""})
                status.update(label=f"Paso {len(steps)}: ejecutando código...")
                st.markdown(f"**Paso {len(steps)}**")
                st.code(content, language="python")
            elif kind == "output":
                steps[-1]["output"] = content
                st.code(content, language="text")
            else:
                answer = content
        status.update(label="Terminado", state="complete", expanded=False)

    st.session_state.result = {
        "steps": steps,
        "answer": answer,
        "images": [p.read_bytes() for p in sorted(OUTPUT_DIR.glob("*.png"))],
    }
    st.rerun()

result = st.session_state.get("result")
if result:
    with st.expander(f"Ver los {len(result['steps'])} pasos del agente"):
        for i, step in enumerate(result["steps"], 1):
            st.markdown(f"**Paso {i}**")
            st.code(step["code"], language="python")
            st.code(step["output"], language="text")

    st.markdown(result["answer"].replace("$", "\\$"))
    for image in result["images"]:
        st.image(image)