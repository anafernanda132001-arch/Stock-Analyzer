# ============================================================
#  Analizador de Acciones Bursátiles — Streamlit Web App
#  Autor: Ana Fernanda Navarro
# ============================================================

import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests, io, base64
from datetime import datetime

st.set_page_config(page_title="Analizador de Acciones", page_icon="📈", layout="wide")
st.markdown("<style>.main{background-color:#FAFAFA}</style>", unsafe_allow_html=True)

SMA_CORTO=20; SMA_LARGO=50; RSI_PERIODO=14; RSI_SOBREVENTA=30; RSI_SOBRECOMPRA=70
RESEND_API_KEY  = st.secrets["RESEND_API_KEY"]
EMAIL_REMITENTE = "onboarding@resend.dev"

def obtener_datos(ticker, periodo):
    try:
        data = yf.Ticker(ticker).history(period=periodo)
        return None if data.empty else data
    except: return None

def calcular_sma(cierre, v): return cierre.rolling(window=v).mean()

def calcular_rsi(cierre, p=RSI_PERIODO):
    d=cierre.diff(); g=d.clip(lower=0); pe=-d.clip(upper=0)
    mg=g.ewm(com=p-1,min_periods=p).mean(); mp=pe.ewm(com=p-1,min_periods=p).mean()
    return (100-(100/(1+mg/mp))).round(2)

def detectar_cruces(sc, sl):
    return (sc>sl)&(sc.shift(1)<=sl.shift(1)), (sc<sl)&(sc.shift(1)>=sl.shift(1))

def graficar(cierre, ind, ticker):
    fig,(ax1,ax2)=plt.subplots(2,1,figsize=(13,7),gridspec_kw={"height_ratios":[3,1]},sharex=True,facecolor="#FAFAFA")
    fig.suptitle(f"Análisis técnico: {ticker}",fontsize=14,fontweight="bold",y=0.98)
    ax1.set_facecolor("#FAFAFA")
    ax1.plot(cierre,color="#1565C0",lw=1.6,label="Precio cierre",zorder=3)
    ax1.plot(ind["sma20"],color="#F57C00",lw=1.2,ls="--",label=f"SMA {SMA_CORTO}",zorder=2)
    ax1.plot(ind["sma50"],color="#C62828",lw=1.2,ls="--",label=f"SMA {SMA_LARGO}",zorder=2)
    c=cierre[ind["senal_compra"]]
    if not c.empty: ax1.scatter(c.index,c.values,marker="^",color="#2E7D32",s=100,zorder=4,label=f"Golden cross ({ind['n_compras']})")
    v=cierre[ind["senal_venta"]]
    if not v.empty: ax1.scatter(v.index,v.values,marker="v",color="#B71C1C",s=100,zorder=4,label=f"Death cross ({ind['n_ventas']})")
    ax1.set_ylabel("Precio (USD)",fontsize=10); ax1.legend(loc="upper left",fontsize=9,framealpha=0.7)
    ax1.grid(alpha=0.25,linestyle="--"); ax1.spines[["top","right"]].set_visible(False)
    ax2.set_facecolor("#FAFAFA"); ax2.plot(ind["rsi"],color="#6A1B9A",lw=1.3)
    ax2.axhline(RSI_SOBRECOMPRA,color="#C62828",lw=0.8,ls="--"); ax2.axhline(RSI_SOBREVENTA,color="#2E7D32",lw=0.8,ls="--")
    ax2.fill_between(ind["rsi"].index,RSI_SOBRECOMPRA,100,alpha=0.07,color="#C62828")
    ax2.fill_between(ind["rsi"].index,0,RSI_SOBREVENTA,alpha=0.07,color="#2E7D32")
    ax2.text(ind["rsi"].index[-1],RSI_SOBRECOMPRA+1,"sobrecompra",fontsize=7.5,color="#C62828",ha="right")
    ax2.text(ind["rsi"].index[-1],RSI_SOBREVENTA-3,"sobreventa",fontsize=7.5,color="#2E7D32",ha="right")
    ax2.set_ylim(0,100); ax2.set_ylabel("RSI",fontsize=10)
    ax2.grid(alpha=0.25,linestyle="--"); ax2.spines[["top","right"]].set_visible(False)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y")); ax2.xaxis.set_major_locator(mdates.MonthLocator())
    plt.setp(ax2.xaxis.get_majorticklabels(),rotation=15,ha="right",fontsize=8)
    plt.tight_layout(); return fig

def fig_a_base64(fig):
    buf=io.BytesIO(); fig.savefig(buf,format="png",dpi=150,bbox_inches="tight"); buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def enviar_email(dest, ticker, metricas, ind, fig):
    fecha=datetime.today().strftime("%d/%m/%Y")
    tendencia="Alcista 📈" if metricas["retorno_pct"]>0 else "Bajista 📉"
    rsi_val=ind["rsi_actual"]
    if rsi_val>RSI_SOBRECOMPRA: zona=f"Sobrecompra ({rsi_val}) — posible corrección"
    elif rsi_val<RSI_SOBREVENTA: zona=f"Sobreventa ({rsi_val}) — posible rebote"
    else: zona=f"Neutral ({rsi_val})"
    img=fig_a_base64(fig)
    html=f"""<div style="font-family:Arial,sans-serif;max-width:600px;margin:auto">
    <div style="background:#1A1612;padding:24px;border-radius:8px 8px 0 0;text-align:center">
      <h1 style="color:#E8624A;margin:0;font-size:22px">📈 Reporte de Acciones</h1>
      <p style="color:#aaa;margin:6px 0 0">{ticker} · {fecha}</p>
    </div>
    <div style="background:#fff;padding:24px;border:1px solid #eee">
      <h2 style="color:#1A1612;font-size:18px;border-bottom:2px solid #E8624A;padding-bottom:8px">Métricas</h2>
      <table style="width:100%;border-collapse:collapse">
        <tr style="background:#fdf5f3"><td style="padding:8px;font-weight:bold">Máximo</td><td>${metricas['maximo']}</td></tr>
        <tr><td style="padding:8px;font-weight:bold">Mínimo</td><td>${metricas['minimo']}</td></tr>
        <tr style="background:#fdf5f3"><td style="padding:8px;font-weight:bold">Media</td><td>${metricas['media']}</td></tr>
        <tr><td style="padding:8px;font-weight:bold">Volatilidad</td><td>${metricas['volatilidad']}</td></tr>
        <tr style="background:#fdf5f3"><td style="padding:8px;font-weight:bold">Retorno</td><td>{metricas['retorno_pct']}%</td></tr>
      </table>
      <h2 style="color:#1A1612;font-size:18px;border-bottom:2px solid #E8624A;padding-bottom:8px;margin-top:24px">Análisis técnico</h2>
      <p>📊 <strong>Tendencia:</strong> {tendencia}</p>
      <p>📉 <strong>RSI (14d):</strong> {zona}</p>
      <p>✅ <strong>Golden cross:</strong> {ind['n_compras']} detectado(s)</p>
      <p>🔴 <strong>Death cross:</strong> {ind['n_ventas']} detectado(s)</p>
      <h2 style="color:#1A1612;font-size:18px;border-bottom:2px solid #E8624A;padding-bottom:8px;margin-top:24px">Gráfico</h2>
      <img src="data:image/png;base64,{img}" style="width:100%;border-radius:6px" />
    </div>
    <div style="background:#f5f5f5;padding:16px;border-radius:0 0 8px 8px;text-align:center">
      <p style="color:#999;font-size:12px;margin:0">Reporte generado por <strong>Ana Fernanda Navarro</strong> ·
      <a href="https://anafernanda132001-arch.github.io/Portafolio-Analisis-De-Datos-" style="color:#E8624A">Ver portafolio</a></p>
      <p style="color:#bbb;font-size:11px;margin:4px 0 0">⚠️ Este reporte es educativo y no constituye asesoramiento financiero.</p>
    </div></div>"""
    r=requests.post("https://api.resend.com/emails",
        headers={"Authorization":f"Bearer {RESEND_API_KEY}","Content-Type":"application/json"},
        json={"from":f"Analizador de Acciones <{EMAIL_REMITENTE}>","to":[dest],"subject":f"📈 Reporte {ticker} — {fecha}","html":html})
    return r.status_code==200

# ── UI ────────────────────────────────────────────────────────
st.title("📈 Analizador de Acciones Bursátiles")
st.markdown("Análisis técnico con **SMA 20/50**, **RSI 14** y detección de señales de cruce. Desarrollado por **Ana Fernanda Navarro**.")
st.divider()

col1,col2=st.columns([2,1])
with col1: ticker=st.text_input("🔍 Ticker",value="AAPL",placeholder="Ej: AAPL, MSFT, GGAL.BA").strip().upper()
with col2: periodo=st.selectbox("📅 Período",["3mo","6mo","1y","2y"],index=1,
    format_func=lambda x:{"3mo":"3 meses","6mo":"6 meses","1y":"1 año","2y":"2 años"}[x])

if st.button("Analizar →",type="primary") and ticker:
    with st.spinner(f"Descargando {ticker}..."):
        data=obtener_datos(ticker,periodo)
    if data is None:
        st.error(f"❌ No se encontraron datos para **{ticker}**.")
    else:
        cierre=data["Close"]; sma20=calcular_sma(cierre,SMA_CORTO); sma50=calcular_sma(cierre,SMA_LARGO)
        rsi=calcular_rsi(cierre); sc,sv=detectar_cruces(sma20,sma50)
        st.session_state.update({
            "metricas":{"maximo":round(float(cierre.max()),2),"minimo":round(float(cierre.min()),2),
                "media":round(float(cierre.mean()),2),"volatilidad":round(float(cierre.std()),2),
                "retorno_pct":round(((float(cierre.iloc[-1])/float(cierre.iloc[0]))-1)*100,2)},
            "indicadores":{"sma20":sma20,"sma50":sma50,"rsi":rsi,"rsi_actual":round(float(rsi.iloc[-1]),2),
                "senal_compra":sc,"senal_venta":sv,"n_compras":int(sc.sum()),"n_ventas":int(sv.sum())},
            "ticker":ticker,"fig":graficar(cierre,{"sma20":sma20,"sma50":sma50,"rsi":rsi,
                "senal_compra":sc,"senal_venta":sv,"n_compras":int(sc.sum()),"n_ventas":int(sv.sum())},ticker)
        })

if "fig" in st.session_state:
    m=st.session_state["metricas"]; ind=st.session_state["indicadores"]
    t=st.session_state["ticker"];   fig=st.session_state["fig"]
    st.subheader(f"📊 {t} — Resultados")
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("Máximo",f"${m['maximo']}"); c2.metric("Mínimo",f"${m['minimo']}")
    c3.metric("Media",f"${m['media']}");   c4.metric("Volatilidad",f"${m['volatilidad']}")
    c5.metric("Retorno",f"{m['retorno_pct']}%",delta=f"{m['retorno_pct']}%")
    st.divider(); st.pyplot(fig); st.divider()

    st.subheader("🧠 Interpretación")
    ca,cb=st.columns(2)
    with ca:
        st.markdown(f"**Tendencia:** {'📈 Alcista' if m['retorno_pct']>0 else '📉 Bajista'}")
        st.markdown(f"**Retorno:** {m['retorno_pct']}%")
        st.markdown(f"**Golden cross:** {ind['n_compras']}"); st.markdown(f"**Death cross:** {ind['n_ventas']}")
    with cb:
        rv=ind["rsi_actual"]
        if rv>RSI_SOBRECOMPRA: st.warning(f"⚠️ RSI en sobrecompra ({rv}) — posible corrección")
        elif rv<RSI_SOBREVENTA: st.success(f"✅ RSI en sobreventa ({rv}) — posible rebote")
        else: st.info(f"ℹ️ RSI neutral ({rv})")

    st.divider()
    st.subheader("📧 Recibí el reporte por email")
    email_dest=st.text_input("Tu email",placeholder="tucorreo@gmail.com")
    if st.button("Enviar reporte →",type="primary"):
        if not email_dest or "@" not in email_dest:
            st.error("❌ Ingresá un email válido.")
        else:
            with st.spinner("Enviando..."):
                ok=enviar_email(email_dest,t,m,ind,fig)
            if ok: st.success(f"✅ Reporte enviado a **{email_dest}**. ¡Revisá tu bandeja!")
            else:  st.error("❌ Error al enviar. Intentá de nuevo.")

    st.caption("⚠️ Este análisis es educativo y no constituye asesoramiento financiero.")

st.divider()
st.markdown("<div style='text-align:center;color:#999;font-size:0.85rem'>Desarrollado por <strong>Ana Fernanda Navarro</strong> · "
    "<a href='https://anafernanda132001-arch.github.io/Portafolio-Analisis-De-Datos-' target='_blank'>Ver portafolio</a></div>",
    unsafe_allow_html=True)
