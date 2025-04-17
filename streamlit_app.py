# streamlit_app.py

import os
import pandas as pd
import streamlit as st
from openai import OpenAI

# —————— CONFIG ——————
# Locally: set OPENAI_API_KEY in your shell.
# On Streamlit Cloud: put it under Settings → Secrets → OPENAI_API_KEY
api_key = os.getenv("OPEN_API_KEY")
if not api_key:
    st.error("Chyba: Nenalezeno OPENAI_API_KEY. Nastavte ho jako env var nebo v Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = """
Jsi specializovaný asistent, který zpracovává Excelové tabulky obsahující následující sloupce:

- "Oblast řešení" (typicky sloupec 4 v původním Excelu)
- "Řešení" (sloupec 5)
- "Owner" (sloupec 12)
- "Marketingová fáze" (sloupec 15)
- "Důvod stavu" (sloupec 18)

Úkolem je provést následující analýzu:

1) Vyčti všechny řádky z nahraného Excelu.
2) Pro každý řádek urč "BU" = 
   - Pokud "Oblast řešení" není prázdná, použij ji.
   - Jinak pokud "Řešení" není prázdné, použij "Řešení".
   - Jinak použij "Owner".

3) Spočti:
   - Celkový počet leadů (všech řádků v Excelu).
   - Počet "servisních" leadů (kde "Důvod stavu" == "Servis").
   - Počet "SQL" = řádky, kde "Marketingová fáze" je jedna z: "40 - SQL", "50 - Develop", "60 - Propose", "70 - Close".
   - Počet "MQL" = řádky, kde "Marketingová fáze" je jedna z: "10 - See", "20 - Think", "30 - Do".
   - Počet "Zrušeno" = řádky, kde "Důvod stavu" == "Zrušeno".

4) Vytvoř tabulku "Počet leadů dle BU":
   - Každý řádek tabulky bude jedna unikátní hodnota BU.
   - Vedle názvu BU uveď "celkový počet leadů / počet servisních".
   - Seřaď tabulku sestupně podle celkového počtu leadů.

5) Finálně vygeneruj **stručný report** v této podobě:

---------------------------------------------------
Lead Management [aktuální měsíc a rok] v číslech

Počet leadů dle BU
Celkový počet přijatých Leadů je XXX.
Z toho je YYY servisních (uvedeno za lomítkem).

[Zde vlož tabulku dle bodu 4]

-------------
- ??? příležitostí (SQL)
- ??? stále neklasifikováno (MQL)
- ??? Zrušeno
---------------------------------------------------

6) Svou odpověď formátuj tak, aby člověk získal stručný, přehledný text s tabulkou a se shrnutím funnelu (SQL, MQL, Zrušeno).

7) Pokud by nějaký sloupec nebo hodnota chyběly, sděl uživateli, že data nelze kompletně zpracovat, ale zpracuj to, co je k dispozici.

8) Po zpracování Excelu vrať výsledek (tzn. report ve formátu uvedeném výše).

Dodrž tento formát a neposílej uživateli žádné další „programátorské“ instrukce. V odpovědi poskytni pouze hotový report.
"""

# —————— STREAMLIT UI ——————
st.set_page_config(page_title="Lead‑Analysis", layout="centered")
st.title("📊 Lead‑Analysis")

uploaded_file = st.file_uploader("Nahraj Excel (xls/xlsx)", type=["xls", "xlsx"])

if st.button("Spustit analýzu"):
    if not uploaded_file:
        st.warning("Nejprve nahrajte soubor.")
        st.stop()

    # 1) Load Excel
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Board")
    except Exception as e:
        st.error(f"Chyba při čtení Excelu: {e}")
        st.stop()

    # 2) Serialize data for the assistant
    records = df.to_dict(orient="records")
    messages = [
        {"role": "system",  "content": SYSTEM_PROMPT},
        {"role": "user",    "content": f"Data ve formátu JSON:\n{records}"}
    ]

    # 3) Call OpenAI
    with st.spinner("Analyzuji…"):
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0
            )
        except Exception as e:
            st.error(f"Chyba API: {e}")
            st.stop()

    # 4) Show report
    report = completion.choices[0].message.content.strip()
    st.subheader("📈 Výstupní report")
    st.markdown(report)
