# 📈 Analizador de Acciones Bursátiles

Herramienta de análisis técnico en Python que descarga datos históricos de cualquier acción, calcula indicadores clave y envía un reporte automático por email con el gráfico adjunto.

---

## ¿Qué hace?

- Descarga datos históricos de Yahoo Finance con `yfinance`
- Calcula **SMA 20 y SMA 50** (medias móviles de corto y mediano plazo)
- Calcula el **RSI de 14 días** para detectar zonas de sobrecompra/sobreventa
- Detecta **señales de cruce** (golden cross / death cross)
- Genera un **gráfico profesional** de dos paneles (precio + RSI)
- Envía un **reporte automático por email** con el gráfico adjunto

---

## Ejemplo de gráfico

> *Insertar captura de pantalla aquí — ejecutá el script con `AAPL` y pegá la imagen*

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/stock-analyzer.git
cd stock-analyzer

# 2. Instalar dependencias
pip install -r requirements.txt
```

---

## Uso

```bash
python analizador.py
```

Al ejecutar, el script pide el ticker por consola:

```
Ingrese el ticker (ej. AAPL, MSFT, GGAL.BA): AAPL
```

Y produce:

```
--- MÉTRICAS ---
  Máximo         : 237.23
  Mínimo         : 169.21
  Media          : 205.47
  Volatilidad    : 18.92
  Retorno %      : 12.35

Resumen del análisis:
  • Tendencia del período : alcista 📈
  • Retorno               : 12.35%
  • RSI (14d)             : neutral (RSI: 54.3)
  • Señales de compra     : 1 golden cross detectado(s)
  • Señales de venta      : 0 death cross detectado(s)
```

---

## Configuración del email

Para activar el envío de reportes, editá estas líneas en `analizador.py`:

```python
enviar_email(
    destinatario = "correo@ejemplo.com",
    asunto       = f"Reporte {ticker}",
    remitente    = "tu_email@gmail.com",
    password     = "tu_password_de_aplicacion",  # contraseña de app Google
)
```

> **Nota:** Gmail requiere una *contraseña de aplicación*, no tu contraseña habitual.
> Activala en: Cuenta Google → Seguridad → Contraseñas de aplicación (requiere 2FA).

---

## Indicadores implementados

| Indicador | Descripción | Señal |
|-----------|-------------|-------|
| SMA 20 | Media móvil 20 días | Tendencia corto plazo |
| SMA 50 | Media móvil 50 días | Tendencia mediano plazo |
| RSI 14 | Índice de Fuerza Relativa | >70 sobrecompra · <30 sobreventa |
| Golden cross | SMA20 cruza ↑ SMA50 | Señal alcista |
| Death cross | SMA20 cruza ↓ SMA50 | Señal bajista |

---

## Stack técnico

- **Python 3.10+**
- `yfinance` — descarga de datos financieros
- `pandas` — manipulación y cálculo de indicadores
- `matplotlib` — visualización
- `smtplib` / `email` — envío de reportes (stdlib)

---

## Estructura del proyecto

```
stock-analyzer/
├── analizador.py      # script principal
├── requirements.txt   # dependencias
└── README.md
```

---

## Posibles mejoras futuras

- [ ] Interfaz web con Streamlit
- [ ] Gráficos interactivos con Plotly
- [ ] Bandas de Bollinger
- [ ] Comparación de múltiples tickers
- [ ] Exportar reporte a PDF

---

*Desarrollado por Fernanda — portafolio de Data Analysis*
