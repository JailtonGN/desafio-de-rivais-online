# Desafio de Rivais Online

Um jogo de palavras online onde você precisa adivinhar palavras embaralhadas no menor tempo possível!

## 🎮 Funcionalidades

- **Modo Solo**: Jogue contra o sistema com diferentes dificuldades
- **Ranking**: Veja os melhores tempos por dificuldade
- **Interface Responsiva**: Jogue em qualquer dispositivo
- **Sistema de Penalidades**: Cada erro adiciona 3 segundos ao tempo final

## 🚀 Como Executar Localmente

### Pré-requisitos
- Python 3.8+
- pip

### Instalação
1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o backend:
   ```bash
   uvicorn main:app --reload
   ```
4. Abra o arquivo `index.html` no navegador

## 🌐 Deploy Online

### Backend (Render.com)
1. Conecte este repositório ao Render
2. Configure como Web Service
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel/Netlify)
1. Faça upload do `index.html`
2. Ajuste o endereço do backend no arquivo

## 🎯 Como Jogar

1. Digite seu nome/nick
2. Escolha a dificuldade (Fácil, Médio, Difícil)
3. Clique nas letras embaralhadas para montar a palavra
4. Cada erro adiciona 3 segundos de penalidade
5. Tente fazer o menor tempo possível!

## 📊 Ranking

O ranking é calculado por:
- Tempo base + (erros × 3 segundos)
- Ordenado do menor para o maior tempo
- Separado por dificuldade

## 🛠️ Tecnologias

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Hospedagem**: Render.com
- **Banco de Dados**: JSON (arquivo local)

## 📝 Licença

Este projeto é de código aberto. 