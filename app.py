import io
import unicodedata
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="TOP Preços", page_icon="🔥", layout="wide")

# ---------- CSS grande ----------
st.markdown("""
<style>
body, div, p, span, label { font-size: 26px !important; }
h1, h2, h3, h4 { font-size: 28px !important; font-weight: bold; }
.stDataFrame tbody td, .stDataFrame thead th { font-size: 26px !important; }
section.main > div { max-width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# ---------- SUA URL publicada (mantém exatamente essa) ----------
DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRLw7a1zV4lrN7q3JbKwKJbOjZ-dzPm3jc1MkFLL6ZfZ1F_B31kve_bDRNsFdpZTDOsUhJMPyL74f9u/pub?gid=1318008819&single=true&output=csv"

# ---------- Utils ----------
def format_brl(x):
    if pd.isna(x): return "-"
    s = f"{float(x):,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")

def norm(s: str) -> str:
    s = str(s or "").strip().lower()
    s = "".join(ch for ch in unicodedata.normalize("NFD", s) if unicodedata.category(ch) != "Mn")
    s = " ".join(s.split())
    return s

# ---------- Carregamento via Sheets (com fallback) ----------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
}

@st.cache_data(ttl=120)
def load_from_google_sheets(url: str) -> pd.DataFrame:
    # 1) tenta a URL 'pub?...&output=csv' com user-agent
    try:
        r = requests.get(url, headers=HEADERS, timeout=25, allow_redirects=True)
        r.raise_for_status()
        return pd.read_csv(io.BytesIO(r.content))
    except Exception as e1:
        # 2) fallback: troca para endpoint gviz (muito estável)
        # aceita tanto urls com /d/e/.../pub?...gid=### quanto /d/<id>/...
        gviz = None
        if "/d/e/" in url and "/pub" in url and "gid=" in url:
            # extrai o /d/e/<ID> e o gid
            base = url.split("/pub")[0]  # .../d/e/<ID>
            gid = url.split("gid=")[-1].split("&")[0]
            gviz = f"{base}/gviz/tq?tqx=out:csv&gid={gid}"
        elif "/d/" in url and "export" in url and "gid=" in url:
            sheet_id = url.split("/d/")[1].split("/")[0]
            gid = url.split("gid=")[-1].split("&")[0]
            gviz = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"

        if gviz:
            r2 = requests.get(gviz, headers=HEADERS, timeout=25, allow_redirects=True)
            r2.raise_for_status()
            return pd.read_csv(io.BytesIO(r2.content))
        # 3) se ainda falhar, propaga o erro original
        raise e1

def padronizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    colmap = {c.strip().lower(): c for c in df.columns}
    def pick(*ops):
        for o in ops:
            if o in colmap: return colmap[o]
        return None
    c_prod = pick("produto")
    c_forn = pick("fornecedor")
    c_val  = pick("valor unitário","valor unitario","preço","preco","valor")
    if not all([c_prod, c_forn, c_val]):
        raise ValueError("Esperava colunas: Produto, Fornecedor, Valor unitário.")
    df = df[[c_prod, c_forn, c_val]].copy()
    df.columns = ["Produto","Fornecedor","Valor unitário"]
    df = df.dropna(subset=["Produto","Fornecedor","Valor unitário"])
    df["Valor unitário"] = (
        df["Valor unitário"].astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace("\u00A0", " ", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df["Valor unitário"] = pd.to_numeric(df["Valor unitário"], errors="coerce")
    df = df.dropna(subset=["Valor unitário"])
    df["__prod_norm"] = df["Produto"].apply(norm)
    df["__forn_norm"] = df["Fornecedor"].apply(norm)
    return df

def deduplicar(df: pd.DataFrame, modo: str) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["__prod_norm","__forn_norm","Valor unitário"], keep="first")
    if modo == "Um preço por fornecedor (menor)":
        df = df.sort_values("Valor unitário").drop_duplicates(
            subset=["__prod_norm","__forn_norm"], keep="first"
        )
    elif modo == "Apenas o menor preço de cada produto":
        df = df.loc[df.groupby("__prod_norm")["Valor unitário"].idxmin()]
    return df

# ---------- UI ----------
st.markdown("## 🔥 TOP Preços")

with st.sidebar:
    st.markdown("### Opções")
    modo_dup = st.selectbox(
        "Tratamento de duplicados:",
        ["Mostrar todos (sem idênticos)", "Um preço por fornecedor (menor)", "Apenas o menor preço de cada produto"],
        index=1
    )
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

# Busca + tabela
busca = st.text_input("Pesquisar produto", placeholder="Ex.: Farinha, Açúcar, Mussarela...")
resultado = df[df["__prod_norm"].str.contains(norm(busca), na=False)] if busca else df.copy()

if resultado.empty:
    st.info("Nenhum item encontrado para o termo buscado.")
else:
    st.subheader("Tabela de preços")
    tabela = resultado[["Produto","Fornecedor","Valor unitário"]].copy()
    tabela["Valor unitário"] = tabela["Valor unitário"].map(format_brl)
    st.dataframe(tabela, hide_index=True, use_container_width=True)
