# 📈 TopTen B3 - Análise e Previsão de Ações

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Docker](https://img.shields.io/badge/docker-supported-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

> 🚀 **Plataforma interativa para análise técnica e previsão de preços dos principais ativos da B3 (Bolsa de Valores brasileira)**

Uma aplicação web desenvolvida com Streamlit que oferece análise técnica avançada, visualizações interativas e modelos preditivos para as ações mais negociadas do Ibovespa.

## 📸 Demonstração

*Em breve: GIF animado mostrando a aplicação em funcionamento*

## ✨ Funcionalidades Principais

### 📊 Análise de Dados
- **Coleta Automática**: Dados históricos via yfinance com sistema de cache inteligente
- **Top 10 Ativos**: Foco nos ativos de maior volume do Ibovespa
- **Período Configurável**: Análise de 1 mês a 5 anos de histórico
- **Tratamento de Dados**: Limpeza automática e interpolação de valores faltantes

### 📈 Visualizações Interativas
- **Gráficos de Linha**: Evolução temporal dos preços
- **Candlestick**: Análise OHLC (Abertura, Máxima, Mínima, Fechamento)
- **Volume**: Visualização do volume de negociação
- **Comparação**: Análise comparativa entre múltiplos ativos
- **Temas**: Suporte a modo claro e escuro

### 🔮 Modelos Preditivos
- **Prophet**: Modelo de séries temporais do Facebook
- **ARIMA**: Modelo AutoRegressivo Integrado de Médias Móveis
- **Intervalos de Confiança**: Bandas de previsão para análise de risco
- **Previsões Configuráveis**: 7 a 90 dias úteis

### 🎛️ Interface Intuitiva
- **Controles Laterais**: Seleção fácil de ativos, períodos e modelos
- **Métricas em Tempo Real**: Preço atual, variação, máximas e mínimas
- **Export de Dados**: Download de previsões em CSV
- **Design Responsivo**: Otimizado para desktop e mobile

## 🛠️ Tecnologias Utilizadas

### Backend & Data Science
- **Python 3.9+**: Linguagem principal
- **Pandas**: Manipulação e análise de dados
- **NumPy**: Computação numérica
- **Prophet**: Previsão de séries temporais
- **Statsmodels**: Modelos estatísticos (ARIMA)
- **yfinance**: Coleta de dados financeiros

### Frontend & Visualização
- **Streamlit**: Framework web interativo
- **Plotly**: Gráficos interativos avançados
- **Matplotlib/Seaborn**: Visualizações complementares

### Infraestrutura
- **Docker**: Containerização
- **Docker Compose**: Orquestração de serviços
- **PyArrow/Parquet**: Cache otimizado de dados
- **GitHub Actions**: CI/CD

## 🚀 Como Executar

### 📋 Pré-requisitos
- Python 3.9 ou superior
- Docker (opcional)
- Git

### 🐳 Execução com Docker (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/Icarolordes-dev/topten-b3.git
cd topten-b3

# Execute com Docker Compose
docker-compose up --build

# Acesse a aplicação
# http://localhost:8501
```

### 🐍 Execução Local

```bash
# Clone o repositório
git clone https://github.com/Icarolordes-dev/topten-b3.git
cd topten-b3

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
streamlit run src/app.py

# Acesse a aplicação
# http://localhost:8501
```

### ⚙️ Variáveis de Ambiente (Opcional)

```bash
# Cache personalizado
export CACHE_DIR="./custom_cache"

# Timeout para APIs
export YFINANCE_TIMEOUT=60

# Número máximo de tentativas
export MAX_RETRIES=5
```

## 📁 Estrutura do Projeto

```
topten-b3/
├── src/                          # Código fonte
│   ├── app.py                   # Interface Streamlit principal
│   ├── config.py                # Configurações da aplicação
│   ├── data_loader.py           # Coleta e cache de dados
│   ├── predictor.py             # Modelos preditivos
│   └── visualizer.py            # Visualizações interativas
├── .github/                      # Configurações GitHub
│   ├── ISSUE_TEMPLATE/          # Templates de issues
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── workflows/               # CI/CD workflows
│       └── ci.yml
├── cache/                       # Cache de dados (criado automaticamente)
├── tests/                       # Testes (a implementar)
├── docker-compose.yml           # Orquestração Docker
├── Dockerfile                   # Imagem Docker
├── requirements.txt             # Dependências Python
├── .gitignore                   # Arquivos ignorados pelo Git
├── LICENSE                      # Licença MIT
└── README.md                    # Este arquivo
```

## 📊 Ativos Suportados

A aplicação foca nos 10 principais ativos do Ibovespa por volume:

- **VALE3** - Vale S.A.
- **PETR4** - Petrobras
- **ITUB4** - Itaú Unibanco
- **BBDC4** - Bradesco
- **ABEV3** - Ambev
- **MGLU3** - Magazine Luiza
- **WEGE3** - WEG
- **RENT3** - Localiza
- **LREN3** - Lojas Renner
- **GGBR4** - Gerdau

*Lista configurável em `src/config.py`*

## 🔧 Configuração Avançada

### Cache de Dados
O sistema utiliza cache em formato Parquet para otimizar o carregamento:

```python
# src/config.py
CACHE_DIR = "cache"
CACHE_FORMAT = "parquet"
```

### Modelos Preditivos
Configure parâmetros dos modelos:

```python
# Prophet
prophet_params = {
    'changepoint_prior_scale': 0.05,
    'seasonality_mode': 'multiplicative',
    'weekly_seasonality': True
}

# ARIMA - ordem determinada automaticamente
arima_order = (1, 1, 1)  # (p, d, q)
```

## 🤝 Como Contribuir

Contribuições são muito bem-vindas! Veja como você pode ajudar:

### 🐛 Reportando Bugs
1. Use o [template de bug report](.github/ISSUE_TEMPLATE/bug_report.md)
2. Inclua informações detalhadas sobre o ambiente
3. Adicione screenshots se possível

### ✨ Sugerindo Features
1. Use o [template de feature request](.github/ISSUE_TEMPLATE/feature_request.md)
2. Descreva claramente o problema que a feature resolve
3. Considere implementar a feature você mesmo

### 💻 Desenvolvendo
1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### 🧪 Executando Testes
```bash
# Instalar dependências de desenvolvimento
pip install pytest flake8 black isort

# Executar linter
flake8 src/

# Verificar formatação
black --check src/

# Executar testes
pytest tests/
```

## 📈 Roadmap

### 🎯 Próximas Features
- [ ] 📊 Indicadores técnicos (RSI, MACD, Bollinger Bands)
- [ ] 🔔 Sistema de alertas por email/webhook
- [ ] 📱 Versão mobile otimizada
- [ ] 🌐 API REST para integração
- [ ] 📋 Relatórios em PDF
- [ ] 🧠 Modelos de ML mais avançados (LSTM, XGBoost)
- [ ] 💹 Análise de carteiras
- [ ] 📊 Dashboard executivo

### 🔄 Melhorias Técnicas
- [ ] Testes automatizados completos
- [ ] Documentação da API
- [ ] Monitoramento e observabilidade
- [ ] Otimização de performance
- [ ] Suporte a múltiplas exchanges

## ⚠️ Aviso Legal

> **IMPORTANTE**: Esta aplicação é apenas para fins educacionais e informativos. Não constitui aconselhamento financeiro ou recomendação de investimento. Sempre consulte um profissional qualificado antes de tomar decisões de investimento.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**Icaro Lordes**
- GitHub: [@Icarolordes-dev](https://github.com/Icarolordes-dev)
- LinkedIn: [Seu LinkedIn](https://linkedin.com/in/seu-perfil)

## 🙏 Agradecimentos

- [Streamlit](https://streamlit.io/) - Framework web incrível
- [yfinance](https://github.com/ranaroussi/yfinance) - Dados financeiros gratuitos
- [Prophet](https://facebook.github.io/prophet/) - Previsão de séries temporais
- [Plotly](https://plotly.com/) - Visualizações interativas
- Comunidade Python - Por todas as bibliotecas fantásticas

---

<div align="center">

**📈 Desenvolvido com ❤️ para a comunidade de investidores brasileiros**

[⭐ Star no GitHub](https://github.com/Icarolordes-dev/topten-b3) • [🐛 Reportar Bug](https://github.com/Icarolordes-dev/topten-b3/issues) • [💡 Sugerir Feature](https://github.com/Icarolordes-dev/topten-b3/issues)

</div>
