import io
import unicodedata
import requests
import pandas as pd
import streamlit as st

# =========================
# CONFIG GERAL + TEMA
# =========================
st.set_page_config(page_title="TOP Preços", page_icon="🔥", layout="wide")

# Paleta
ACCENT = "#ff7a1a"     # laranja
BG     = "#0f0f11"     # fundo escuro
CARD   = "#17181b"     # cartões
TEXT   = "#f4f4f4"     # texto principal
MUTED  = "#b9bcc2"     # texto secundário

# CSS: fonte grande + inputs + tabela + cards
st.markdown(f"""
<style>
:root {{
  --accent: {ACCENT};
  --bg: {BG};
  --card: {CARD};
  --text: {TEXT};
  --muted: {MUTED};
}}
html, body, [data-testid="stAppViewContainer"] {{
  background: var(--bg) !important; color: var(--text) !important;
}}
/* Tipografia grande */
body, div, p, span, label {{ font-size: 30px !important; color: var(--text); }}
h1, h2, h3, h4 {{ font-size: 34px !important; font-weight: 800 !important; color: var(--text); }}

/* Inputs */
input, textarea, select {{
  background: var(--card) !important; color: var(--text) !important;
  border: 2px solid #2a2d33 !important; border-radius: 10px !important;
}}
input:focus, textarea:focus, select:focus {{
  outline: none !important; border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(255,122,26,.25) !important;
}}

/* DataFrame mais legível */
.stDataFrame, .stDataFrame table {{ background: var(--card) !important; border-radius: 14px !important; }}
.stDataFrame tbody td, .stDataFrame thead th {{ font-size: 30px !important; padding: 14px 16px !important; color: var(--text) !important; }}

/* Largura total do conteúdo */
section.main > div {{ max-width: 100% !important; padding-right: 24px; }}

/* Cards (modo celular) */
.card {{
  background: var(--card); border: 1px solid #282b30; border-radius: 16px;
  padding: 14px 16px; margin: 8px 0; box-shadow: 0 6px 20px rgba(0,0,0,.35);
}}
.badge {{
  display:inline-block; padding: 2px 10px; border-radius: 999px;
  background: rgba(255,122,26,.18); color: var(--accent); font-weight: 700;
  border: 1px solid rgba(255,122,26,.45); font-size: 26px;
}}
.value {{ font-weight: 800; color: var(--text); }}
.muted {{ color: var(--muted); }}

/* Sidebar */
[data-testid="stSidebar"] {{ background: #121316 !important; border-right: 1px solid #24272d !important; }}
</style>
""", unsafe_allow_html=True)

# =========================
# SUA PLANILHA (CSV publicado)
# =========================
DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRLw7a1zV4lrN7q3JbKwKJbOjZ-dzPm3jc1MkFLL6ZfZ1F_B31kve_bDRNsFdpZTDOsUhJMPyL74f9u/pub?gid=1318008819&single=true&output=csv"

# =========================
# Utils
# =========================
def format_brl(x):
    if pd.isna(x):
        return "-"
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

@st.cache_data(ttl=120)
def load_from_google_sheets(url: str) -> pd.DataFrame:
    """Tenta a URL publicada; se falhar, usa endpoint gviz (out:csv)."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=25, allow_redirects=True)
        r.raise_for_status()
        return pd.read_csv(io.BytesIO(r.content))
    except Exception:
        # fallback gviz
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

def padronizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza nomes e tipos das colunas essenciais."""
    colmap = {c.strip().lower(): c for c in df.columns}

    def pick(*ops):
        for o in ops:
            if o in colmap:
                return colmap[o]
        return None

    c_prod = pick("produto")
    c_forn = pick("fornecedor")
    c_val  = pick("valor unitário", "valor unitario", "preço", "preco", "valor")
    if not all([c_prod, c_forn, c_val]):
        raise ValueError("Esperava colunas: Produto, Fornecedor, Valor unitário.")

    df = df[[c_prod, c_forn, c_val]].copy()
    df.columns = ["Produto", "Fornecedor", "Valor unitário"]
    df = df.dropna(subset=["Produto", "Fornecedor", "Valor unitário"])

    # "R$ 1.234,56" -> 1234.56
    df["Valor unitário"] = (
        df["Valor unitário"].astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace("\u00A0", " ", regex=False)   # NBSP
        .str.replace(".", "", regex=False)         # milhar
        .str.replace(",", ".", regex=False)        # vírgula -> ponto
    )
    df["Valor unitário"] = pd.to_numeric(df["Valor unitário"], errors="coerce")
    df = df.dropna(subset=["Valor unitário"])

    # normalização p/ comparação
    df["__prod_norm"] = df["Produto"].apply(norm)
    df["__forn_norm"] = df["Fornecedor"].apply(norm)
    return df

def deduplicar(df: pd.DataFrame, modo: str) -> pd.DataFrame:
    """Remove duplicatas de acordo com a estratégia escolhida."""
    # remove linhas idênticas (produto+fornecedor+valor)
    df = df.drop_duplicates(subset=["__prod_norm", "__forn_norm", "Valor unitário"], keep="first")

    if modo == "Um preço por fornecedor (menor)":
        df = df.sort_values("Valor unitário").drop_duplicates(
            subset=["__prod_norm", "__forn_norm"], keep="first"
        )
    elif modo == "Apenas o menor preço de cada produto":
        df = df.loc[df.groupby("__prod_norm")["Valor unitário"].idxmin()]
    return df

def render_cards(df_view: pd.DataFrame):
    """Exibe cada linha como um card (ótimo para celular)."""
    for _, row in df_view.iterrows():
        st.markdown(
            f"""
            <div class="card">
              <div class="badge">Produto</div><br>
              <div class="value">{row['Produto']}</div>
              <div class="muted" style="margin-top:6px;">Fornecedor</div>
              <div>{row['Fornecedor']}</div>
              <div class="muted" style="margin-top:6px;">Valor</div>
              <div class="value">{format_brl(row['Valor unitário'])}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# =========================
# INTERFACE
# =========================
st.markdown("## 🔥 TOP Preços")

with st.sidebar:
    st.markdown("### Opções")
    modo_dup = st.selectbox(
        "Tratamento de duplicados:",
        ["Mostrar todos (sem idênticos)", "Um preço por fornecedor (menor)", "Apenas o menor preço de cada produto"],
        index=1
    )
    visu = st.radio("Visualização", ["Tabela", "Cards (celular)"], index=0)
    if st.button("Atualizar dados (limpar cache)"):
        st.cache_data.clear()
        st.experimental_rerun()

# Carrega dados
try:
    df_raw = load_from_google_sheets(DATA_URL)
except Exception as e:
    st.error(f"Erro ao carregar dados do Google Sheets: {e}")
    st.stop()

# Limpa/deduplica
try:
    df = padronizar_colunas(df_raw)
    df = deduplicar(df, modo_dup)
except Exception as e:
    st.error(f"Erro ao padronizar dados: {e}")
    st.write("Colunas encontradas:", list(df_raw.columns))
    st.stop()

st.caption("Fonte: **Google Sheets (publicado como CSV)** — edite a planilha e o site reflete em ~2 min (ou use 'Atualizar dados').")

# Busca
busca = st.text_input("Pesquisar produto", placeholder="Ex.: Farinha, Açúcar, Mussarela...")
resultado = df[df["__prod_norm"].str.contains(norm(busca), na=False)] if busca else df.copy()

# Exibição
if resultado.empty:
    st.info("Nenhum item encontrado para o termo buscado.")
else:
    if visu == "Tabela":
        st.subheader("Tabela de preços")
        tabela = resultado[["Produto", "Fornecedor", "Valor unitário"]].copy()
        tabela["Valor unitário"] = tabela["Valor unitário"].map(format_brl)
        st.dataframe(tabela, hide_index=True, use_container_width=True)
    else:
        st.subheader("Lista de preços")
        render_cards(resultado[["Produto", "Fornecedor", "Valor unitário"]])
