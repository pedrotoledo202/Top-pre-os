import os
import unicodedata
import pandas as pd
import streamlit as st

st.set_page_config(page_title="TOP Preços", page_icon="🔥", layout="wide")

# ---- CSS para ampliar fonte e expandir tabela ----
st.markdown("""
<style>
/* tamanho padrão dos textos */
body, div, p, span, label {
    font-size: 26px !important;
}

/* cabeçalhos (subheader, títulos, etc.) */
h1, h2, h3, h4 {
    font-size: 28px !important;
    font-weight: bold;
}

/* tabela */
.stDataFrame tbody td {
    font-size: 26px !important;
}
.stDataFrame thead th {
    font-size: 26px !important;
}

/* faz a tabela ocupar toda a largura */
section.main > div { max-width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# -------------------- Utilidades --------------------
def format_brl(x):
    if pd.isna(x): return "-"
    s = f"{float(x):,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")

def norm(s: str) -> str:
    s = str(s or "").strip().lower()
    s = "".join(ch for ch in unicodedata.normalize("NFD", s) if unicodedata.category(ch) != "Mn")
    s = " ".join(s.split())
    return s

# -------------------- Carregamento --------------------
@st.cache_data(ttl=300)
def load_local_file():
    candidatos = [
        "lista - Sheet1.csv",
        "lista.csv",
        "lista - Sheet1.xlsx",
        "lista.xlsx",
        "cotacao_limpa.xlsx",
    ]
    for nome in candidatos:
        if os.path.exists(nome):
            if nome.lower().endswith(".csv"):
                df = pd.read_csv(nome)
            else:
                df = pd.read_excel(nome)
            return df, nome
    return None, None

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

# -------------------- Interface --------------------
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

df_raw, origem = load_local_file()
if df_raw is None:
    st.warning("Não encontrei arquivo local. Faça upload de CSV/XLSX:")
    up = st.file_uploader("Envie sua lista", type=["csv","xlsx"])
    if up is None:
        st.stop()
    df_raw = pd.read_csv(up) if up.name.lower().endswith(".csv") else pd.read_excel(up)
    origem = up.name

try:
    df = padronizar_colunas(df_raw)
    df = deduplicar(df, modo_dup)
except Exception as e:
    st.error(f"Erro ao padronizar dados: {e}")
    st.write("Colunas encontradas:", list(df_raw.columns))
    st.stop()

st.caption(f"Fonte de dados: **{origem}**")

# -------------------- Busca e Tabela --------------------
busca = st.text_input("Pesquisar produto", placeholder="Ex.: Farinha, Açúcar, Mussarela...")
resultado = df[df["__prod_norm"].str.contains(norm(busca), na=False)] if busca else df.copy()

if resultado.empty:
    st.info("Nenhum item encontrado para o termo buscado.")
    st.stop()

st.subheader("Tabela de preços")
tabela = resultado[["Produto","Fornecedor","Valor unitário"]].copy()
tabela["Valor unitário"] = tabela["Valor unitário"].map(format_brl)
st.dataframe(tabela, hide_index=True, use_container_width=True)
