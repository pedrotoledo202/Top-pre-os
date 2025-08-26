import io
import unicodedata
import requests
import pandas as pd
import streamlit as st

# =========================================
# Configurações gerais
# =========================================
st.set_page_config(page_title="TOP Preços", page_icon="🔥", layout="wide")

# CSS: fonte grande + tabela 100% largura
st.markdown("""
<style>
body, div, p, span, label { font-size: 26px !important; }
h1, h2, h3, h4 { font-size: 28px !important; font-weight: bold; }
.stDataFrame tbody td { font-size: 26px !important; }
.stDataFrame thead th { font-size: 26px !important; }
section.main > div { max-width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# =========================================
# Config - SUA URL do Google Sheets publicado como CSV
# =========================================
DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRLw7a1zV4lrN7q3JbKwKJbOjZ-dzPm3jc1MkFLL6ZfZ1F_B31kve_bDRNsFdpZTDOsUhJMPyL74f9u/pub?gid=1318008819&single=true&output=csv"

# =========================================
# Utilidades
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

# =========================================
# Carregamento de dados SOMENTE via Google Sheets
# =========================================
@st.cache_data(ttl=120)  # cache de 2 minutos
def load_from_google_sheets(url: str) -> pd.DataFrame:
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    content = resp.content
    df = pd.read_csv(io.BytesIO(content))
    return df

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
    # remove linhas idênticas (produto+fornecedor+valor)
    df = df.drop_duplicates(subset=["__prod_norm","__forn_norm","Valor unitário"], keep="first")

    if modo == "Um preço por fornecedor (menor)":
        # mantém o menor preço por (produto, fornecedor)
        df = df.sort_values("Valor unitário").drop_duplicates(
            subset=["__prod_norm","__forn_norm"], keep="first"
        )
    elif modo == "Apenas o menor preço de cada produto":
        df = df.loc[df.groupby("__prod_norm")["Valor unitário"].idxmin()]
    return df

# =========================================
# Interface
# =========================================
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

# Carrega dados da planilha
try:
    df_raw = load_from_google_sheets(DATA_URL)
except Exception as e:
    st.error(f"Erro ao carregar dados do Google Sheets: {e}")
    st.stop()

# Limpa/padroniza e deduplica
try:
    df = padronizar_colunas(df_raw)
    df = deduplicar(df, modo_dup)
except Exception as e:
    st.error(f"Erro ao padronizar dados: {e}")
    st.write("Colunas encontradas:", list(df_raw.columns))
    st.stop()

st.caption("Fonte de dados: **Google Sheets (URL pública)** — edite a planilha e o site atualiza automaticamente.")

# Busca
busca = st.text_input("Pesquisar produto", placeholder="Ex.: Farinha, Açúcar, Mussarela...")
resultado = df[df["__prod_norm"].str.contains(norm(busca), na=False)] if busca else df.copy()

if resultado.empty:
    st.info("Nenhum item encontrado para o termo buscado.")
    st.stop()

# Tabela final
st.subheader("Tabela de preços")
tabela = resultado[["Produto","Fornecedor","Valor unitário"]].copy()
tabela["Valor unitário"] = tabela["Valor unitário"].map(format_brl)
st.dataframe(tabela, hide_index=True, use_container_width=True)
