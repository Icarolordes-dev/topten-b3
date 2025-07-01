"""
Módulo para modelagem preditiva de séries temporais financeiras
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import logging
import warnings

# Suppressar warnings dos modelos
warnings.filterwarnings('ignore')

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logging.warning("Prophet não disponível. Instale com: pip install prophet")

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller
    from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
    import matplotlib.pyplot as plt
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False
    logging.warning("Statsmodels não disponível. Instale com: pip install statsmodels")

from config import DEFAULT_FORECAST_DAYS, SUPPORTED_MODELS

logger = logging.getLogger(__name__)

class FinancialPredictor:
    """Classe para previsão de séries temporais financeiras"""
    
    def __init__(self):
        """Inicializa o preditor"""
        self.models = {}
        self.fitted_models = {}
    
    def _prepare_data_for_prophet(self, data: pd.DataFrame, 
                                 target_column: str = 'Close') -> pd.DataFrame:
        """
        Prepara dados para o modelo Prophet
        
        Args:
            data: DataFrame com dados históricos
            target_column: Coluna alvo para previsão
            
        Returns:
            DataFrame formatado para Prophet
        """
        if data.empty or target_column not in data.columns:
            raise ValueError(f"Dados insuficientes ou coluna '{target_column}' não encontrada")
        
        prophet_data = pd.DataFrame({
            'ds': data.index,
            'y': data[target_column]
        })
        
        # Remover valores NaN
        prophet_data = prophet_data.dropna()
        
        return prophet_data
    
    def _check_stationarity(self, data: pd.Series) -> Tuple[bool, float]:
        """
        Verifica estacionariedade da série temporal
        
        Args:
            data: Série temporal
            
        Returns:
            Tupla (é_estacionária, p_value)
        """
        try:
            result = adfuller(data.dropna())
            p_value = result[1]
            is_stationary = p_value < 0.05
            return is_stationary, p_value
        except Exception as e:
            logger.warning(f"Erro ao verificar estacionariedade: {str(e)}")
            return False, 1.0
    
    def _difference_series(self, data: pd.Series, order: int = 1) -> pd.Series:
        """
        Aplica diferenciação à série temporal
        
        Args:
            data: Série temporal
            order: Ordem da diferenciação
            
        Returns:
            Série diferenciada
        """
        result = data.copy()
        for _ in range(order):
            result = result.diff().dropna()
        return result
    
    def _find_arima_order(self, data: pd.Series) -> Tuple[int, int, int]:
        """
        Encontra os parâmetros ótimos para ARIMA usando busca simples
        
        Args:
            data: Série temporal
            
        Returns:
            Tupla (p, d, q) dos parâmetros ARIMA
        """
        # Determinar d (ordem de diferenciação)
        d = 0
        series = data.copy()
        max_d = 2
        
        for i in range(max_d + 1):
            is_stationary, p_value = self._check_stationarity(series)
            if is_stationary:
                d = i
                break
            if i < max_d:
                series = self._difference_series(series, 1)
        
        # Para simplicidade, usar valores padrão para p e q
        # Em uma implementação mais robusta, usaríamos AIC/BIC para otimizar
        p = 1  # Ordem AR
        q = 1  # Ordem MA
        
        logger.info(f"Parâmetros ARIMA selecionados: ({p}, {d}, {q})")
        return p, d, q
    
    def fit_prophet(self, data: pd.DataFrame, target_column: str = 'Close',
                   **kwargs) -> Optional[object]:
        """
        Treina modelo Prophet
        
        Args:
            data: DataFrame com dados históricos
            target_column: Coluna alvo para previsão
            **kwargs: Parâmetros adicionais para Prophet
            
        Returns:
            Modelo treinado ou None se falhar
        """
        if not PROPHET_AVAILABLE:
            logger.error("Prophet não está disponível")
            return None
        
        try:
            prophet_data = self._prepare_data_for_prophet(data, target_column)
            
            # Parâmetros padrão para dados financeiros
            default_params = {
                'changepoint_prior_scale': 0.05,
                'seasonality_prior_scale': 10.0,
                'holidays_prior_scale': 10.0,
                'seasonality_mode': 'multiplicative',
                'weekly_seasonality': True,
                'yearly_seasonality': True,
                'daily_seasonality': False
            }
            
            # Atualizar com parâmetros fornecidos
            default_params.update(kwargs)
            
            model = Prophet(**default_params)
            model.fit(prophet_data)
            
            logger.info("Modelo Prophet treinado com sucesso")
            return model
            
        except Exception as e:
            logger.error(f"Erro ao treinar Prophet: {str(e)}")
            return None
    
    def fit_arima(self, data: pd.DataFrame, target_column: str = 'Close',
                 order: Optional[Tuple[int, int, int]] = None) -> Optional[object]:
        """
        Treina modelo ARIMA
        
        Args:
            data: DataFrame com dados históricos
            target_column: Coluna alvo para previsão
            order: Ordem ARIMA (p, d, q). Se None, será determinada automaticamente
            
        Returns:
            Modelo treinado ou None se falhar
        """
        if not ARIMA_AVAILABLE:
            logger.error("ARIMA não está disponível")
            return None
        
        try:
            if target_column not in data.columns:
                raise ValueError(f"Coluna '{target_column}' não encontrada")
            
            series = data[target_column].dropna()
            
            if len(series) < 10:
                raise ValueError("Dados insuficientes para treinar ARIMA")
            
            # Determinar ordem automaticamente se não fornecida
            if order is None:
                order = self._find_arima_order(series)
            
            model = ARIMA(series, order=order)
            fitted_model = model.fit()
            
            logger.info(f"Modelo ARIMA{order} treinado com sucesso")
            return fitted_model
            
        except Exception as e:
            logger.error(f"Erro ao treinar ARIMA: {str(e)}")
            return None
    
    def predict_prophet(self, model: object, periods: int = DEFAULT_FORECAST_DAYS) -> pd.DataFrame:
        """
        Gera previsões com Prophet
        
        Args:
            model: Modelo Prophet treinado
            periods: Número de períodos para prever
            
        Returns:
            DataFrame com previsões
        """
        try:
            # Criar datas futuras
            future = model.make_future_dataframe(periods=periods, freq='D')
            
            # Gerar previsões
            forecast = model.predict(future)
            
            # Filtrar apenas previsões futuras
            future_forecast = forecast.tail(periods).copy()
            
            # Renomear colunas para padronização
            result = pd.DataFrame({
                'yhat': future_forecast['yhat'].values,
                'yhat_lower': future_forecast['yhat_lower'].values,
                'yhat_upper': future_forecast['yhat_upper'].values
            }, index=pd.to_datetime(future_forecast['ds'].values))
            
            logger.info(f"Previsão Prophet gerada para {periods} períodos")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao gerar previsão Prophet: {str(e)}")
            return pd.DataFrame()
    
    def predict_arima(self, model: object, periods: int = DEFAULT_FORECAST_DAYS,
                     last_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Gera previsões com ARIMA
        
        Args:
            model: Modelo ARIMA treinado
            periods: Número de períodos para prever
            last_date: Última data dos dados históricos
            
        Returns:
            DataFrame com previsões
        """
        try:
            # Gerar previsões
            forecast_result = model.forecast(steps=periods)
            confidence_intervals = model.get_forecast(steps=periods).conf_int()
            
            # Criar índice de datas
            if last_date is None:
                last_date = datetime.now()
            
            future_dates = pd.date_range(
                start=last_date + timedelta(days=1),
                periods=periods,
                freq='D'
            )
            
            # Criar DataFrame resultado
            result = pd.DataFrame({
                'yhat': forecast_result,
                'yhat_lower': confidence_intervals.iloc[:, 0],
                'yhat_upper': confidence_intervals.iloc[:, 1]
            }, index=future_dates)
            
            logger.info(f"Previsão ARIMA gerada para {periods} períodos")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao gerar previsão ARIMA: {str(e)}")
            return pd.DataFrame()
    
    def train_and_predict(self, data: pd.DataFrame, model_type: str,
                         target_column: str = 'Close',
                         forecast_days: int = DEFAULT_FORECAST_DAYS,
                         **kwargs) -> Dict[str, Any]:
        """
        Treina modelo e gera previsões
        
        Args:
            data: DataFrame com dados históricos
            model_type: Tipo do modelo ('Prophet' ou 'ARIMA')
            target_column: Coluna alvo para previsão
            forecast_days: Número de dias para prever
            **kwargs: Parâmetros adicionais para o modelo
            
        Returns:
            Dicionário com modelo, previsões e métricas
        """
        if model_type not in SUPPORTED_MODELS:
            raise ValueError(f"Modelo '{model_type}' não suportado. Use: {SUPPORTED_MODELS}")
        
        result = {
            'model_type': model_type,
            'model': None,
            'predictions': pd.DataFrame(),
            'success': False,
            'error': None
        }
        
        try:
            if model_type == 'Prophet':
                model = self.fit_prophet(data, target_column, **kwargs)
                if model is not None:
                    predictions = self.predict_prophet(model, forecast_days)
                    result.update({
                        'model': model,
                        'predictions': predictions,
                        'success': True
                    })
            
            elif model_type == 'ARIMA':
                model = self.fit_arima(data, target_column, **kwargs)
                if model is not None:
                    last_date = data.index[-1] if not data.empty else None
                    predictions = self.predict_arima(model, forecast_days, last_date)
                    result.update({
                        'model': model,
                        'predictions': predictions,
                        'success': True
                    })
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Erro no treinamento e previsão: {str(e)}")
        
        return result
    
    def get_available_models(self) -> list:
        """
        Retorna lista de modelos disponíveis
        
        Returns:
            Lista de modelos disponíveis
        """
        available = []
        
        if PROPHET_AVAILABLE:
            available.append('Prophet')
        
        if ARIMA_AVAILABLE:
            available.append('ARIMA')
        
        return available
    
    def validate_prediction_data(self, data: pd.DataFrame, 
                               min_periods: int = 30) -> Tuple[bool, str]:
        """
        Valida se os dados são adequados para previsão
        
        Args:
            data: DataFrame com dados históricos
            min_periods: Número mínimo de períodos necessários
            
        Returns:
            Tupla (é_válido, mensagem)
        """
        if data.empty:
            return False, "Dados vazios"
        
        if len(data) < min_periods:
            return False, f"Dados insuficientes. Mínimo: {min_periods}, atual: {len(data)}"
        
        if 'Close' not in data.columns:
            return False, "Coluna 'Close' não encontrada"
        
        # Verificar se há muitos valores NaN
        nan_ratio = data['Close'].isna().sum() / len(data)
        if nan_ratio > 0.1:  # Mais de 10% de NaN
            return False, f"Muitos valores faltantes: {nan_ratio:.1%}"
        
        return True, "Dados válidos para previsão"
