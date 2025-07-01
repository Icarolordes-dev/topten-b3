"""
Módulo para coleta e preparação de dados históricos da B3
"""
import os
import pandas as pd
import yfinance as yf
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import logging
from pathlib import Path

from config import (
    DEFAULT_TICKERS, 
    DEFAULT_PERIOD_MONTHS,
    CACHE_DIR,
    CACHE_FORMAT,
    YFINANCE_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
    get_cache_path,
    validate_ticker
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """Classe para carregar e gerenciar dados históricos de ações"""
    
    def __init__(self, use_cache: bool = True):
        """
        Inicializa o DataLoader
        
        Args:
            use_cache: Se deve usar cache em disco
        """
        self.use_cache = use_cache
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Garante que o diretório de cache existe"""
        Path(CACHE_DIR).mkdir(exist_ok=True)
    
    def _is_cache_valid(self, cache_path: str, max_age_hours: int = 24) -> bool:
        """
        Verifica se o cache é válido baseado na idade
        
        Args:
            cache_path: Caminho do arquivo de cache
            max_age_hours: Idade máxima em horas
            
        Returns:
            True se o cache é válido
        """
        if not os.path.exists(cache_path):
            return False
        
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        max_age = timedelta(hours=max_age_hours)
        
        return datetime.now() - file_time < max_age
    
    def _fetch_ticker_data(self, ticker: str, start_date: datetime, end_date: datetime) -> Optional[pd.DataFrame]:
        """
        Busca dados de um ticker com retry logic
        
        Args:
            ticker: Símbolo do ticker
            start_date: Data de início
            end_date: Data de fim
            
        Returns:
            DataFrame com dados ou None se falhar
        """
        for attempt in range(MAX_RETRIES):
            try:
                stock = yf.Ticker(ticker)
                data = stock.history(
                    start=start_date,
                    end=end_date,
                    timeout=YFINANCE_TIMEOUT
                )
                
                if data.empty:
                    logger.warning(f"Nenhum dado encontrado para {ticker}")
                    return None
                
                # Adicionar coluna com o ticker
                data['Ticker'] = ticker
                
                logger.info(f"Dados carregados para {ticker}: {len(data)} registros")
                return data
                
            except Exception as e:
                logger.warning(f"Tentativa {attempt + 1} falhou para {ticker}: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Falha ao carregar dados para {ticker} após {MAX_RETRIES} tentativas")
        
        return None
    
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa e trata os dados
        
        Args:
            data: DataFrame com dados brutos
            
        Returns:
            DataFrame limpo
        """
        if data.empty:
            return data
        
        # Interpolar valores NaN
        numeric_columns = data.select_dtypes(include=['float64', 'int64']).columns
        data[numeric_columns] = data[numeric_columns].interpolate(method='linear')
        
        # Remover linhas onde todos os valores principais são NaN
        essential_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        available_columns = [col for col in essential_columns if col in data.columns]
        data = data.dropna(subset=available_columns, how='all')
        
        # Garantir que o índice é datetime
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)
        
        # Ordenar por data
        data = data.sort_index()
        
        return data
    
    def load_ticker_data(self, ticker: str, start_date: datetime, end_date: datetime, 
                        force_refresh: bool = False) -> Optional[pd.DataFrame]:
        """
        Carrega dados de um ticker específico
        
        Args:
            ticker: Símbolo do ticker
            start_date: Data de início
            end_date: Data de fim
            force_refresh: Se deve ignorar o cache
            
        Returns:
            DataFrame com dados históricos
        """
        if not validate_ticker(ticker):
            logger.error(f"Ticker inválido: {ticker}")
            return None
        
        cache_path = get_cache_path(ticker)
        
        # Verificar cache
        if self.use_cache and not force_refresh and self._is_cache_valid(cache_path):
            try:
                logger.info(f"Carregando {ticker} do cache")
                data = pd.read_parquet(cache_path)
                
                # Filtrar datas se necessário
                data = data[(data.index >= start_date) & (data.index <= end_date)]
                return self._clean_data(data)
                
            except Exception as e:
                logger.warning(f"Erro ao ler cache para {ticker}: {str(e)}")
        
        # Buscar dados da API
        logger.info(f"Buscando dados para {ticker} via API")
        data = self._fetch_ticker_data(ticker, start_date, end_date)
        
        if data is not None and not data.empty:
            data = self._clean_data(data)
            
            # Salvar no cache
            if self.use_cache:
                try:
                    data.to_parquet(cache_path)
                    logger.info(f"Cache salvo para {ticker}")
                except Exception as e:
                    logger.warning(f"Erro ao salvar cache para {ticker}: {str(e)}")
            
            return data
        
        return None
    
    def load_multiple_tickers(self, tickers: List[str], start_date: datetime, 
                            end_date: datetime, force_refresh: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Carrega dados de múltiplos tickers
        
        Args:
            tickers: Lista de tickers
            start_date: Data de início
            end_date: Data de fim
            force_refresh: Se deve ignorar o cache
            
        Returns:
            Dicionário com dados de cada ticker
        """
        results = {}
        
        for ticker in tickers:
            data = self.load_ticker_data(ticker, start_date, end_date, force_refresh)
            if data is not None and not data.empty:
                results[ticker] = data
            else:
                logger.warning(f"Não foi possível carregar dados para {ticker}")
        
        logger.info(f"Carregados dados para {len(results)} de {len(tickers)} tickers")
        return results
    
    def get_top_volume_tickers(self, period: str = "1d", limit: int = 10) -> List[str]:
        """
        Busca os tickers com maior volume de negociação
        
        Args:
            period: Período para análise do volume
            limit: Número máximo de tickers
            
        Returns:
            Lista de tickers ordenados por volume
        """
        try:
            # Por simplicidade, retornamos a lista padrão
            # Em uma implementação mais robusta, poderíamos consultar uma API
            # que retorna os maiores volumes em tempo real
            return DEFAULT_TICKERS[:limit]
            
        except Exception as e:
            logger.error(f"Erro ao buscar tickers por volume: {str(e)}")
            return DEFAULT_TICKERS[:limit]
    
    def clear_cache(self, ticker: Optional[str] = None):
        """
        Limpa o cache
        
        Args:
            ticker: Ticker específico ou None para limpar tudo
        """
        if ticker:
            cache_path = get_cache_path(ticker)
            if os.path.exists(cache_path):
                os.remove(cache_path)
                logger.info(f"Cache removido para {ticker}")
        else:
            if os.path.exists(CACHE_DIR):
                for file in os.listdir(CACHE_DIR):
                    if file.endswith(f".{CACHE_FORMAT}"):
                        os.remove(os.path.join(CACHE_DIR, file))
                logger.info("Todo o cache foi removido")

def get_default_date_range(months: int = DEFAULT_PERIOD_MONTHS) -> tuple:
    """
    Retorna o intervalo de datas padrão
    
    Args:
        months: Número de meses para voltar
        
    Returns:
        Tupla (start_date, end_date)
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30 * months)
    return start_date, end_date
