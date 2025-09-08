import io
import unicodedata
import requests
import pandas as pd
import streamlit as st

# =========================
# CONFIG GERAL + TEMA
# =========================
st.set_page_config(
    page_title="TOP Preços", 
    page_icon="🏆", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Paleta baseada na logo: azuis e verdes
PRIMARY = "#4A90A4"      # Azul principal da logo
SECONDARY = "#5BA05B"    # Verde da logo  
ACCENT = "#6BB6FF"       # Azul mais claro
BG = "#1C1C1C"           # Fundo escuro mantido
CARD = "#2A2A2A"         # Cards em cinza escuro
TEXT = "#FFFFFF"         # Texto branco
MUTED = "#B0B0B0"        # Texto mais suave
ECONOMY = "#4CAF50"      # Verde para economia

# CSS otimizado para mobile
st.markdown(f"""
<style>
:root {{
  --primary: {PRIMARY};
  --secondary: {SECONDARY};
  --accent: {ACCENT};
  --bg: {BG};
  --card: {CARD};
  --text: {TEXT};
  --muted: {MUTED};
  --economy: {ECONOMY};
}}

* {{ box-sizing: border-box; }}

html, body, [data-testid="stAppViewContainer"] {{
  background: var(--bg) !important; 
  color: var(--text) !important;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
}}

.main-header {{
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  padding: 20px;
  border-radius: 15px;
  margin-bottom: 25px;
  text-align: center;
  box-shadow: 0 2px 15px rgba(74, 144, 164, 0.15);
}}

.main-header h1 {{
  color: white !important;
  font-size: 2.5rem !important;
  font-weight: 800 !important;
  margin: 0 !important;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}}

.main-header .subtitle {{
  color: rgba(255,255,255,0.9);
  font-size: 1.1rem;
  margin-top: 8px;
  font-weight: 400;
}}

.search-container {{
  background: var(--card);
  padding: 20px;
  border-radius: 15px;
  margin-bottom: 25px;
  border: 1px solid rgba(74, 144, 164, 0.15);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}}

.stTextInput > div > div > input {{
  background: var(--bg) !important;
  color: var(--text) !important;
  border: 2px solid var(--primary) !important;
  border-radius: 25px !important;
  padding: 15px 20px !important;
  font-size: 1.1rem !important;
  font-weight: 500 !important;
}}

.stTextInput > div > div > input:focus {{
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(107, 182, 255, 0.2) !important;
  outline: none !important;
}}

.product-card {{
  background: var(--card);
  border-radius: 12px;
  padding: 20px;
  margin: 15px 0;
  border: 1px solid rgba(74, 144, 164, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}}

.product-card::before {{
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
}}

.product-card:hover {{
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(74, 144, 164, 0.4);
  border-color: var(--primary);
}}

.product-name {{
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 12px;
  line-height: 1.4;
}}

.supplier-info {{
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}}

.supplier-label {{
  background: rgba(74, 144, 164, 0.15);
  color: var(--primary);
  padding: 5px 12px;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-right: 10px;
  border: 1px solid rgba(74, 144, 164, 0.3);
}}

.supplier-name {{
  color: var(--muted);
  font-size: 1.05rem;
  font-weight: 500;
}}

.price-container {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(74, 144, 164, 0.1);
  padding: 15px;
  border-radius: 12px;
  margin-top: 15px;
}}

.price-value {{
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--primary);
  text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
}}

.check-badge {{
  background: var(--economy);
  color: white;
  padding: 5px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}}

/* Card principal de economia centralizado */
.main-stat-card {{
  background: var(--card);
  padding: 40px;
  border-radius: 20px;
  text-align: center;
  border: 2px solid rgba(74, 144, 164, 0.3);
  box-shadow: 0 8px 25px rgba(74, 144, 164, 0.15);
  margin: 30px auto;
  max-width: 400px;
  position: relative;
  overflow: hidden;
}}

.main-stat-card::before {{
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
}}

.main-stat-number {{
  font-size: 3rem;
  font-weight: 900;
  color: var(--primary);
  display: block;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}}

.main-stat-label {{
  color: var(--muted);
  font-size: 1.2rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}}

/* Tabela melhorada para mobile */
.stDataFrame {{
  font-size: 0.9rem !important;
}}

.stDataFrame table {{
  background: var(--card) !important;
  border-radius: 15px !important;
  overflow: hidden !important;
}}

.stDataFrame th {{
  background: var(--primary) !important;
  color: white !important;
  font-weight: 600 !important;
  padding: 15px 10px !important;
  text-align: center !important;
}}

.stDataFrame td {{
  padding: 12px 10px !important;
  border-bottom: 1px solid rgba(74, 144, 164, 0.1) !important;
  text-align: center !important;
}}

/* Sidebar customizada */
[data-testid="stSidebar"] {{
  background: var(--card) !important;
  border-right: 1px solid rgba(74, 144, 164, 0.1) !important;
}}

/* Selectbox e inputs da sidebar */
.stSelectbox > div > div {{
  background: var(--bg) !important;
  border: 1px solid var(--primary) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
}}

/* Botões */
.stButton > button {{
  background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
  color: white !important;
  border: none !important;
  border-radius: 25px !important;
  padding: 12px 25px !important;
  font-weight: 600 !important;
  transition: all 0.3s ease !important;
}}

.stButton > button:hover {{
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 15px rgba(74, 144, 164, 0.3) !important;
}}

.block-container {{
  padding: 20px !important;
  max-width: 100% !important;
}}

/* Loading e mensagens */
.stAlert {{
  border-radius: 15px !important;
  border-left: 4px solid var(--primary) !important;
}}

@media (max-width: 768px) {{
  .main-header h1 {{
    font-size: 2rem !important;
  }}
  .product-card {{
    margin: 10px 0;
    padding: 15px;
  }}
  .price-value {{
    font-size: 1.5rem;
  }}
  .main-stat-card {{
    padding: 30px;
    margin: 20px auto;
  }}
  .main-stat-number {{
    font-size: 2.5rem;
  }}
}}
</style>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES
# =========================
DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRLw7a1zV4lrN7q3JbKwKJbOjZ-dzPm3jc1MkFLL6ZfZ1F_B31kve_bDRNsFdpZTDOsUhJMPyL74f9u/pub?gid=1318008819&single=true&output=csv"
ECONOMIA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRLw7a1zV4lrN7q3JbKwKJbOjZ-dzPm3jc1MkFLL6ZfZ1F_B31kve_bDRNsFdpZTDOsUhJMPyL74f9u/pub?gid=861060469&single=true&output=csv"

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
    try:
        r = requests.get(url, headers=HEADERS, timeout=25, allow_redirects=True)
        r.raise_for_status()
        return pd.read_csv(io.BytesIO(r.content))
    except Exception:
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

@st.cache_data(ttl=120)
def load_economia_value() -> str:
    try:
        df_economia = load_from_google_sheets(ECONOMIA_URL)
        
        if df_economia.empty:
            return "R$ 12,00"
        
        # Busca na célula A2
        if len(df_economia) >= 2 and len(df_economia.columns) >= 1:
            valor_a2 = df_economia.iloc[1, 0]
            if pd.notna(valor_a2) and str(valor_a2).strip():
                return str(valor_a2).strip()
        
        # Busca por coluna com "potencial" e "economia"
        for col in df_economia.columns:
            col_lower = str(col).lower().strip()
            if "potencial" in col_lower and "economia" in col_lower:
                for value in df_economia[col]:
                    if pd.notna(value) and str(value).strip():
                        return str(value).strip()
        
        return "R$ 12,00"
        
    except Exception:
        return "R$ 12,00"

def padronizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    colmap = {c.strip().lower(): c for c in df.columns}

    def pick(*ops):
        for o in ops:
            if o in colmap:
                return colmap[o]
        return None

    c_prod = pick("produto")
    c_forn = pick("fornecedor") 
    c_val = pick("valor unitário", "valor unitario", "preço", "preco", "valor")
    c_econ = pick("potencial de economia", "economia", "potencial economia")
    
    if not all([c_prod, c_forn, c_val]):
        raise ValueError("Esperava colunas: Produto, Fornecedor, Valor unitário.")

    cols_to_keep = [c_prod, c_forn, c_val]
    col_names = ["Produto", "Fornecedor", "Valor unitário"]
    
    if c_econ:
        cols_to_keep.append(c_econ)
        col_names.append("Potencial de economia")

    df = df[cols_to_keep].copy()
    df.columns = col_names
    
    if "Potencial de economia" in df.columns:
        df["Potencial de economia"] = df["Potencial de economia"].astype(str).str.strip()
        df["Potencial de economia"] = df["Potencial de economia"].replace("", None)
    
    df = df.dropna(subset=["Produto", "Fornecedor", "Valor unitário"])

    df["Valor unitário"] = (
        df["Valor unitário"].astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace("\u00A0", " ", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df["Valor unitário"] = pd.to_numeric(df["Valor unitário"], errors="coerce")
    df = df.dropna(subset=["Valor unitário"])

    df["produto_norm"] = df["Produto"].apply(norm)
    df["fornecedor_norm"] = df["Fornecedor"].apply(norm)
    return df

def deduplicar(df: pd.DataFrame, modo: str) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["produto_norm", "fornecedor_norm", "Valor unitário"], keep="first")

    if modo == "Um preço por fornecedor (menor)":
        df = df.sort_values("Valor unitário").drop_duplicates(
            subset=["produto_norm", "fornecedor_norm"], keep="first"
        )
    elif modo == "Apenas o menor preço de cada produto":
        df = df.loc[df.groupby("produto_norm")["Valor unitário"].idxmin()]
    return df

def render_cards_mobile(df_view: pd.DataFrame):
    for _, row in df_view.iterrows():
        st.markdown(f"""
        <div class="product-card">
            <div class="product-name">{row['Produto']}</div>
            <div class="supplier-info">
                <span class="supplier-label">Fornecedor</span>
                <span class="supplier-name">{row['Fornecedor']}</span>
            </div>
            <div class="price-container">
                <span class="price-value">{format_brl(row['Valor unitário'])}</span>
                <span class="check-badge">✅ Disponível</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =========================
# INTERFACE PRINCIPAL
# =========================

st.markdown("""
<div class="main-header">
    <h1>🏆 TOP Preços</h1>
    <div class="subtitle">Os melhores preços de panificação toda segunda-feira</div>
</div>
""", unsafe_allow_html=True)

try:
    df_raw = load_from_google_sheets(DATA_URL)
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")
    st.stop()

try:
    df = padronizar_colunas(df_raw)
    df_original = df.copy()
    st.success("✅ Dados carregados com sucesso!")
    st.info("💡 Os preços listados são referenciais obtidos através de cotações. Entre em contato com seu representante comercial para confirmar disponibilidade e condições especiais.")
except Exception as e:
    st.error(f"❌ Erro ao processar dados: {e}")
    st.write("Colunas encontradas:", list(df_raw.columns))
    st.stop()

with st.sidebar:
    st.markdown("### ⚙ Configurações")
    modo_dup = st.selectbox(
        "Filtro de preços:",
        ["Mostrar todos", "Um preço por fornecedor (menor)", "Apenas o menor preço de cada produto"],
        index=1
    )
    visu = st.radio("Visualização:", ["Cards (Mobile)", "Tabela"], index=0)
    
    st.markdown("---")
    if st.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.rerun()

df = deduplicar(df, modo_dup)

# Carrega valor de economia da segunda página
valor_economia = load_economia_value()

# CARD PRINCIPAL CENTRALIZADO - POTENCIAL DE ECONOMIA
st.markdown(f"""
<div class="main-stat-card">
    <span class="main-stat-number">{valor_economia}</span>
    <div class="main-stat-label">Potencial de Economia</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="search-container">', unsafe_allow_html=True)
busca = st.text_input("🔍 Pesquisar produto", placeholder="Digite o nome do produto (ex: Farinha, Açúcar...)")
st.markdown('</div>', unsafe_allow_html=True)

if busca:
    resultado = df[df["produto_norm"].str.contains(norm(busca), na=False)]
else:
    resultado = df.copy()

if resultado.empty:
    st.markdown("""
    <div style="text-align: center; padding: 40px; background: var(--card); border-radius: 15px; margin: 20px 0;">
        <h3 style="color: var(--muted);">🔍 Nenhum produto encontrado</h3>
        <p style="color: var(--muted);">Tente buscar por outro termo ou verifique a ortografia.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    resultado = resultado.sort_values(['Produto', 'Valor unitário'])
    
    if visu == "Cards (Mobile)":
        st.markdown(f"### 📋 Lista de Preços ({len(resultado)} itens)")
        render_cards_mobile(resultado[["Produto", "Fornecedor", "Valor unitário"]])
    else:
        st.markdown(f"### 📊 Tabela de Preços ({len(resultado)} itens)")
        display_cols = ["Produto", "Fornecedor", "Valor unitário"]
        tabela = resultado[display_cols].copy()
        tabela["Valor unitário"] = tabela["Valor unitário"].map(format_brl)
        st.dataframe(tabela, hide_index=True, use_container_width=True)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--muted); padding: 20px;">
    📊 Dados atualizados automaticamente do Google Sheets<br>
    🔄 Última atualização em cache: 2 minutos<br>
    📱 Interface otimizada para dispositivos móveis
</div>
""", unsafe_allow_html=True)