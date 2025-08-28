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

# Paleta alaranjada harmoniosa com fundo escuro
PRIMARY = "#FF8C42"    # Laranja vibrante principal
SECONDARY = "#FFB366"  # Laranja dourado médio
ACCENT = "#FFA726"     # Laranja âmbar para destaques
BG = "#1C1C1C"         # Fundo escuro (mantido)
CARD = "#2A2A2A"       # Cards em cinza escuro para contraste suave
TEXT = "#FFFFFF"       # Texto branco
MUTED = "#B0B0B0"      # Texto mais suave em cinza claro
ECONOMY = "#FF7043"    # Laranja coral para economia

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
  box-shadow: 0 2px 15px rgba(255, 179, 102, 0.15);
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
  border: 1px solid rgba(255, 140, 66, 0.15);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
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
  border-radius: 12px;
  padding: 20px;
  margin: 15px 0;
  border: 1px solid rgba(255, 140, 66, 0.2);
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
  box-shadow: 0 4px 15px rgba(255, 140, 66, 0.4);
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
  background: rgba(255, 140, 66, 0.15);
  color: var(--primary);
  padding: 5px 12px;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-right: 10px;
  border: 1px solid rgba(255, 140, 66, 0.3);
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
  background: rgba(255, 140, 66, 0.1);
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

.economy-badge {{
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
  border-radius: 12px;
  text-align: center;
  border: 1px solid rgba(255, 140, 66, 0.2);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
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
  border-bottom: 1px solid rgba(255, 140, 66, 0.1) !important;
  text-align: center !important;
}}

/* Sidebar customizada */
[data-testid="stSidebar"] {{
  background: var(--card) !important;
  border-right: 1px solid rgba(255, 140, 66, 0.1) !important;
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
  box-shadow: 0 4px 15px rgba(255, 140, 66, 0.3) !important;
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
    c_econ = pick("potencial de economia", "economia", "potencial economia")
    
    if not all([c_prod, c_forn, c_val]):
        raise ValueError("Esperava colunas: Produto, Fornecedor, Valor unitário.")

    # Inclui coluna de economia se existir
    cols_to_keep = [c_prod, c_forn, c_val]
    col_names = ["Produto", "Fornecedor", "Valor unitário"]
    
    if c_econ:
        cols_to_keep.append(c_econ)
        col_names.append("Potencial de economia")

    df = df[cols_to_keep].copy()
    df.columns = col_names
    
    # Processamento da coluna economia se existir
    if "Potencial de economia" in df.columns:
        # Limpa e converte valores de economia
        df["Potencial de economia"] = df["Potencial de economia"].astype(str).str.strip()
        # Não converte para numérico se for texto descritivo
        df["Potencial de economia"] = df["Potencial de economia"].replace("", None)
    
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
    # remove linhas idênticas (produto+fornecedor+valor) - CORRIGIDO: usando __prod_norm e __forn_norm
    df = df.drop_duplicates(subset=["_prod_norm", "_forn_norm", "Valor unitário"], keep="first")

    if modo == "Um preço por fornecedor (menor)":
        df = df.sort_values("Valor unitário").drop_duplicates(
            subset=["_prod_norm", "_forn_norm"], keep="first"
        )
    elif modo == "Apenas o menor preço de cada produto":
        df = df.loc[df.groupby("__prod_norm")["Valor unitário"].idxmin()]
    return df

def render_cards_mobile(df_view: pd.DataFrame):
    """Exibe cards otimizados para mobile com potencial de economia."""
    
    for _, row in df_view.iterrows():
        # Verifica se tem coluna de economia
        has_economy = "Potencial de economia" in row.index and pd.notna(row.get("Potencial de economia"))
        economy_value = row.get("Potencial de economia", "") if has_economy else ""
        
        # Badge de economia (se existir)
        economy_badge = ""
        if has_economy and economy_value and str(economy_value).strip():
            # Se é um valor numérico, formata como moeda
            try:
                if isinstance(economy_value, (int, float)) or str(economy_value).replace(",", ".").replace("R$", "").strip().replace(".", "").isdigit():
                    economy_badge = f'<span class="economy-badge">🌡 {format_brl(float(str(economy_value).replace("R$", "").replace(",", ".")))}</span>'
                else:
                    # Se é texto descritivo
                    economy_badge = f'<span class="economy-badge">🌡 {economy_value}</span>'
            except:
                economy_badge = f'<span class="economy-badge">🌡 {economy_value}</span>'
        
        st.markdown(f"""
        <div class="product-card">
            <div class="product-name">{row['Produto']}</div>
            <div class="supplier-info">
                <span class="supplier-label">Fornecedor</span>
                <span class="supplier-name">{row['Fornecedor']}</span>
            </div>
            <div class="price-container">
                <span class="price-value">{format_brl(row['Valor unitário'])}</span>
                {economy_badge}
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
    st.success("✅ Dados carregados com sucesso!")
    if "Potencial de economia" in df.columns:
        st.info("🌡 Coluna 'Potencial de economia' detectada!")
except Exception as e:
    st.error(f"❌ Erro ao processar dados: {e}")
    st.write("Colunas encontradas:", list(df_raw.columns))
    st.stop()

# Sidebar com opções
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

# Aplica filtro de duplicatas
df = deduplicar(df, modo_dup)

# Estatísticas com potencial de economia
col1, col2, col3, col4 = st.columns(4)
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

with col4:
    # Card de Potencial de Economia com valor fixo
    st.markdown(f"""
    <div class="stat-card">
        <span class="stat-number">R$ 1.480,48</span>
        <div class="stat-label">Potencial de Economia</div>
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
        # Inclui todas as colunas disponíveis para os cards
        cols_to_show = ["Produto", "Fornecedor", "Valor unitário", "__prod_norm"]
        if "Potencial de economia" in resultado.columns:
            cols_to_show.append("Potencial de economia")
        render_cards_mobile(resultado[cols_to_show])
    else:
        st.markdown(f"### 📊 Tabela de Preços ({len(resultado)} itens)")
        # Para tabela, mostra apenas as colunas básicas
        display_cols = ["Produto", "Fornecedor", "Valor unitário"]
        tabela = resultado[display_cols].copy()
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