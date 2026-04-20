# ============================================================
#  Analizador de Acciones Bursátiles — Streamlit Web App
#  Autor: Ana Fernanda Navarro
#  Descripción: Análisis técnico con SMA, RSI y señales de
#               cruce. Interfaz web interactiva con Streamlit.
# ============================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ── Configuración de página ──────────────────────────────────
st.set_page_config(
    page_title="Analizador de Acciones",
    page_icon="📈",
    layout="wide"
)

# ── Estilos ──────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #FAFAFA; }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #EEE;
        text-align: center;
    }
    h1 { color: #1A1612; }
</style>
""", unsafe_allow_html=True)

# ── Parámetros ───────────────────────────────────────────────
SMA_CORTO       = 20
SMA_LARGO       = 50
RSI_PERIODO     = 14
RSI_SOBREVENTA  = 30
RSI_SOBRECOMPRA = 70

# ── Funciones ────────────────────────────────────────────────
def obtener_datos(ticker, periodo):
    try:
        data = yf.Ticker(ticker).history(period=periodo)
        if data.empty:
            return None
        return data
    except:
        return None

def calcular_sma(cierre, ventana):
    return cierre.rolling(window=ventana).mean()

def calcular_rsi(cierre, periodo=RSI_PERIODO):
    delta    = cierre.diff()
    ganancias = delta.clip(lower=0)
    perdidas  = -delta.clip(upper=0)
    media_gan = ganancias.ewm(com=periodo - 1, min_periods=periodo).mean()
    media_per = perdidas.ewm(com=periodo - 1, min_periods=periodo).mean()
    rs  = media_gan / media_per
    rsi = 100 - (100 / (1 + rs))
    return rsi.round(2)

def detectar_cruces(sma_corto, sma_largo):
    senal_compra = (sma_corto > sma_largo) & (sma_corto.shift(1) <= sma_largo.shift(1))
    senal_venta  = (sma_corto < sma_largo) & (sma_corto.shift(1) >= sma_largo.shift(1))
    return senal_compra, senal_venta

def graficar(cierre, indicadores, ticker):
    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        figsize=(13, 7),
        gridspec_kw={"height_ratios": [3, 1]},
        sharex=True,
        facecolor="#FAFAFA"
    )
    fig.suptitle(f"Análisis técnico: {ticker}",
                 fontsize=14, fontweight="bold", y=0.98)

    ax1.set_facecolor("#FAFAFA")
    ax1.plot(cierre,               color="#1565C0", lw=1.6, label="Precio cierre", zorder=3)
    ax1.plot(indicadores["sma20"], color="#F57C00", lw=1.2, ls="--", label=f"SMA {SMA_CORTO}", zorder=2)
    ax1.plot(indicadores["sma50"], color="#C62828", lw=1.2, ls="--", label=f"SMA {SMA_LARGO}", zorder=2)

    compras = cierre[indicadores["senal_compra"]]
    if not compras.empty:
        ax1.scatter(compras.index, compras.values,
                    marker="^", color="#2E7D32", s=100, zorder=4,
                    label=f"Golden cross ({indicadores['n_compras']})")

    ventas = cierre[indicadores["senal_venta"]]
    if not ventas.empty:
        ax1.scatter(ventas.index, ventas.values,
                    marker="v", color="#B71C1C", s=100, zorder=4,
                    label=f"Death cross ({indicadores['n_ventas']})")

    ax1.set_ylabel("Precio (USD)", fontsize=10)
    ax1.legend(loc="upper left", fontsize=9, framealpha=0.7)
    ax1.grid(alpha=0.25, linestyle="--")
    ax1.spines[["top", "right"]].set_visible(False)

    ax2.set_facecolor("#FAFAFA")
    ax2.plot(indicadores["rsi"], color="#6A1B9A", lw=1.3, label="RSI 14")
    ax2.axhline(RSI_SOBRECOMPRA, color="#C62828", lw=0.8, ls="--")
    ax2.axhline(RSI_SOBREVENTA,  color="#2E7D32", lw=0.8, ls="--")
    ax2.fill_between(indicadores["rsi"].index, RSI_SOBRECOMPRA, 100, alpha=0.07, color="#C62828")
    ax2.fill_between(indicadores["rsi"].index, 0, RSI_SOBREVENTA, alpha=0.07, color="#2E7D32")
    ax2.text(indicadores["rsi"].index[-1], RSI_SOBRECOMPRA + 1, "sobrecompra", fontsize=7.5, color="#C62828", ha="right")
    ax2.text(indicadores["rsi"].index[-1], RSI_SOBREVENTA - 3, "sobreventa",  fontsize=7.5, color="#2E7D32", ha="right")
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("RSI", fontsize=10)
    ax2.grid(alpha=0.25, linestyle="--")
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=15, ha="right", fontsize=8)
    plt.tight_layout()
    return fig

# ── Interfaz ─────────────────────────────────────────────────
st.title("📈 Analizador de Acciones Bursátiles")
st.markdown("Análisis técnico con **SMA 20/50**, **RSI 14** y detección de señales de cruce. Desarrollado por **Ana Fernanda Navarro**.")
st.divider()

col1, col2 = st.columns([2, 1])
with col1:
    ticker = st.text_input("🔍 Ingresá el ticker", value="AAPL", placeholder="Ej: AAPL, MSFT, GGAL.BA, TSLA").strip().upper()
with col2:
    periodo = st.selectbox("📅 Período", ["3mo", "6mo", "1y", "2y"], index=1,
                           format_func=lambda x: {"3mo":"3 meses","6mo":"6 meses","1y":"1 año","2y":"2 años"}[x])

analizar = st.button("Analizar →", type="primary", use_container_width=False)

if analizar and ticker:
    with st.spinner(f"Descargando datos de {ticker}..."):
        data = obtener_datos(ticker, periodo)

    if data is None:
        st.error(f"❌ No se encontraron datos para **{ticker}**. Verificá el ticker e intentá de nuevo.")
    else:
        cierre = data["Close"]
        sma20  = calcular_sma(cierre, SMA_CORTO)
        sma50  = calcular_sma(cierre, SMA_LARGO)
        rsi    = calcular_rsi(cierre)
        senal_compra, senal_venta = detectar_cruces(sma20, sma50)

        metricas = {
            "maximo":      round(float(cierre.max()), 2),
            "minimo":      round(float(cierre.min()), 2),
            "media":       round(float(cierre.mean()), 2),
            "volatilidad": round(float(cierre.std()), 2),
            "retorno_pct": round(((float(cierre.iloc[-1]) / float(cierre.iloc[0])) - 1) * 100, 2),
        }

        indicadores = {
            "sma20":        sma20,
            "sma50":        sma50,
            "rsi":          rsi,
            "rsi_actual":   round(float(rsi.iloc[-1]), 2),
            "senal_compra": senal_compra,
            "senal_venta":  senal_venta,
            "n_compras":    int(senal_compra.sum()),
            "n_ventas":     int(senal_venta.sum()),
        }

        # ── KPIs ──
        st.subheader(f"📊 {ticker} — Resultados")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Máximo", f"${metricas['maximo']}")
        c2.metric("Mínimo", f"${metricas['minimo']}")
        c3.metric("Media", f"${metricas['media']}")
        c4.metric("Volatilidad", f"${metricas['volatilidad']}")
        retorno = metricas['retorno_pct']
        c5.metric("Retorno", f"{retorno}%", delta=f"{retorno}%")

        st.divider()

        # ── Gráfico ──
        fig = graficar(cierre, indicadores, ticker)
        st.pyplot(fig)

        st.divider()

        # ── Interpretación ──
        st.subheader("🧠 Interpretación")
        col_a, col_b = st.columns(2)

        tendencia = "📈 Alcista" if metricas["retorno_pct"] > 0 else "📉 Bajista"
        rsi_val   = indicadores["rsi_actual"]

        with col_a:
            st.markdown(f"**Tendencia del período:** {tendencia}")
            st.markdown(f"**Retorno:** {metricas['retorno_pct']}%")
            st.markdown(f"**Señales de compra (golden cross):** {indicadores['n_compras']}")
            st.markdown(f"**Señales de venta (death cross):** {indicadores['n_ventas']}")

        with col_b:
            if rsi_val > RSI_SOBRECOMPRA:
                st.warning(f"⚠️ **RSI en sobrecompra ({rsi_val})** — posible corrección próxima")
            elif rsi_val < RSI_SOBREVENTA:
                st.success(f"✅ **RSI en sobreventa ({rsi_val})** — posible rebote próximo")
            else:
                st.info(f"ℹ️ **RSI neutral ({rsi_val})** — sin señal extrema")

        st.caption("⚠️ Este análisis es educativo y no constituye asesoramiento financiero.")

# ── Footer ───────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center;color:#999;font-size:0.85rem'>"
    "Desarrollado por <strong>Ana Fernanda Navarro</strong> · "
    "<a href='https://anafernanda132001-arch.github.io/Portafolio-Analisis-De-Datos-' target='_blank'>Ver portafolio</a>"
    "</div>",
    unsafe_allow_html=True
)
