import io
import unicodedata
import requests
import pandas as pd
import streamlit as st

# =========================================
# CONFIG GERAL + TEMA
# =========================================
st.set_page_config(page_title="TOP Preços", page_icon="🔥", layout="wide")

# Paleta
ACCENT = "#ff7a1a"     # laranja claro
BG     = "#0f0f11"     # preto/cinza-escuro do fundo
CARD   = "#17181b"     # painéis/caixas
TEXT   = "#f4f4f4"     # texto principal
MUTED  = "#b9bcc2"     # texto secundário

# CSS: fonte grande + tabela ampla + inputs e botões com laranja
st.markdown(f"""
<style>
/* Base */
:root {{
  --accent: {ACCENT};
  --bg: {BG};
  --card: {CARD};
  --text: {TEXT};
  --muted: {MUTED};
}}
html, body, [data-testid="stAppViewContainer"] {{
  background: var(--bg) !important;
  color: var(--text) !important;
}}
/* Tipografia grande */
body, div, p, span, label {{
  font-size: 30px !important;
  color: var(--text);
}}
h1, h2, h3, h4 {{
  font-size: 34px !important;
  font-weight: 800 !important;
  color: var(--text);
}}
/* Título com linha laranja */
.section-title {{
  display:flex; align-items:center; gap:.6rem; margin: .25rem 0 1rem 0;
}}
.section-title:before {{
  content: ""; display:block; width:14px; height:14px; border-radius:50%;
  background: var(--accent);
}}
/* Inputs */
input, textarea, select {{
  background: var(--card) !important;
  color: var(--text) !important;
  border: 2px solid #2a2d33 !important;
  border-radius: 10px !important;
}}
input:focus, textarea:focus, select:focus {{
  outline: none !important;
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(255,122,26,.25) !important;
}}
/* DataFrame mais legível */
.stDataFrame, .stDataFrame table {{
  background: var(--card) !important;
  border-radius: 14px !important;
}}
.stDataFrame tbody td, .stDataFrame thead th {{
  font-size: 30px !important;
  padding: 14px 16px !important;
  color: var(--text) !important;
}}
/* Largura total do conteúdo */
section.main > div {{ max-width: 100% !important; padding-right: 24px; }}
/* Cards para modo celular */
.card {{
  background: var(--card);
  border: 1px solid #282b30;
  border-radius: 16px;
  padding: 14px 16px;
  margin: 8px 0;
  box-shadow: 0 6px 20px rgba(0,0,0,.35);
}}
.badge {{
  display:inline-block; padding: 2px 10px; border-radius: 999px;
  background: rgba(255,122,26,.18); color: var(--accent); font-weight: 700;
  border: 1px solid rgba(255,122,26,.45);
  font-size: 26px;
}}
.value {{
  font-weight: 800; color: var(--text);
}}
.muted {{ color: var(--muted); }}
/* Sidebar */
[data-testid="stSidebar"] {{
  background: #121316 !important;
  border-right: 1px solid #24272d !important;
}}
</style>
""", unsafe_allow_html=True)

# =========================================
# SUA PLANILHA (CSV publicado)
# =========================================
DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRLw7a1zV4lrN7q3JbKwKJbOjZ-dzPm3jc1MkFLL6ZfZ1F_B31kve_bDRNsFdpZTDOsUhJMPyL74f9u/pub?gid=1318008819&single=true&output=csv"

# =========================================
# Utils
# =========================================
def format_brl(x):
    if pd.isna(x): return "-"
    s = f"{float(x):,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")

def norm(s: str) -> str:
    s = str(s or "").strip().lower()
    s = "".join(ch for ch in unicodedata.normalize("NFD", s) if unicodedata.category(ch) != "Mn")
    s = " ".join(s.split())
    return s

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
}

@st.cache_data(ttl=120)  # ~2 min de cache
def load_from_google_sheets(url: str) -> pd.DataFrame:
    # 1) tenta URL publicada
    try:
        r = requests.get(url, headers=HEADERS, timeout=25, allow_redirects=True)
        r.raise_for_status()
        return pd.read_csv(io.BytesIO(r.content))
    except Exception:
        # 2) fallback gviz
        gid = url.split("gid=")[-1].split("&")[0] if "gid=" in url else "0"
        if "/d/e/" in url:
            base = url.split("/pub")[0]
            gviz = f"{base}/gviz/tq?tqx=out:csv&gid={gid}"
        elif "/d/" in url:
            sheet_id = url.split("/d/")[1].split("/")[0]
            gviz = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
        else:
            raise
        r2 = requests.get(gviz, headers=HEADERS, timeout=25, allow_redirects=True)
        r2.raise_for_status()
        return pd.read_csv(io.BytesIO(r2.content))

def padronizar_colunas(df: pd.DataFrame
