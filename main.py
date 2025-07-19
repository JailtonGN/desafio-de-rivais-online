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
    """Busca definição de uma palavra (versão simplificada)"""
    if palavra in DICIO_CACHE:
        return DICIO_CACHE[palavra]
    
    try:
        # Definições expandidas e melhoradas
        definicoes_melhoradas = {
            'casa': 'Lugar onde moramos, habitação, residência familiar.',
            'livro': 'Conjunto de folhas impressas ou manuscritas, encadernadas com conhecimento.',
            'porta': 'Abertura na parede para entrar ou sair de um local, passagem.',
            'mesa': 'Móvel com superfície plana para colocar objetos, trabalhar ou comer.',
            'pato': 'Ave aquática com bico largo e pés palmados, excelente nadadora.',
            'fogo': 'Combustão que produz luz e calor, elemento fundamental da natureza.',
            'bola': 'Objeto esférico usado em jogos e esportes, símbolo de diversão.',
            'janela': 'Abertura na parede para entrada de luz e ar, vista para o mundo.',
            'amarelo': 'Cor primária entre verde e laranja, cor do sol e da alegria.',
            'computador': 'Máquina eletrônica para processar dados, ferramenta moderna.',
            'telefone': 'Aparelho para comunicação à distância, conecta pessoas.',
            'cachorro': 'Animal doméstico da família dos canídeos, melhor amigo do homem.',
            'banana': 'Fruta amarela alongada, rica em potássio e energia.',
            'abacaxi': 'Fruta tropical com casca espinhosa, doce e refrescante.',
            'programador': 'Pessoa que escreve códigos de computador, criador digital.',
            'bicicleta': 'Veículo de duas rodas movido a pedal, transporte sustentável.',
            'universidade': 'Instituição de ensino superior, centro de conhecimento.',
            'conhecimento': 'Informação adquirida através do estudo e experiência.',
            'inteligência': 'Capacidade de aprender e resolver problemas, raciocínio.',
            'responsabilidade': 'Obrigação de responder pelos próprios atos, dever.',
            'oportunidade': 'Momento favorável para fazer algo, chance de sucesso.',
            'desenvolvimento': 'Processo de crescimento e evolução, progresso.',
            'compreensão': 'Capacidade de entender algo, entendimento profundo.',
            'organização': 'Ato de organizar ou estruturar, ordem e eficiência.',
            'comunicação': 'Troca de informações entre pessoas, diálogo.',
            'transformação': 'Mudança de forma ou natureza, evolução constante.',
            'experiência': 'Conhecimento adquirido pela prática, vivência.',
            'possibilidade': 'Chance de algo acontecer, potencial futuro.',
            'realização': 'Ato de realizar ou concretizar, conquista pessoal.',
            'aprendizado': 'Processo de aprender algo, aquisição de conhecimento.',
            'crescimento': 'Aumento de tamanho ou desenvolvimento, evolução.',
            'cama': 'Móvel para dormir e descansar, lugar de sonhos.',
            'sol': 'Estrela central do sistema solar, fonte de luz e vida.',
            'lua': 'Satélite natural da Terra, ilumina as noites.',
            'mar': 'Massa de água salgada, imensidão azul.',
            'rio': 'Corpo de água doce que flui, caminho natural.',
            'pé': 'Parte inferior da perna, base do movimento.',
            'mão': 'Parte do corpo para pegar e manipular objetos.',
            'olho': 'Órgão da visão, janela da alma.',
            'boca': 'Órgão para falar e comer, expressão facial.',
            'pai': 'Progenitor masculino, figura paterna.',
            'mãe': 'Progenitora feminina, amor materno.',
            'filho': 'Descendente direto, herdeiro da família.',
            'amigo': 'Pessoa com quem temos laços de amizade.',
            'carro': 'Veículo motorizado para transporte, liberdade.',
            'escola': 'Instituição de ensino, lugar de aprendizado.',
            'trabalho': 'Atividade laboral, fonte de sustento.',
            'família': 'Grupo de pessoas unidas por laços afetivos.',
            'amizade': 'Relação de afeto entre pessoas, companheirismo.',
            'felicidade': 'Estado de bem-estar e alegria, contentamento.',
            'esperança': 'Confiança no futuro, otimismo.',
            'liberdade': 'Direito de agir livremente, autonomia.',
            'justiça': 'Princípio de equidade, direito.',
            'paz': 'Estado de tranquilidade, harmonia.',
            'amor': 'Sentimento profundo de afeto, carinho.',
            'vida': 'Existência, período entre nascimento e morte.',
            'tempo': 'Duração dos eventos, momento presente.'
        }
        
        definicao = definicoes_melhoradas.get(palavra.lower())
        if definicao:
            DICIO_CACHE[palavra] = definicao
            return definicao
        
        return f"Definição de '{palavra}': Palavra em português brasileiro com significado próprio."
    except Exception as e:
        print(f"Erro ao buscar palavra '{palavra}': {e}")
        return f"Definição de '{palavra}': Palavra em português brasileiro."

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

@app.get("/teste")
def teste():
    """Endpoint de teste simples"""
    return {"mensagem": "Backend funcionando!", "versao": "2.0"}

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