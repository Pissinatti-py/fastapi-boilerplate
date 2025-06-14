# Imagem base oficial Python
FROM python:3.12-slim

# Instala dependências de sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requirements
COPY requirements.txt requirements.txt
COPY requirements-dev.txt requirements-dev.txt

# Instala dependências
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copia todo o código da aplicação
COPY . .

# Log de inicialização
RUN echo "✅ Dependencies installed. Application is ready to run."

# Expõe a porta da aplicação (a mesma que uvicorn usará)
EXPOSE 8000

# Define diretório de trabalho dentro do container
WORKDIR /app

# Define o PYTHONPATH para que o pacote src seja encontrado
ENV PYTHONPATH=/app

# Comando padrão para subir a aplicação
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
