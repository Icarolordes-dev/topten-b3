@echo off
REM Script de inicialização do TopTen B3 para Windows
REM Este script prepara o ambiente e inicia a aplicação

echo 🚀 Iniciando TopTen B3...
echo ==========================

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado. Por favor, instale Python 3.9+ primeiro.
    pause
    exit /b 1
)

echo ✅ Python encontrado

REM Criar ambiente virtual se não existir
if not exist "venv\" (
    echo 📦 Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual
echo 🔧 Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Atualizar pip
echo ⬆️ Atualizando pip...
python -m pip install --upgrade pip

REM Instalar dependências
echo 📚 Instalando dependências...
pip install -r requirements.txt

REM Criar diretório de cache
echo 💾 Preparando cache...
if not exist "cache\" mkdir cache

REM Verificar se todos os arquivos necessários existem
echo 🧪 Verificando arquivos...

if not exist "src\app.py" (
    echo ❌ Arquivo não encontrado: src\app.py
    pause
    exit /b 1
)

if not exist "src\config.py" (
    echo ❌ Arquivo não encontrado: src\config.py
    pause
    exit /b 1
)

if not exist "src\data_loader.py" (
    echo ❌ Arquivo não encontrado: src\data_loader.py
    pause
    exit /b 1
)

if not exist "src\predictor.py" (
    echo ❌ Arquivo não encontrado: src\predictor.py
    pause
    exit /b 1
)

if not exist "src\visualizer.py" (
    echo ❌ Arquivo não encontrado: src\visualizer.py
    pause
    exit /b 1
)

echo ✅ Todos os arquivos necessários encontrados

REM Executar verificações básicas
echo 🧪 Executando verificações...
python -c "import sys; sys.path.append('src'); import streamlit, pandas, plotly, yfinance; print('✅ Dependências verificadas')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Erro na verificação de dependências
    pause
    exit /b 1
)

REM Iniciar aplicação
echo.
echo 🎉 Iniciando aplicação TopTen B3...
echo 📊 Acesse: http://localhost:8501
echo.
echo Para parar a aplicação, pressione Ctrl+C
echo.

streamlit run src\app.py

pause
