"""
Módulo para visualização interativa de dados financeiros
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Optional, Dict, Any
import logging

from config import THEME_CONFIG

logger = logging.getLogger(__name__)

class FinancialVisualizer:
    """Classe para criar visualizações interativas de dados financeiros"""
    
    def __init__(self, theme: str = "light"):
        """
        Inicializa o visualizador
        
        Args:
            theme: Tema da interface ('light' ou 'dark')
        """
        self.theme = theme
        self.template = THEME_CONFIG[theme]["plot_template"]
    
    def set_theme(self, theme: str):
        """
        Define o tema dos gráficos
        
        Args:
            theme: Tema ('light' ou 'dark')
        """
        if theme in THEME_CONFIG:
            self.theme = theme
            self.template = THEME_CONFIG[theme]["plot_template"]
    
    def _apply_layout_defaults(self, fig: go.Figure, title: str, height: int = 500) -> go.Figure:
        """
        Aplica configurações padrão de layout
        
        Args:
            fig: Figura do Plotly
            title: Título do gráfico
            height: Altura do gráfico
            
        Returns:
            Figura com layout aplicado
        """
        fig.update_layout(
            title=title,
            template=self.template,
            height=height,
            hovermode='x unified',
            showlegend=True,
            xaxis=dict(
                rangeslider=dict(visible=False),
                type='date'
            ),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        return fig
    
    def plot_line_chart(self, data: pd.DataFrame, ticker: str, 
                       column: str = 'Close', title: Optional[str] = None) -> go.Figure:
        """
        Cria gráfico de linha para preços
        
        Args:
            data: DataFrame com dados históricos
            ticker: Símbolo do ticker
            column: Coluna a ser plotada
            title: Título customizado
            
        Returns:
            Figura do Plotly
        """
        if data.empty or column not in data.columns:
            logger.warning(f"Dados insuficientes para gráfico de linha de {ticker}")
            return go.Figure()
        
        title = title or f"Preço de Fechamento - {ticker}"
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data[column],
            mode='lines',
            name=f'{ticker} - {column}',
            line=dict(width=2),
            hovertemplate=f'<b>{ticker}</b><br>' +
                         'Data: %{x}<br>' +
                         f'{column}: R$ %{{y:.2f}}<br>' +
                         '<extra></extra>'
        ))
        
        return self._apply_layout_defaults(fig, title)
    
    def plot_candlestick(self, data: pd.DataFrame, ticker: str, 
                        title: Optional[str] = None) -> go.Figure:
        """
        Cria gráfico de candlestick (OHLC)
        
        Args:
            data: DataFrame com dados OHLC
            ticker: Símbolo do ticker
            title: Título customizado
            
        Returns:
            Figura do Plotly
        """
        required_columns = ['Open', 'High', 'Low', 'Close']
        if data.empty or not all(col in data.columns for col in required_columns):
            logger.warning(f"Dados OHLC insuficientes para {ticker}")
            return go.Figure()
        
        title = title or f"Gráfico de Candlestick - {ticker}"
        
        fig = go.Figure(data=go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=ticker,
            hovertemplate='<b>' + ticker + '</b><br>' +
                         'Data: %{x}<br>' +
                         'Abertura: R$ %{open:.2f}<br>' +
                         'Máxima: R$ %{high:.2f}<br>' +
                         'Mínima: R$ %{low:.2f}<br>' +
                         'Fechamento: R$ %{close:.2f}<br>' +
                         '<extra></extra>'
        ))
        
        return self._apply_layout_defaults(fig, title)
    
    def plot_volume(self, data: pd.DataFrame, ticker: str,
                   title: Optional[str] = None) -> go.Figure:
        """
        Cria gráfico de volume de negociação
        
        Args:
            data: DataFrame com dados de volume
            ticker: Símbolo do ticker
            title: Título customizado
            
        Returns:
            Figura do Plotly
        """
        if data.empty or 'Volume' not in data.columns:
            logger.warning(f"Dados de volume insuficientes para {ticker}")
            return go.Figure()
        
        title = title or f"Volume de Negociação - {ticker}"
        
        # Determinar cores baseadas no movimento do preço
        colors = []
        if 'Close' in data.columns and 'Open' in data.columns:
            for i in range(len(data)):
                if data['Close'].iloc[i] >= data['Open'].iloc[i]:
                    colors.append('green')
                else:
                    colors.append('red')
        else:
            colors = ['blue'] * len(data)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=data.index,
            y=data['Volume'],
            name='Volume',
            marker_color=colors,
            hovertemplate=f'<b>{ticker}</b><br>' +
                         'Data: %{x}<br>' +
                         'Volume: %{y:,.0f}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            yaxis_title="Volume",
            xaxis_title="Data"
        )
        
        return self._apply_layout_defaults(fig, title)
    
    def plot_ohlc_with_volume(self, data: pd.DataFrame, ticker: str,
                             title: Optional[str] = None) -> go.Figure:
        """
        Cria gráfico combinado de OHLC com volume
        
        Args:
            data: DataFrame com dados OHLC e volume
            ticker: Símbolo do ticker
            title: Título customizado
            
        Returns:
            Figura do Plotly com subplots
        """
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if data.empty or not all(col in data.columns for col in required_columns):
            logger.warning(f"Dados insuficientes para gráfico combinado de {ticker}")
            return go.Figure()
        
        title = title or f"Análise Completa - {ticker}"
        
        # Criar subplots
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3],
            subplot_titles=[f'Preços - {ticker}', 'Volume']
        )
        
        # Adicionar candlestick
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='OHLC',
                hovertemplate='Data: %{x}<br>' +
                             'Abertura: R$ %{open:.2f}<br>' +
                             'Máxima: R$ %{high:.2f}<br>' +
                             'Mínima: R$ %{low:.2f}<br>' +
                             'Fechamento: R$ %{close:.2f}<br>' +
                             '<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Cores do volume baseadas no movimento do preço
        colors = ['green' if data['Close'].iloc[i] >= data['Open'].iloc[i] 
                 else 'red' for i in range(len(data))]
        
        # Adicionar volume
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Volume',
                marker_color=colors,
                hovertemplate='Data: %{x}<br>' +
                             'Volume: %{y:,.0f}<br>' +
                             '<extra></extra>'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=title,
            template=self.template,
            height=600,
            showlegend=True,
            xaxis2_title="Data",
            yaxis_title="Preço (R$)",
            yaxis2_title="Volume",
            hovermode='x unified'
        )
        
        # Remover rangeslider do candlestick
        fig.update_layout(xaxis_rangeslider_visible=False)
        
        return fig
    
    def plot_prediction(self, historical_data: pd.DataFrame, 
                       prediction_data: pd.DataFrame, ticker: str,
                       title: Optional[str] = None) -> go.Figure:
        """
        Cria gráfico com dados históricos e previsão
        
        Args:
            historical_data: DataFrame com dados históricos
            prediction_data: DataFrame com previsão (deve ter colunas: yhat, yhat_lower, yhat_upper)
            ticker: Símbolo do ticker
            title: Título customizado
            
        Returns:
            Figura do Plotly
        """
        if historical_data.empty:
            logger.warning(f"Dados históricos insuficientes para {ticker}")
            return go.Figure()
        
        title = title or f"Previsão de Preços - {ticker}"
        
        fig = go.Figure()
        
        # Adicionar dados históricos
        fig.add_trace(go.Scatter(
            x=historical_data.index,
            y=historical_data['Close'],
            mode='lines',
            name='Histórico',
            line=dict(color='blue', width=2),
            hovertemplate='<b>Histórico</b><br>' +
                         'Data: %{x}<br>' +
                         'Preço: R$ %{y:.2f}<br>' +
                         '<extra></extra>'
        ))
        
        if not prediction_data.empty:
            # Adicionar banda de confiança
            if 'yhat_upper' in prediction_data.columns and 'yhat_lower' in prediction_data.columns:
                fig.add_trace(go.Scatter(
                    x=prediction_data.index,
                    y=prediction_data['yhat_upper'],
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                fig.add_trace(go.Scatter(
                    x=prediction_data.index,
                    y=prediction_data['yhat_lower'],
                    mode='lines',
                    line=dict(width=0),
                    fill='tonexty',
                    fillcolor='rgba(255, 0, 0, 0.2)',
                    name='Intervalo de Confiança',
                    hoverinfo='skip'
                ))
            
            # Adicionar previsão
            if 'yhat' in prediction_data.columns:
                fig.add_trace(go.Scatter(
                    x=prediction_data.index,
                    y=prediction_data['yhat'],
                    mode='lines',
                    name='Previsão',
                    line=dict(color='red', width=2, dash='dash'),
                    hovertemplate='<b>Previsão</b><br>' +
                                 'Data: %{x}<br>' +
                                 'Preço Previsto: R$ %{y:.2f}<br>' +
                                 '<extra></extra>'
                ))
        
        fig.update_layout(
            yaxis_title="Preço (R$)",
            xaxis_title="Data"
        )
        
        return self._apply_layout_defaults(fig, title, height=600)
    
    def plot_multiple_tickers(self, data_dict: Dict[str, pd.DataFrame], 
                             column: str = 'Close',
                             title: Optional[str] = None) -> go.Figure:
        """
        Cria gráfico comparativo de múltiplos tickers
        
        Args:
            data_dict: Dicionário com DataFrames de cada ticker
            column: Coluna a ser plotada
            title: Título customizado
            
        Returns:
            Figura do Plotly
        """
        if not data_dict:
            logger.warning("Nenhum dado fornecido para comparação")
            return go.Figure()
        
        title = title or f"Comparação de {column}"
        
        fig = go.Figure()
        
        colors = px.colors.qualitative.Set1
        
        for i, (ticker, data) in enumerate(data_dict.items()):
            if not data.empty and column in data.columns:
                color = colors[i % len(colors)]
                
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=data[column],
                    mode='lines',
                    name=ticker.replace('.SA', ''),
                    line=dict(color=color, width=2),
                    hovertemplate=f'<b>{ticker}</b><br>' +
                                 'Data: %{x}<br>' +
                                 f'{column}: R$ %{{y:.2f}}<br>' +
                                 '<extra></extra>'
                ))
        
        fig.update_layout(
            yaxis_title=f"{column} (R$)",
            xaxis_title="Data"
        )
        
        return self._apply_layout_defaults(fig, title)
