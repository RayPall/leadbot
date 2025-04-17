import os
import streamlit as st
import requests

st.set_page_config(page_title="Lead Analysis", layout="centered")
st.title("📊 Lead Management Analyzer")

uploaded_file = st.file_uploader(
    "Nahraj Excel (xls/xlsx)",
    type=["xls", "xlsx"]
)

if st.button("Spustit analýzu"):
    if not uploaded_file:
        st.warning("Nejprve nahrajte soubor.")
    else:
        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        }
        headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}

        with st.spinner("Analyzuji…"):
            response = requests.post(
                "https://<YOUR-APP-URL>/analyze",  # we’ll replace this after deploy
                headers=headers,
                files=files
            )

        if response.ok:
            report = response.json().get("analysis", "")
            st.subheader("📈 Výstupní report")
            st.markdown(report)
        else:
            st.error(f"Chyba API {response.status_code}: {response.text}")
