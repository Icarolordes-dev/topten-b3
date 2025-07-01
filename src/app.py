"""
Interface web principal da aplicação TopTen B3
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar módulos locais
try:
    from config import (
        DEFAULT_TICKERS, 
        APP_TITLE, 
        APP_DESCRIPTION,
        DEFAULT_FORECAST_DAYS,
        SUPPORTED_MODELS,
        THEME_CONFIG
    )
    from data_loader import DataLoader, get_default_date_range
    from visualizer import FinancialVisualizer
    from predictor import FinancialPredictor
except ImportError as e:
    st.error(f"Erro ao importar módulos: {e}")
    st.stop()

# Configurações da página
st.set_page_config(
    page_title="TopTen B3",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
def load_custom_css(theme: str = "light"):
    """Carrega CSS customizado baseado no tema"""
    theme_colors = THEME_CONFIG[theme]
    
    css = f"""
    <style>
    .main-header {{
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }}
    
    .metric-card {{
        background-color: {theme_colors['background_color']};
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 0.5rem 0;
    }}
    
    .stSelectbox > div > div {{
        background-color: {theme_colors['background_color']};
    }}
    
    .sidebar .sidebar-content {{
        background-color: {theme_colors['background_color']};
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Funções auxiliares
@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_data(ticker: str, start_date: datetime, end_date: datetime, force_refresh: bool = False) -> pd.DataFrame:
    """Carrega dados com cache"""
    loader = DataLoader(use_cache=True)
    return loader.load_ticker_data(ticker, start_date, end_date, force_refresh)

@st.cache_data(ttl=3600)
def load_multiple_data(tickers: list, start_date: datetime, end_date: datetime) -> Dict[str, pd.DataFrame]:
    """Carrega dados de múltiplos tickers com cache"""
    loader = DataLoader(use_cache=True)
    return loader.load_multiple_tickers(tickers, start_date, end_date)

def format_currency(value: float) -> str:
    """Formata valor como moeda brasileira"""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calculate_metrics(data: pd.DataFrame) -> Dict[str, float]:
    """Calcula métricas básicas dos dados"""
    if data.empty or 'Close' not in data.columns:
        return {}
    
    current_price = data['Close'].iloc[-1]
    previous_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
    
    return {
        'current_price': current_price,
        'price_change': current_price - previous_price,
        'price_change_pct': ((current_price - previous_price) / previous_price) * 100 if previous_price != 0 else 0,
        'max_price': data['Close'].max(),
        'min_price': data['Close'].min(),
        'avg_volume': data['Volume'].mean() if 'Volume' in data.columns else 0
    }

def main():
    """Função principal da aplicação"""
    
    # Sidebar
    st.sidebar.title("🎛️ Controles")
    
    # Seletor de tema
    theme = st.sidebar.selectbox(
        "🎨 Tema",
        options=["light", "dark"],
        index=0,
        help="Selecione o tema da interface"
    )
    
    # Carregar CSS customizado
    load_custom_css(theme)
    
    # Header principal
    st.markdown(f"""
    <div class="main-header">
        <h1>{APP_TITLE}</h1>
        <p>{APP_DESCRIPTION}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Controles da sidebar
    st.sidebar.markdown("### 📊 Configurações de Dados")
    
    # Seletor de ativo
    selected_ticker = st.sidebar.selectbox(
        "Selecione o Ativo",
        options=DEFAULT_TICKERS,
        index=0,
        format_func=lambda x: f"{x.replace('.SA', '')} ({x})",
        help="Escolha o ativo para análise"
    )
    
    # Seletor de período
    col1, col2 = st.sidebar.columns(2)
    
    default_start, default_end = get_default_date_range()
    
    with col1:
        start_date = st.date_input(
            "Data Início",
            value=default_start,
            max_value=datetime.now(),
            help="Data de início para análise"
        )
    
    with col2:
        end_date = st.date_input(
            "Data Fim",
            value=default_end,
            max_value=datetime.now(),
            help="Data de fim para análise"
        )
    
    # Validar datas
    if start_date >= end_date:
        st.sidebar.error("A data de início deve ser anterior à data de fim!")
        return
    
    # Controles de previsão
    st.sidebar.markdown("### 🔮 Configurações de Previsão")
    
    predictor = FinancialPredictor()
    available_models = predictor.get_available_models()
    
    if not available_models:
        st.sidebar.error("Nenhum modelo de previsão disponível! Instale Prophet ou Statsmodels.")
        selected_model = None
    else:
        selected_model = st.sidebar.selectbox(
            "Modelo Preditivo",
            options=available_models,
            help="Escolha o modelo para previsão"
        )
    
    forecast_days = st.sidebar.slider(
        "Dias para Previsão",
        min_value=7,
        max_value=90,
        value=DEFAULT_FORECAST_DAYS,
        help="Número de dias úteis para prever"
    )
    
    # Botões de ação
    st.sidebar.markdown("### ⚡ Ações")
    
    force_refresh = st.sidebar.button(
        "🔄 Atualizar Dados",
        help="Força atualização dos dados (ignora cache)"
    )
    
    show_comparison = st.sidebar.checkbox(
        "📊 Comparar Ativos",
        help="Mostrar comparação entre múltiplos ativos"
    )
    
    # Área principal
    try:
        # Carregar dados
        with st.spinner(f"Carregando dados para {selected_ticker}..."):
            data = load_data(selected_ticker, start_date, end_date, force_refresh)
        
        if data is None or data.empty:
            st.error(f"Não foi possível carregar dados para {selected_ticker}")
            return
        
        # Calcular métricas
        metrics = calculate_metrics(data)
        
        # Exibir métricas principais
        if metrics:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                price_change_color = "normal" if metrics['price_change'] >= 0 else "inverse"
                st.metric(
                    "Preço Atual",
                    format_currency(metrics['current_price']),
                    f"{metrics['price_change']:+.2f} ({metrics['price_change_pct']:+.2f}%)",
                    delta_color=price_change_color
                )
            
            with col2:
                st.metric(
                    "Máxima",
                    format_currency(metrics['max_price'])
                )
            
            with col3:
                st.metric(
                    "Mínima",
                    format_currency(metrics['min_price'])
                )
            
            with col4:
                st.metric(
                    "Volume Médio",
                    f"{metrics['avg_volume']:,.0f}"
                )
        
        # Inicializar visualizador
        visualizer = FinancialVisualizer(theme)
        
        # Abas principais
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Preços", "🕯️ Candlestick", "📊 Volume", "🔮 Previsão"])
        
        with tab1:
            st.subheader(f"Evolução do Preço - {selected_ticker}")
            fig_line = visualizer.plot_line_chart(data, selected_ticker)
            st.plotly_chart(fig_line, use_container_width=True)
        
        with tab2:
            st.subheader(f"Gráfico de Candlestick - {selected_ticker}")
            fig_candle = visualizer.plot_ohlc_with_volume(data, selected_ticker)
            st.plotly_chart(fig_candle, use_container_width=True)
        
        with tab3:
            st.subheader(f"Volume de Negociação - {selected_ticker}")
            fig_volume = visualizer.plot_volume(data, selected_ticker)
            st.plotly_chart(fig_volume, use_container_width=True)
        
        with tab4:
            st.subheader(f"Previsão de Preços - {selected_ticker}")
            
            if selected_model and len(data) >= 30:
                # Validar dados para previsão
                is_valid, validation_msg = predictor.validate_prediction_data(data)
                
                if is_valid:
                    with st.spinner(f"Gerando previsão com {selected_model}..."):
                        try:
                            result = predictor.train_and_predict(
                                data, 
                                selected_model, 
                                forecast_days=forecast_days
                            )
                            
                            if result['success'] and not result['predictions'].empty:
                                # Plotar previsão
                                fig_pred = visualizer.plot_prediction(
                                    data, 
                                    result['predictions'], 
                                    selected_ticker
                                )
                                st.plotly_chart(fig_pred, use_container_width=True)
                                
                                # Exibir resumo da previsão
                                pred_data = result['predictions']
                                st.markdown("#### 📋 Resumo da Previsão")
                                
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric(
                                        "Previsão Próximos 7 dias",
                                        format_currency(pred_data['yhat'].iloc[6] if len(pred_data) > 6 else pred_data['yhat'].iloc[-1])
                                    )
                                
                                with col2:
                                    st.metric(
                                        "Previsão Final",
                                        format_currency(pred_data['yhat'].iloc[-1])
                                    )
                                
                                with col3:
                                    trend = "📈 Alta" if pred_data['yhat'].iloc[-1] > data['Close'].iloc[-1] else "📉 Baixa"
                                    st.metric(
                                        "Tendência",
                                        trend
                                    )
                                
                                # Opção de baixar previsões
                                if st.button("📥 Baixar Previsões CSV"):
                                    csv = pred_data.to_csv()
                                    st.download_button(
                                        label="Download",
                                        data=csv,
                                        file_name=f"previsao_{selected_ticker}_{datetime.now().strftime('%Y%m%d')}.csv",
                                        mime='text/csv'
                                    )
                            
                            else:
                                st.error(f"Erro na previsão: {result.get('error', 'Erro desconhecido')}")
                        
                        except Exception as e:
                            st.error(f"Erro ao gerar previsão: {str(e)}")
                else:
                    st.warning(f"Dados inadequados para previsão: {validation_msg}")
            else:
                if not selected_model:
                    st.warning("Nenhum modelo de previsão disponível")
                else:
                    st.warning("Dados insuficientes para previsão (mínimo: 30 períodos)")
        
        # Seção de comparação (se habilitada)
        if show_comparison:
            st.markdown("---")
            st.subheader("📊 Comparação entre Ativos")
            
            # Seletor de ativos para comparação
            comparison_tickers = st.multiselect(
                "Selecione ativos para comparar",
                options=[t for t in DEFAULT_TICKERS if t != selected_ticker],
                default=DEFAULT_TICKERS[1:4],
                help="Escolha até 5 ativos para comparar"
            )
            
            if comparison_tickers:
                with st.spinner("Carregando dados para comparação..."):
                    # Incluir o ativo selecionado
                    all_tickers = [selected_ticker] + comparison_tickers[:4]  # Limitar a 5 total
                    comparison_data = load_multiple_data(all_tickers, start_date, end_date)
                
                if comparison_data:
                    fig_comparison = visualizer.plot_multiple_tickers(
                        comparison_data, 
                        title="Comparação de Preços de Fechamento"
                    )
                    st.plotly_chart(fig_comparison, use_container_width=True)
                    
                    # Tabela de performance
                    st.markdown("#### 📈 Performance Comparativa")
                    
                    performance_data = []
                    for ticker, ticker_data in comparison_data.items():
                        if not ticker_data.empty:
                            ticker_metrics = calculate_metrics(ticker_data)
                            performance_data.append({
                                'Ativo': ticker.replace('.SA', ''),
                                'Preço Atual': format_currency(ticker_metrics['current_price']),
                                'Variação (%)': f"{ticker_metrics['price_change_pct']:+.2f}%",
                                'Máxima': format_currency(ticker_metrics['max_price']),
                                'Mínima': format_currency(ticker_metrics['min_price'])
                            })
                    
                    if performance_data:
                        st.dataframe(pd.DataFrame(performance_data), use_container_width=True)
    
    except Exception as e:
        st.error(f"Erro na aplicação: {str(e)}")
        logger.error(f"Erro na aplicação: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        📈 TopTen B3 | Desenvolvido com Streamlit | Dados via yfinance
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
