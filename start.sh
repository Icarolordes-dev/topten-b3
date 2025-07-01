#!/bin/bash

# Script de inicialização do TopTen B3
# Este script prepara o ambiente e inicia a aplicação

echo "🚀 Iniciando TopTen B3..."
echo "=========================="

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.9+ primeiro."
    exit 1
fi

# Verificar versão do Python
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Versão do Python inadequada. Requerido: $required_version+, Atual: $python_version"
    exit 1
fi

echo "✅ Python $python_version encontrado"

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "⬆️ Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📚 Instalando dependências..."
pip install -r requirements.txt

# Criar diretório de cache
echo "💾 Preparando cache..."
mkdir -p cache

# Verificar se todos os arquivos necessários existem
required_files=("src/app.py" "src/config.py" "src/data_loader.py" "src/predictor.py" "src/visualizer.py")

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Arquivo necessário não encontrado: $file"
        exit 1
    fi
done

echo "✅ Todos os arquivos necessários encontrados"

# Executar verificações básicas
echo "🧪 Executando verificações..."
python3 -c "
import sys
sys.path.append('src')
try:
    import streamlit
    import pandas
    import plotly
    import yfinance
    print('✅ Todas as dependências principais importadas com sucesso')
except ImportError as e:
    print(f'❌ Erro ao importar dependência: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Falha na verificação de dependências"
    exit 1
fi

# Iniciar aplicação
echo ""
echo "🎉 Iniciando aplicação TopTen B3..."
echo "📊 Acesse: http://localhost:8501"
echo ""
echo "Para parar a aplicação, pressione Ctrl+C"
echo ""

streamlit run src/app.py
