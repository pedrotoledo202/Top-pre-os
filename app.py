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
    page_icon="🔥", 
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar fechada por padrão no mobile
)

# Paleta moderna alaranjada
PRIMARY = "#FF6B35"    # Laranja vibrante principal
SECONDARY = "#FF8A5B"  # Laranja mais suave
ACCENT = "#FFD23F"     # Amarelo dourado para destaques
BG = "#1A1A1A"         # Fundo escuro principal
CARD = "#2D2D2D"       # Cards com contraste suave
TEXT = "#FFFFFF"       # Texto principal branco puro
MUTED = "#B8B8B8"      # Texto secundário
SUCCESS = "#4CAF50"    # Verde para menor preço

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
  --success: {SUCCESS};
}}

/* Reset e base */
* {{ box-sizing: border-box; }}

html, body, [data-testid="stAppViewContainer"] {{
  background: var(--bg) !important; 
  color: var(--text) !important;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
}}

/* Header customizado */
.main-header {{
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  padding: 20px;
  border-radius: 15px;
  margin-bottom: 25px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(255, 107, 53, 0.3);
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

/* Search box melhorado */
.search-container {{
  background: var(--card);
  padding: 20px;
  border-radius: 15px;
  margin-bottom: 25px;
  border: 2px solid rgba(255, 107, 53, 0.2);
}}

/* Input de busca estilizado */
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
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.2) !important;
  outline: none !important;
}}

/* Cards de produtos - design mobile-first */
.product-card {{
  background: var(--card);
  border-radius: 20px;
  padding: 20px;
  margin: 15px 0;
  border: 2px solid rgba(255, 107, 53, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
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
  height: 4px;
  background: linear-gradient(90deg, var(--primary), var(--accent));
}}

.product-card:hover {{
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(255, 107, 53, 0.2);
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
  background: rgba(255, 107, 53, 0.15);
  color: var(--primary);
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-right: 10px;
  border: 1px solid rgba(255, 107, 53, 0.3);
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
  background: rgba(255, 107, 53, 0.1);
  padding: 15px;
  border-radius: 15px;
  margin-top: 15px;
}}

.price-value {{
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--primary);
  text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
}}

.best-price {{
  background: rgba(76, 175, 80, 0.15);
  border: 2px solid var(--success);
}}

.best-price .price-value {{
  color: var(--success);
}}

.best-badge {{
  background: var(--success);
  color: white;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}}

/* Stats container */
.stats-container {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 25px;
}}

.stat-card {{
  background: var(--card);
  padding: 20px;
  border-radius: 15px;
  text-align: center;
  border: 2px solid rgba(255, 107, 53, 0.1);
}}

.stat-number {{
  font-size: 2rem;
  font-weight: 800;
  color: var(--primary);
  display: block;
}}

.stat-label {{
  color: var(--muted);
  font-size: 0.9rem;
  margin-top: 5px;
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
  border-bottom: 1px solid rgba(255, 107, 53, 0.1) !important;
  text-align: center !important;
}}

/* Sidebar customizada */
.css-1d391kg {{
  background: var(--card) !important;
}}

/* Selectbox e inputs da sidebar */
.stSelectbox > div > div {{
  background: var(--bg) !important;
  border: 1px solid var(--primary) !important;
  border-radius: 10px !important;
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
  box-shadow: 0 8px 25px rgba(255, 107, 53, 0.4) !important;
}}

/* Remover padding extra do container principal */
.block-container {{
  padding: 20px !important;
  max-width: 100% !important;
}}

/* Responsividade mobile */
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
  
  .stats-container {{
    grid-template-columns: repeat(2, 1fr);
  }}
}}

/* Loading e mensagens */
.stAlert {{
  border-radius: 15px !important;
  border-left: 4px solid var(--primary) !important;
}}
</style>
""", unsafe_allow_html=True)

# =========================
# SUA PLANILHA (CSV publicado)
# =========================
DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRLw7a1zV4lrN7q3JbKwKJbOjZ-dzPm3jc1MkFLL6ZfZ1F_B31kve_bDRNsFdpZTDOsUhJMPyL74f9u/pub?gid=1318008819&single=true&output=csv"

# =========================
# Utils (mantidas suas funções originais)
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

def render_cards_mobile(df_view: pd.DataFrame):
    """Exibe cards otimizados para mobile com destaque para menores preços."""
    # Identifica os menores preços por produto
    min_prices = df_view.groupby("__prod_norm")["Valor unitário"].min().to_dict()
    
    for _, row in df_view.iterrows():
        produto_norm = row["__prod_norm"]
        is_best_price = row["Valor unitário"] == min_prices.get(produto_norm, float('inf'))
        
        card_class = "product-card best-price" if is_best_price else "product-card"
        
        best_badge = '<span class="best-badge">Melhor Preço</span>' if is_best_price else ""
        
        st.markdown(f"""
        <div class="{card_class}">
            <div class="product-name">{row['Produto']}</div>
            <div class="supplier-info">
                <span class="supplier-label">Fornecedor</span>
                <span class="supplier-name">{row['Fornecedor']}</span>
            </div>
            <div class="price-container">
                <span class="price-value">{format_brl(row['Valor unitário'])}</span>
                {best_badge}
            </div>
        </div>
        """, unsafe_allow_html=True)

# =========================
# INTERFACE PRINCIPAL
# =========================

# Header customizado
st.markdown("""
<div class="main-header">
    <h1>🔥 TOP Preços</h1>
    <div class="subtitle">Os melhores preços de panificação toda segunda-feira</div>
</div>
""", unsafe_allow_html=True)

# Carrega dados
try:
    df_raw = load_from_google_sheets(DATA_URL)
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")
    st.stop()

# Limpa/deduplica
try:
    df = padronizar_colunas(df_raw)
    df_original = df.copy()  # Guarda cópia para estatísticas
except Exception as e:
    st.error(f"❌ Erro ao processar dados: {e}")
    st.write("Colunas encontradas:", list(df_raw.columns))
    st.stop()

# Sidebar com opções
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
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

# Aplica filtro de duplicatas
df = deduplicar(df, modo_dup)

# Estatísticas rápidas
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="stat-card">
        <span class="stat-number">{len(df)}</span>
        <div class="stat-label">Produtos</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    fornecedores_unicos = df['Fornecedor'].nunique()
    st.markdown(f"""
    <div class="stat-card">
        <span class="stat-number">{fornecedores_unicos}</span>
        <div class="stat-label">Fornecedores</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if not df.empty:
        menor_preco = df['Valor unitário'].min()
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">{format_brl(menor_preco)}</span>
            <div class="stat-label">Menor Preço</div>
        </div>
        """, unsafe_allow_html=True)

# Container de busca
st.markdown('<div class="search-container">', unsafe_allow_html=True)
busca = st.text_input("🔍 Pesquisar produto", placeholder="Digite o nome do produto (ex: Farinha, Açúcar...)")
st.markdown('</div>', unsafe_allow_html=True)

# Filtra resultados
if busca:
    resultado = df[df["__prod_norm"].str.contains(norm(busca), na=False)]
else:
    resultado = df.copy()

# Exibição dos resultados
if resultado.empty:
    st.markdown("""
    <div style="text-align: center; padding: 40px; background: var(--card); border-radius: 15px; margin: 20px 0;">
        <h3 style="color: var(--muted);">🔍 Nenhum produto encontrado</h3>
        <p style="color: var(--muted);">Tente buscar por outro termo ou verifique a ortografia.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Ordenar por produto e depois por preço
    resultado = resultado.sort_values(['Produto', 'Valor unitário'])
    
    if visu == "Cards (Mobile)":
        st.markdown(f"### 📋 Lista de Preços ({len(resultado)} itens)")
        render_cards_mobile(resultado[["Produto", "Fornecedor", "Valor unitário", "__prod_norm"]])
    else:
        st.markdown(f"### 📊 Tabela de Preços ({len(resultado)} itens)")
        tabela = resultado[["Produto", "Fornecedor", "Valor unitário"]].copy()
        tabela["Valor unitário"] = tabela["Valor unitário"].map(format_brl)
        st.dataframe(tabela, hide_index=True, use_container_width=True)

# Footer informativo
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--muted); padding: 20px;">
    📊 Dados atualizados automaticamente do Google Sheets<br>
    🔄 Última atualização em cache: 2 minutos<br>
    📱 Interface otimizada para dispositivos móveis
</div>
""", unsafe_allow_html=True)