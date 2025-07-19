from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import random
from typing import Optional
import os
import json
import requests
import time

app = FastAPI()

# Permite que o frontend acesse a API (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, troque para o domínio do seu site
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PalavraRequest(BaseModel):
    palavra: str

class SorteioRequest(BaseModel):
    dificuldade: str

class RankingRequest(BaseModel):
    nome: str
    tempo: float
    erros: int
    dificuldade: str
    palavra: str

# Listas de palavras para cada dificuldade (exemplo)
PALAVRAS = {
    'facil': ["casa", "livro", "porta", "mesa", "pato", "fogo", "bola"],
    'medio': ["janela", "amarelo", "computador", "telefone", "cachorro", "banana"],
    'dificil': ["abacaxi", "paralelepipedo", "dificuldade", "programador", "bicicleta", "universidade"]
}

# Cache para palavras do Dicio (versão 2.0)
DICIO_CACHE = {}

def buscar_palavra_dicio(palavra):
    """Busca uma palavra no Dicio.com.br (versão simplificada)"""
    if palavra in DICIO_CACHE:
        return DICIO_CACHE[palavra]
    
    try:
        # Por enquanto, retorna uma definição simples
        definicoes_simples = {
            'casa': 'Lugar onde moramos, habitação, residência.',
            'livro': 'Conjunto de folhas impressas ou manuscritas, encadernadas.',
            'porta': 'Abertura na parede para entrar ou sair de um local.',
            'mesa': 'Móvel com superfície plana para colocar objetos.',
            'pato': 'Ave aquática com bico largo e pés palmados.',
            'fogo': 'Combustão que produz luz e calor.',
            'bola': 'Objeto esférico usado em jogos e esportes.',
            'janela': 'Abertura na parede para entrada de luz e ar.',
            'amarelo': 'Cor primária entre verde e laranja.',
            'computador': 'Máquina eletrônica para processar dados.',
            'telefone': 'Aparelho para comunicação à distância.',
            'cachorro': 'Animal doméstico da família dos canídeos.',
            'banana': 'Fruta amarela alongada, rica em potássio.',
            'abacaxi': 'Fruta tropical com casca espinhosa.',
            'programador': 'Pessoa que escreve códigos de computador.',
            'bicicleta': 'Veículo de duas rodas movido a pedal.',
            'universidade': 'Instituição de ensino superior.',
            'conhecimento': 'Informação adquirida através do estudo.',
            'inteligência': 'Capacidade de aprender e resolver problemas.',
            'responsabilidade': 'Obrigação de responder pelos próprios atos.',
            'oportunidade': 'Momento favorável para fazer algo.',
            'desenvolvimento': 'Processo de crescimento e evolução.',
            'compreensão': 'Capacidade de entender algo.',
            'organização': 'Ato de organizar ou estruturar.',
            'comunicação': 'Troca de informações entre pessoas.',
            'transformação': 'Mudança de forma ou natureza.',
            'experiência': 'Conhecimento adquirido pela prática.',
            'possibilidade': 'Chance de algo acontecer.',
            'realização': 'Ato de realizar ou concretizar.',
            'aprendizado': 'Processo de aprender algo.',
            'crescimento': 'Aumento de tamanho ou desenvolvimento.'
        }
        
        definicao = definicoes_simples.get(palavra.lower())
        if definicao:
            DICIO_CACHE[palavra] = definicao
            return definicao
        
        return f"Definição de '{palavra}': Palavra em português brasileiro."
    except Exception as e:
        print(f"Erro ao buscar palavra '{palavra}': {e}")
        return None

def obter_palavras_por_dificuldade(dificuldade):
    """Retorna palavras baseadas na dificuldade"""
    if dificuldade == 'facil':
        return ["casa", "livro", "porta", "mesa", "pato", "fogo", "bola", "cama", "sol", "lua", "mar", "rio", "pé", "mão", "olho", "boca", "pai", "mãe", "filho", "amigo"]
    elif dificuldade == 'medio':
        return ["janela", "amarelo", "computador", "telefone", "cachorro", "banana", "carro", "livro", "escola", "trabalho", "família", "amizade", "felicidade", "esperança", "liberdade", "justiça", "paz", "amor", "vida", "tempo"]
    else:  # dificil
        return ["abacaxi", "paralelepipedo", "dificuldade", "programador", "bicicleta", "universidade", "conhecimento", "inteligência", "responsabilidade", "oportunidade", "desenvolvimento", "compreensão", "organização", "comunicação", "transformação", "experiência", "possibilidade", "realização", "aprendizado", "crescimento"]

import json
RANKING_SOLO_ARQ = 'ranking_solo.json'

def carregar_ranking():
    try:
        with open(RANKING_SOLO_ARQ, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def salvar_ranking(ranking):
    with open(RANKING_SOLO_ARQ, 'w', encoding='utf-8') as f:
        json.dump(ranking, f, ensure_ascii=False, indent=2)

@app.post("/embaralhar")
def embaralhar(req: PalavraRequest):
    letras = list(req.palavra)
    random.shuffle(letras)
    return {"embaralhada": ''.join(letras)}

@app.post("/validar")
def validar(req: PalavraRequest):
    palavra = req.palavra
    if palavra.isalpha() and 4 <= len(palavra) <= 20:
        return {"valida": True}
    else:
        return {"valida": False, "motivo": "A palavra deve ter entre 4 e 20 letras e conter apenas letras."}

@app.post("/sortear_palavra")
def sortear_palavra(req: SorteioRequest):
    dificuldade = req.dificuldade.lower()
    palavras = obter_palavras_por_dificuldade(dificuldade)
    palavra = random.choice(palavras)
    letras = list(palavra)
    random.shuffle(letras)
    return {"palavra": palavra, "embaralhada": ''.join(letras)}

@app.get("/definicao/{palavra}")
def obter_definicao(palavra: str):
    """Busca a definição de uma palavra no Dicio.com.br"""
    definicao = buscar_palavra_dicio(palavra)
    if definicao:
        return {"palavra": palavra, "definicao": definicao, "encontrada": True}
    else:
        return {"palavra": palavra, "definicao": "Definição não encontrada", "encontrada": False}

@app.post('/salvar_ranking')
def salvar_ranking_endpoint(req: RankingRequest):
    ranking = carregar_ranking()
    novo_registro = {
        'nome': req.nome,
        'tempo': req.tempo,
        'erros': req.erros,
        'dificuldade': req.dificuldade,
        'palavra': req.palavra
    }
    ranking.append(novo_registro)
    try:
        salvar_ranking(ranking)
        print(f"[LOG] Ranking salvo em: {os.path.abspath(RANKING_SOLO_ARQ)}")
        print(f"[LOG] Último registro salvo: {novo_registro}")
        print(f"[LOG] Total de registros: {len(ranking)}")
        return {'sucesso': True}
    except Exception as e:
        print(f"[ERRO] Falha ao salvar ranking: {e}")
        return {'sucesso': False, 'erro': str(e)}

@app.get('/ranking_solo')
def ranking_solo(dificuldade: Optional[str] = None):
    ranking = carregar_ranking()
    if dificuldade:
        ranking = [r for r in ranking if r['dificuldade'] == dificuldade]
    ranking_ordenado = sorted(ranking, key=lambda x: x['tempo'] + x['erros']*3)
    return ranking_ordenado 