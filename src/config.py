"""
Configurações da aplicação TopTen B3
"""
import os
from datetime import datetime, timedelta

# Configurações de dados
DEFAULT_TICKERS = [
    "VALE3.SA",    # Vale
    "PETR4.SA",    # Petrobras
    "ITUB4.SA",    # Itaú Unibanco
    "BBDC4.SA",    # Bradesco
    "ABEV3.SA",    # Ambev
    "MGLU3.SA",    # Magazine Luiza
    "WEGE3.SA",    # WEG
    "RENT3.SA",    # Localiza
    "LREN3.SA",    # Lojas Renner
    "GGBR4.SA"     # Gerdau
]

# Período de dados padrão
DEFAULT_PERIOD_MONTHS = 12
DEFAULT_START_DATE = datetime.now() - timedelta(days=365)
DEFAULT_END_DATE = datetime.now()

# Configurações de cache
CACHE_DIR = "cache"
CACHE_FORMAT = "parquet"

# Configurações de previsão
DEFAULT_FORECAST_DAYS = 30
SUPPORTED_MODELS = ["Prophet", "ARIMA"]

# Configurações da interface
APP_TITLE = "📈 TopTen B3 - Análise de Ações"
APP_DESCRIPTION = """
Plataforma de análise e previsão de ações da B3 com dados dos principais ativos do Ibovespa.
"""

# Configurações de tema
THEME_CONFIG = {
    "light": {
        "background_color": "#FFFFFF",
        "text_color": "#000000",
        "plot_template": "plotly_white"
    },
    "dark": {
        "background_color": "#0E1117",
        "text_color": "#FFFFFF", 
        "plot_template": "plotly_dark"
    }
}

# Configurações de API
YFINANCE_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 1  # segundos

# Validação de configurações
def validate_ticker(ticker: str) -> bool:
    """Valida se o ticker está no formato correto"""
    return ticker.endswith(".SA") and len(ticker) >= 6

def get_cache_path(ticker: str) -> str:
    """Retorna o caminho do arquivo de cache para um ticker"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"{ticker.replace('.SA', '')}.{CACHE_FORMAT}")
