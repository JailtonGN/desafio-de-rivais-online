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

# Cache para palavras do Dicio (versão 2.0)
DICIO_CACHE = {}

# Controle de palavras já usadas por sessão
PALAVRAS_USADAS = {
    'facil': set(),
    'medio': set(),
    'dificil': set()
}

def buscar_palavra_dicio(palavra):
    """Busca definição de uma palavra (versão simplificada para deploy)"""
    if palavra in DICIO_CACHE:
        return DICIO_CACHE[palavra]
    
    # Definições locais expandidas
    definicoes_locais = {
            'casa': 'Lugar onde moramos, habitação, residência familiar.',
            'livro': 'Conjunto de folhas impressas ou manuscritas, encadernadas com conhecimento.',
            'porta': 'Abertura na parede para entrar ou sair de um local, passagem.',
            'mesa': 'Móvel com superfície plana para colocar objetos, trabalhar ou comer.',
            'pato': 'Ave aquática com bico largo e pés palmados, excelente nadadora.',
            'fogo': 'Combustão que produz luz e calor, elemento fundamental da natureza.',
            'bola': 'Objeto esférico usado em jogos e esportes, símbolo de diversão.',
            'amor': 'Sentimento profundo de afeto, carinho e dedicação.',
            'café': 'Bebida quente feita de grãos torrados, estimulante natural.',
            'água': 'Substância líquida essencial para a vida, H2O.',
            'azul': 'Cor do céu e do mar, uma das cores primárias.',
            'rosa': 'Cor suave entre vermelho e branco, cor das flores.',
            'alto': 'Que tem altura considerável, elevado.',
            'baixo': 'Que tem pouca altura, pequeno em estatura.',
            'novo': 'Que foi feito ou criado recentemente, recente.',
            'velho': 'Que existe há muito tempo, antigo.',
            'bom': 'Que tem qualidade positiva, benéfico.',
            'ruim': 'Que tem qualidade negativa, prejudicial.',
            'feliz': 'Que sente alegria e contentamento.',
            'triste': 'Que sente pesar ou melancolia.',
            'forte': 'Que tem força física ou moral.',
            'fraco': 'Que tem pouca força ou resistência.',
            'rico': 'Que possui muitos bens ou recursos.',
            'pobre': 'Que tem poucos recursos financeiros.',
            'jovem': 'Que tem pouca idade, adolescente.',
            'limpo': 'Que está sem sujeira, higiênico.',
            'sujo': 'Que está com sujeira, impuro.',
            'cheio': 'Que está completamente ocupado.',
            'vazio': 'Que não contém nada, desocupado.',
            'claro': 'Que tem muita luz, iluminado.',
            'escuro': 'Que tem pouca luz, sombrio.',
            'fácil': 'Que não apresenta dificuldade.',
            'cima': 'Parte superior, direção ascendente.',
            'dentro': 'No interior de algo, interno.',
            'fora': 'No exterior de algo, externo.',
            'antes': 'Em tempo anterior, precedente.',
            'depois': 'Em tempo posterior, subsequente.',
            'agora': 'No momento presente, atualmente.',
            'sempre': 'Em todos os momentos, constantemente.',
            'nunca': 'Em nenhum momento, jamais.',
            'logo': 'Em breve, em seguida.',
            'auto': 'Que funciona por si mesmo, automático.',
            'alma': 'Parte espiritual do ser humano.',
            'arte': 'Expressão criativa humana.',
            'onde': 'Em que lugar, localização.',
            'meta': 'Objetivo a ser alcançado.',
            'sair': 'Deixar um lugar, partir.',
            'noia': 'Preocupação excessiva, ansiedade.',
            'cela': 'Pequeno compartimento, cela de prisão.',
            'foco': 'Centro de atenção, ponto principal.',
            'face': 'Rosto, expressão facial.',
            'alvo': 'Objetivo, meta a ser atingida.',
            'nojo': 'Sensação de repugnância.',
            'agir': 'Tomar ação, comportar-se.',
            'base': 'Fundamento, suporte.',
            'pose': 'Postura, posição do corpo.',
            'vale': 'Depressão entre montanhas.',
            'todo': 'Completo, inteiro.',
            'ágil': 'Que se move com rapidez.',
            'nada': 'Nenhuma coisa, zero.',
            'quer': 'Deseja, tem vontade.',
            'alva': 'Branca, clara.',
            'alta': 'Que tem altura considerável.',
            'frio': 'Que tem baixa temperatura.',
            'caso': 'Situação, circunstância.',
            'este': 'Este aqui, próximo.',
            'pode': 'Tem permissão, consegue.',
            'lume': 'Luz, claridade.',
            'algo': 'Alguma coisa, um pouco.',
            'belo': 'Bonito, agradável aos olhos.',
            'pena': 'Sentimento de compaixão.',
            'tema': 'Assunto, tópico.',
            'fiel': 'Leal, confiável.',
            'nome': 'Denominação, identificação.',
            'hera': 'Planta trepadeira.',
            'tipo': 'Modelo, padrão.',
            'guia': 'Que orienta, direciona.',
            'luta': 'Combate, disputa.',
            'esse': 'Esse aqui, próximo.',
            'dote': 'Qualidade, talento.',
            'qual': 'Que, qual.',
            'seja': 'Que seja, qualquer que seja.',
            'povo': 'Conjunto de pessoas, população.',
            'nato': 'Nascido, natural.',
            'real': 'Verdadeiro, autêntico.',
            'item': 'Elemento, ponto.',
            'leal': 'Fiel, honesto.',
            'usar': 'Utilizar, empregar.',
            'erro': 'Mistake, falha.',
            'fuga': 'Escape, fuga.',
            'puro': 'Limpo, sem impurezas.',
            'grau': 'Nível, intensidade.',
            'dois': 'Número 2.',
            'orar': 'Fazer oração, rezar.',
            'modo': 'Maneira, forma.',
            'taxa': 'Percentual, valor.',
            'selo': 'Marca, carimbo.',
            'bolo': 'Massa assada, doce.',
            'cair': 'Descer, tombar.',
            'dado': 'Informação, fato.',
            'trem': 'Veículo ferroviário.',
            'obra': 'Trabalho, construção.',
            'aqui': 'Neste lugar.',
            'raro': 'Pouco comum, incomum.',
            'cena': 'Cenário, situação.',
            'gana': 'Desejo, vontade.',
            'fome': 'Sensação de necessidade de comer.',
            'raiz': 'Parte da planta que fica no solo.',
            'cada': 'Cada um, individualmente.',
            'show': 'Apresentação, espetáculo.',
            'cara': 'Rosto, face.',
            'flor': 'Órgão reprodutivo das plantas.',
            'caro': 'Custoso, de alto valor.',
            'aula': 'Sessão de ensino.',
            'hora': 'Unidade de tempo.',
            'deve': 'Deve fazer, obrigação.',
            'seco': 'Sem umidade, árido.',
            'sobe': 'Ascende, vai para cima.',
            'mora': 'Reside, habita.',
            'moço': 'Jovem, rapaz.',
            'feio': 'Não bonito, desagradável.',
            'lixo': 'Resíduo, material descartado.',
            'topo': 'Parte superior, cume.',
            'fofo': 'Macio, suave.',
            'peso': 'Massa, gravidade.',
            'rede': 'Malha de fios entrelaçados.',
            'reto': 'Direto, sem curvas.',
            'vixe': 'Expressão de surpresa.',
            'ramo': 'Galho, parte da árvore.',
            'anel': 'Objeto circular usado como adorno.',
            'bela': 'Bonita, formosa.',
            'odor': 'Cheiro, aroma.',
            'esta': 'Esta aqui, próxima.',
            'liso': 'Sem rugas, liso.',
            'mole': 'Macio, flexível.',
            'rosa': 'Cor suave, flor.',
            'voto': 'Opinião, escolha.',
            'mesa': 'Móvel com superfície plana.',
            'pipa': 'Brinquedo que voa com o vento.',
            'sapo': 'Anfíbio, animal.',
            'boca': 'Órgão para falar e comer.',
            'rato': 'Pequeno roedor.',
            'vela': 'Objeto que ilumina.',
            'olho': 'Órgão da visão.',
            'mimo': 'Carinho, afeto.',
            'fama': 'Reputação, notoriedade.',
            'coco': 'Fruto do coqueiro.',
            'duro': 'Rígido, resistente.',
            'gado': 'Animais de criação.',
            'voar': 'Mover-se pelo ar.',
            'vaga': 'Espaço disponível.',
            'saia': 'Peça de vestuário.',
            'vara': 'Pau, bastão.',
            'nota': 'Observação, comentário.',
            'meia': 'Metade, peça de vestuário.',
            'acha': 'Pensa, considera.',
            'dose': 'Quantidade, porção.',
            'dito': 'Dito, falado.',
            'pesa': 'Tem peso, pesa.',
            'foto': 'Fotografia, imagem.',
            'cepa': 'Variedade, tipo.',
            'luxo': 'Ostentação, riqueza.',
            'cego': 'Sem visão.',
            'dele': 'Pertence a ele.',
            'rota': 'Caminho, direção.',
            'cabo': 'Extremidade, cabo.',
            'leia': 'Leia, leitura.',
            'pura': 'Limpa, sem impurezas.',
            'ilha': 'Terra cercada de água.',
            'foge': 'Escapa, foge.',
            'ouro': 'Metal precioso.',
            'óleo': 'Substância oleosa.',
            'luto': 'Período de luto.',
            'muro': 'Parede, barreira.',
            'seta': 'Indicador, direção.',
            'cama': 'Móvel para dormir.',
            'sono': 'Estado de repouso.',
            'hino': 'Música oficial.',
            'dona': 'Proprietária, senhora.',
            'nora': 'Esposa do filho.',
            'polo': 'Extremidade, polo.',
            'solo': 'Terra, chão.',
            'fala': 'Comunicação verbal.',
            'nata': 'Creme do leite.',
            'laje': 'Laje, laje.',
            'fixa': 'Fixa, estável.',
            'sigo': 'Continuo, sigo.',
            'cima': 'Parte superior.',
            'time': 'Equipe, grupo.',
            'guri': 'Menino, garoto.',
            'nova': 'Nova, recente.',
            'unir': 'Juntar, conectar.',
            'ceia': 'Refeição noturna.',
            'azar': 'Má sorte.',
            'cura': 'Tratamento, cura.',
            'faço': 'Faço, realizo.',
            'anjo': 'Ser celestial.',
            'site': 'Sítio web.',
            'raça': 'Grupo étnico.',
            'copa': 'Competição, taça.',
            'mana': 'Irmã mais velha.',
            'acre': 'Estado brasileiro.',
            'digo': 'Digo, falo.',
            'isto': 'Isto aqui.',
            'sujo': 'Com sujeira.',
            'osso': 'Parte do esqueleto.',
            'raio': 'Descarga elétrica.',
            'vago': 'Indefinido, vago.',
            'mapa': 'Representação geográfica.',
            'mago': 'Feiticeiro, mago.',
            'sala': 'Cômodo da casa.',
            'lado': 'Lateral, lado.',
            'sabe': 'Conhece, sabe.',
            'seca': 'Sem umidade.',
            'pomo': 'Fruto, maçã.',
            'boia': 'Objeto flutuante.',
            'leva': 'Transporta, leva.',
            'pior': 'Mais ruim.',
            'momo': 'Carnaval, festa.',
            'vivo': 'Com vida.',
            'caju': 'Fruto do cajueiro.',
            'coxa': 'Parte da perna.',
            'nela': 'Nela, dentro dela.',
            'mega': 'Muito grande.',
            'veto': 'Proibição, veto.',
            'riso': 'Riso, risada.',
            'dama': 'Senhora, dama.',
            'luna': 'Lua, satélite.',
            'vaso': 'Recipiente.',
            'data': 'Data, dia.',
            'pede': 'Solicita, pede.',
            'roça': 'Lavoura, plantação.',
            'pedi': 'Pedido, solicitei.',
            'viva': 'Com vida.',
            'faia': 'Árvore, faia.',
            'oral': 'Verbal, falado.',
            'pera': 'Fruta, pera.',
            'cola': 'Substância adesiva.',
            'luar': 'Luz da lua.',
            'onda': 'Onda do mar.',
            'cabe': 'Cabe, cabe.',
            'seda': 'Tecido fino.',
            'sopa': 'Alimento líquido.',
            'vaca': 'Animal bovino.',
            'moda': 'Tendência, moda.',
            'cruz': 'Símbolo cristão.',
            'pane': 'Falha, pane.',
            'nulo': 'Sem valor, nulo.',
            'bula': 'Instruções de medicamento.',
            'musa': 'Inspiração, musa.',
            'pele': 'Tecido que cobre o corpo.',
            'atar': 'Amarrar, atar.',
            'caça': 'Busca, caça.',
            'cova': 'Buraco, cova.',
            'sois': 'Sois, são.',
            'toga': 'Vestimenta, toga.',
            'maré': 'Movimento do mar.',
            'doze': 'Número 12.',
            'beco': 'Passagem estreita.',
            'dedo': 'Parte da mão.',
            'gaze': 'Tecido fino.',
            'mãos': 'Partes das mãos.',
            'gera': 'Produz, gera.',
            'papo': 'Conversa, papo.',
            'táxi': 'Veículo de transporte.',
            'mano': 'Irmão, mano.',
            'tatu': 'Animal, tatu.',
            'pais': 'País, nação.',
            'roxo': 'Cor, roxo.',
            'tara': 'Defeito, tara.',
            'cria': 'Filhote, cria.',
            'frei': 'Religioso, frei.',
            'sete': 'Número 7.',
            'tapa': 'Golpe, tapa.',
            'bala': 'Projétil, bala.',
            'teto': 'Parte superior da casa.',
            'dono': 'Proprietário, dono.',
            'dias': 'Períodos de tempo.',
            'alho': 'Tempero, alho.',
            'zona': 'Área, zona.',
            'grão': 'Semente, grão.',
            'veia': 'Vaso sanguíneo.',
            'dita': 'Dita, falada.',
            'mato': 'Vegetação, mato.',
            'lago': 'Massa de água.',
            'jipe': 'Veículo, jipe.',
            'urso': 'Animal, urso.',
            'faca': 'Instrumento cortante.',
            'gelo': 'Água congelada.',
            'arco': 'Curva, arco.',
            'oito': 'Número 8.',
            'rama': 'Galho, rama.',
            'cera': 'Substância, cera.',
            'mala': 'Bagagem, mala.',
            'neve': 'Água congelada.',
            'onça': 'Animal, onça.',
            'tina': 'Recipiente, tina.',
            'erva': 'Planta, erva.',
            'arma': 'Instrumento de defesa.',
            'ator': 'Artista, ator.',
            'duas': 'Número 2.',
            'lama': 'Barro, lama.',
            'fada': 'Ser mágico, fada.',
            'pino': 'Pequeno prego.',
            'seis': 'Número 6.',
            'galo': 'Ave, galo.',
            'muda': 'Sem voz, muda.',
            'copo': 'Recipiente, copo.',
            'silo': 'Armazém, silo.',
            'fino': 'Delgado, fino.',
            'olmo': 'Árvore, olmo.',
            'baía': 'Enseada, baía.',
            'tour': 'Passeio, tour.',
            'fria': 'Com baixa temperatura.',
            'suco': 'Bebida, suco.',
            'gume': 'Fio da lâmina.',
            'cuia': 'Recipiente, cuia.',
            'lobo': 'Animal, lobo.',
            'bote': 'Barco pequeno.',
            'loja': 'Estabelecimento, loja.',
            'mini': 'Pequeno, mini.',
            'raia': 'Faixa, raia.',
            'mofo': 'Fungo, mofo.',
            'bode': 'Animal, bode.',
            'égua': 'Animal, égua.',
            'moto': 'Veículo, moto.',
            'tela': 'Superfície, tela.',
            'toca': 'Toca, esconderijo.',
            'juro': 'Prometo, juro.',
            'lote': 'Parcela, lote.',
            'peru': 'Ave, peru.',
            'soma': 'Adição, soma.',
            'filo': 'Filo, filo.',
            'cone': 'Forma geométrica.',
            'doer': 'Causar dor.',
            'vila': 'Pequena cidade.',
            'feno': 'Alimento para animais.',
            'nega': 'Negar, nega.',
            'leoa': 'Animal, leoa.',
            'vala': 'Canal, vala.',
            'mata': 'Floresta, mata.',
            'pata': 'Pé do animal.',
            'veja': 'Veja, observe.',
            'cega': 'Sem visão.',
            'olha': 'Olha, observa.',
            'saci': 'Personagem folclórico.',
            'meme': 'Conteúdo viral.',
            'poda': 'Corte, poda.',
            'liga': 'União, liga.',
            'mico': 'Animal, mico.',
            'lata': 'Recipiente, lata.',
            'anta': 'Animal, anta.',
            'muco': 'Substância, muco.',
            'pico': 'Ponto mais alto.',
            'pote': 'Recipiente, pote.',
            'saco': 'Recipiente, saco.',
            'lava': 'Rocha derretida.',
            'peta': 'Peta, peta.',
            'luva': 'Proteção para mãos.',
            'roda': 'Objeto circular.',
            'foca': 'Animal marinho.',
            'fumo': 'Fumaça, fumo.',
            'tira': 'Tira, remove.',
            'gala': 'Festa, gala.',
            'pego': 'Pego, capturado.',
            'sino': 'Objeto sonoro.',
            'menu': 'Lista, menu.',
            'bati': 'Bati, golpeei.',
            'baga': 'Fruto pequeno.',
            'chat': 'Conversa, chat.',
            'tava': 'Estava, estava.',
            'guru': 'Mestre, guru.',
            'mira': 'Alvo, mira.',
            'mona': 'Mona, mona.',
            'gibi': 'Revista em quadrinhos.',
            'isca': 'Isca, isca.',
            'dura': 'Rígida, dura.',
            'fita': 'Fita, fita.',
            'capa': 'Cobertura, capa.',
            'sova': 'Golpe, sova.',
            'fina': 'Delgada, fina.',
            'furo': 'Buraco, furo.',
            'demo': 'Demonstração, demo.',
            'vime': 'Material, vime.',
            'caco': 'Pedaço, caco.',
            'ralo': 'Ralo, ralo.',
            'bule': 'Recipiente, bule.',
            'trio': 'Grupo de três.',
            'ruga': 'Ruga, ruga.',
            'pisa': 'Pisa, pisa.',
            'migo': 'Comigo, comigo.',
            'lido': 'Lido, lido.',
            'moca': 'Moça, moça.',
            'doca': 'Doca, doca.',
            'fila': 'Sequência, fila.',
            'alça': 'Alça, alça.',
            'fava': 'Legume, fava.',
            'bota': 'Calçado, bota.',
            'jato': 'Jato, jato.',
            'rolo': 'Cilindro, rolo.',
            'pupa': 'Pupa, pupa.',
            'reta': 'Linha reta.',
            'favo': 'Favo de mel.',
            'cava': 'Cava, cava.',
            'mola': 'Mola, mola.',
            'saio': 'Saio, saio.',
            'dual': 'Duplo, dual.',
            'arca': 'Arca, arca.',
            'seto': 'Seto, seto.',
            'soro': 'Soro, soro.',
            'toma': 'Toma, toma.',
            'gema': 'Gema, gema.',
            'nele': 'Nele, nele.',
            'noda': 'Noda, noda.',
            'rodo': 'Rodo, rodo.',
            'nave': 'Nave, nave.',
            'puxo': 'Puxo, puxo.',
            'viga': 'Viga, viga.',
            'tiro': 'Tiro, tiro.',
            'cebo': 'Cebo, cebo.',
            'deck': 'Deck, deck.',
            'elmo': 'Elmo, elmo.',
            'paga': 'Paga, paga.',
            'bate': 'Bate, bate.',
            'duna': 'Duna, duna.',
            'gira': 'Gira, gira.',
            'cana': 'Cana, cana.',
            'gari': 'Gari, gari.',
            'nove': 'Número 9.',
            'boas': 'Boas, boas.',
            'lima': 'Lima, lima.',
            'piso': 'Piso, piso.',
            'fofa': 'Macia, fofa.',
            'soco': 'Soco, soco.',
            'grua': 'Grua, grua.',
            'urna': 'Urna, urna.',
            'abra': 'Abra, abra.',
            'pano': 'Pano, pano.',
            'roer': 'Roer, roer.',
            'nano': 'Nano, nano.',
            'viso': 'Viso, viso.',
            'rega': 'Rega, rega.',
            'paca': 'Paca, paca.',
            'miga': 'Miga, miga.',
            'pega': 'Pega, pega.',
            'roxa': 'Roxa, roxa.',
            'bico': 'Bico, bico.',
            'fico': 'Fico, fico.',
            'maga': 'Maga, maga.',
            'tico': 'Tico, tico.',
            'gota': 'Gota, gota.',
            'puxa': 'Puxa, puxa.',
            'faro': 'Faro, faro.',
            'cora': 'Cora, cora.',
            'levo': 'Levo, levo.',
            'mula': 'Mula, mula.',
            'lero': 'Lero, lero.',
            'doma': 'Doma, doma.',
            'pira': 'Pira, pira.',
            'sola': 'Sola, sola.',
            'alar': 'Alar, alar.',
            'roco': 'Roco, roco.',
            'apar': 'Apar, apar.',
            'gata': 'Gata, gata.',
            'nona': 'Nona, nona.',
            'lula': 'Lula, lula.',
            'abre': 'Abre, abre.',
            'bica': 'Bica, bica.',
            'gogo': 'Gogo, gogo.',
            'gomo': 'Gomo, gomo.',
            'rela': 'Rela, rela.',
            'bole': 'Bole, bole.',
            'avós': 'Avós, avós.',
            'cubo': 'Cubo, cubo.',
            'ache': 'Ache, ache.',
            'kilo': 'Kilo, kilo.',
            'loca': 'Loca, loca.',
            'palo': 'Palo, palo.',
            'papa': 'Papa, papa.',
            'tamo': 'Tamo, tamo.',
            'rapa': 'Rapa, rapa.',
            'triz': 'Triz, triz.',
            'siga': 'Siga, siga.',
            'mate': 'Mate, mate.',
            'gude': 'Gude, gude.',
            'pila': 'Pila, pila.',
            'cuca': 'Cuca, cuca.',
            'cast': 'Cast, cast.',
            'adir': 'Adir, adir.',
            'baba': 'Baba, baba.',
            'siri': 'Siri, siri.',
            'puma': 'Puma, puma.',
            'toco': 'Toco, toco.',
            'godo': 'Godo, godo.',
            'rubi': 'Rubi, rubi.',
            'neto': 'Neto, neto.',
            'bato': 'Bato, bato.',
            'anis': 'Anis, anis.',
            'cica': 'Cica, cica.',
            'porta': 'Abertura na parede.',
            'livro': 'Conjunto de folhas.',
            'mesa': 'Móvel com superfície plana.',
            'cama': 'Móvel para dormir.',
            'sala': 'Cômodo da casa.',
            'rua': 'Via pública.',
            'ponte': 'Estrutura sobre água.',
            'hotel': 'Estabelecimento hoteleiro.',
            'museu': 'Local de exposição.',
            'igreja': 'Templo religioso.',
            'cidade': 'Centro urbano.',
            'estado': 'Unidade federativa.',
            'país': 'Nação, território.',
            'sol': 'Estrela central.',
            'lua': 'Satélite natural.',
            'estrela': 'Corpo celeste.',
            'nuvem': 'Massa de vapor d\'água.',
            'vulcão': 'Montanha que expele lava.',
            'vale': 'Depressão entre montanhas.',
            'rio': 'Corpo de água doce.',
            'mar': 'Massa de água salgada.',
            'oceano': 'Grande massa de água.',
            'ilha': 'Terra cercada de água.',
            'chuva': 'Precipitação de água.'
        }
    
    definicao = definicoes_locais.get(palavra.lower())
    if definicao:
        DICIO_CACHE[palavra] = definicao
        return definicao
    
    return f"Definição de '{palavra}': Palavra em português brasileiro com significado próprio."

def obter_palavras_por_dificuldade(dificuldade):
    """Retorna palavras baseadas na dificuldade"""
    if dificuldade == 'facil':
        return [
            # Palavras com 4-5 letras
            # 4 letras
            "amor", "casa", "bola", "fogo", "pato", "gato", "cão", "pão", "café", "água", "azul", "rosa", "alto", "baixo", "novo", "velho", "bom", "ruim", "feliz", "triste",
            "forte", "fraco", "rico", "pobre", "jovem", "limpo", "sujo", "cheio", "vazio", "claro", "escuro", "fácil", "cima", "baixo", "dentro", "fora", "antes", "depois", "agora", "sempre",
            "nunca", "logo", "auto", "alma", "arte", "onde", "meta", "sair", "noia", "cela", "foco", "face", "alvo", "nojo", "alto", "agir", "base", "pose", "vale", "todo",
            "novo", "ágil", "nada", "quer", "alva", "alta", "frio", "caso", "fora", "este", "pode", "lume", "algo", "belo", "pena", "tema", "fiel", "nome", "hera", "tipo", "guia", "luta",
            "esse", "dote", "qual", "seja", "povo", "nato", "real", "item", "leal", "usar", "erro", "café", "fuga", "puro", "grau", "dois", "orar", "modo", "taxa", "selo", "bolo", "cair",
            "dado", "trem", "obra", "gato", "aqui", "raro", "cena", "gana", "fome", "raiz", "cada", "show", "cara", "flor", "caro", "aula", "hora", "rico", "deve", "seco", "sobe", "mora",
            "moço", "face", "feio", "lixo", "topo", "fofo", "peso", "rede", "reto", "vixe", "ramo", "anel", "nada", "quer", "bela", "odor", "esta", "liso", "mole", "rosa", "voto", "mesa",
            "pipa", "sapo", "boca", "rato", "vela", "olho", "mimo", "fama", "coco", "duro", "gado", "voar", "vaga", "saia", "vara", "nota", "meia", "acha", "dose", "dito", "pesa", "foto",
            "cepa", "luxo", "cego", "dele", "rota", "cabo", "leia", "pura", "ilha", "foge", "ouro", "óleo", "luto", "muro", "seta", "cama", "sono", "hino", "dona", "nora", "polo", "solo",
            "fala", "nata", "laje", "fixa", "sigo", "cima", "time", "guri", "nova", "unir", "ceia", "azar", "cura", "faço", "anjo", "site", "raça", "copa", "mana", "acre", "digo", "isto",
            "sujo", "osso", "raio", "vago", "mapa", "mago", "sala", "lado", "sabe", "seca", "pomo", "boia", "leva", "pior", "momo", "vivo", "caju", "coxa", "nela", "mega", "veto", "riso",
            "dama", "luna", "vaso", "data", "pede", "roça", "pedi", "viva", "faia", "oral", "pera", "cola", "luar", "onda", "cabe", "seda", "sopa", "vaca", "moda", "cruz", "pane", "nulo",
            "bula", "musa", "pele", "atar", "caça", "cova", "sois", "toga", "maré", "doze", "beco", "dedo", "gaze", "mãos", "gera", "papo", "táxi", "mano", "tatu", "pais", "roxo", "tara",
            "cria", "frei", "sete", "tapa", "bala", "teto", "dono", "dias", "alho", "zona", "grão", "veia", "dita", "mato", "lago", "jipe", "urso", "faca", "gelo", "arco", "oito", "rama",
            "cera", "mala", "neve", "onça", "tina", "erva", "arma", "ator", "duas", "lama", "fada", "pino", "seis", "galo", "muda", "copo", "silo", "fino", "olmo", "baía", "tour", "fria",
            "suco", "gume", "cuia", "lobo", "bote", "loja", "mini", "raia", "mofo", "bode", "égua", "moto", "tela", "toca", "juro", "lote", "peru", "soma", "filo", "cone", "doer", "vila",
            "feno", "nega", "leoa", "vala", "mata", "pata", "veja", "cega", "olha", "saci", "meme", "poda", "liga", "mico", "lata", "anta", "muco", "pico", "pote", "saco", "lava", "peta",
            "luva", "roda", "foca", "fumo", "tira", "gala", "pego", "sino", "menu", "bati", "baga", "chat", "tava", "guru", "mira", "mona", "gibi", "isca", "dura", "fita", "capa", "sova",
            "fina", "furo", "demo", "vime", "caco", "ralo", "bule", "trio", "ruga", "pisa", "migo", "lido", "moca", "doca", "fila", "alça", "fava", "bota", "jato", "rolo", "pupa", "reta",
            "favo", "cava", "mola", "saio", "dual", "arca", "seto", "soro", "toma", "gema", "nele", "noda", "rodo", "nave", "puxo", "viga", "tiro", "cebo", "deck", "elmo", "paga", "bate",
            "duna", "gira", "cana", "gari", "nove", "boas", "lima", "piso", "fofa", "soco", "grua", "urna", "abra", "pano", "roer", "nano", "viso", "rega", "paca", "miga", "pega", "roxa",
            "bico", "fico", "maga", "tico", "gota", "puxa", "faro", "cora", "levo", "mula", "lero", "doma", "pira", "sola", "alar", "roco", "apar", "gata", "nona", "lula", "abre", "bica",
            "gogo", "gomo", "rela", "bole", "avós", "cubo", "ache", "kilo", "loca", "palo", "papa", "tamo", "rapa", "triz", "siga", "mate", "gude", "pila", "cuca", "cast", "adir", "baba",
            "siri", "puma", "toco", "godo", "rubi", "neto", "bato", "anis", "cica",
            # 5 letras
            "porta", "mesa", "cama", "sala", "ponte", "hotel", "museu", "igreja", "cidade", "estado", "sol", "lua", "estrela", "nuvem", "vulcão", "vale", "rio", "mar", "oceano", "ilha", "chuva"
        ]
    elif dificuldade == 'medio':
        return [
            # Palavras com 6-8 letras
            "janela", "amarelo", "cachorro", "banana", "carro", "escola", "trabalho", "família", "amizade", "felicidade", "esperança", "liberdade", "justiça", "música", "arte", "ciência", "história", "geografia", "matemática", "português",
            "inglês", "espanhol", "francês", "alemão", "italiano", "chinês", "japonês", "coreano", "russo", "árabe", "hebraico", "latim", "grego", "sânscrito", "medicina", "direito", "engenharia", "arquitetura", "psicologia", "filosofia",
            "sociologia", "antropologia", "economia", "política", "religião", "esporte", "teatro", "cinema", "literatura", "poesia", "romance", "contos", "crônicas", "biografia", "memórias", "jornal", "revista", "biblioteca", "galeria",
            "exposição", "concerto", "pintura", "escultura", "fotografia", "televisão", "caminho", "cozinha", "banheiro", "quarto", "escritório", "garagem", "parque", "avenida", "estrada", "túnel", "viaduto", "prédio", "apartamento",
            "condomínio", "restaurante", "shopping", "supermercado", "farmácia", "hospital", "universidade", "igreja", "templo", "mesquita", "sinagoga", "continente", "planeta", "galáxia", "universo", "natureza", "ambiente", "ecologia",
            "sustentabilidade", "reciclagem", "energia", "eletricidade", "tempestade", "tornado", "furacão", "terremoto", "montanha", "península", "deserto", "floresta", "savana", "tundra", "computador", "telefone", "autobiografia"
        ]
    else:  # dificil
        return [
            # Palavras com 8+ letras
            "abacaxi", "dificuldade", "programador", "bicicleta", "universidade", "conhecimento", "inteligência", "responsabilidade", "oportunidade", "desenvolvimento", "compreensão", "organização", "comunicação", "transformação", "experiência", "possibilidade", "realização", "aprendizado", "crescimento",
            "tecnologia", "inovação", "criatividade", "imaginação", "inspiração", "motivação", "dedicação", "perseverança", "determinação", "coragem", "confiança", "autoestima", "autoconhecimento", "autodisciplina", "autocontrole", "autoconfiança", "autodeterminação", "autorealização",
            "sustentabilidade", "biodiversidade", "ecossistema", "preservação", "conservação", "reciclagem", "reutilização", "renovação", "regeneração", "restauração", "reconstrução", "reformulação", "reestruturação", "reorganização", "reorientação", "redirecionamento", "replanejamento", "reprogramação", "reconfiguração",
            "interdisciplinaridade", "multidisciplinaridade", "transdisciplinaridade", "interculturalidade", "multiculturalidade", "transculturalidade", "internacionalização", "globalização", "mundialização", "universalização", "democratização", "modernização", "industrialização", "urbanização", "digitalização", "virtualização", "automatização", "robotização",
            "matemática", "português", "espanhol", "francês", "alemão", "italiano", "chinês", "japonês", "coreano", "hebraico", "sânscrito", "engenharia", "arquitetura", "psicologia", "filosofia", "sociologia", "antropologia", "literatura", "biografia", "autobiografia", "biblioteca", "exposição", "fotografia", "televisão", "apartamento", "condomínio", "restaurante", "supermercado", "farmácia", "hospital", "universidade", "mesquita", "sinagoga", "eletricidade", "tempestade", "terremoto"
        ]

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
    
    # Filtra palavras já usadas
    palavras_disponiveis = [p for p in palavras if p not in PALAVRAS_USADAS[dificuldade]]
    
    # Se todas as palavras foram usadas, reseta a lista
    if not palavras_disponiveis:
        PALAVRAS_USADAS[dificuldade].clear()
        palavras_disponiveis = palavras
    
    # Sorteia uma palavra não usada
    palavra = random.choice(palavras_disponiveis)
    
    # Marca como usada
    PALAVRAS_USADAS[dificuldade].add(palavra)
    
    letras = list(palavra)
    random.shuffle(letras)
    
    return {
        "palavra": palavra, 
        "embaralhada": ''.join(letras),
        "palavras_restantes": len(palavras) - len(PALAVRAS_USADAS[dificuldade])
    }

@app.get("/definicao/{palavra}")
def obter_definicao(palavra: str):
    """Busca a definição de uma palavra (versão 2.0)"""
    definicao = buscar_palavra_dicio(palavra)
    if definicao:
        return {"palavra": palavra, "definicao": definicao, "encontrada": True}
    else:
        return {"palavra": palavra, "definicao": "Definição não encontrada", "encontrada": False}

@app.get("/teste")
def teste():
    """Endpoint de teste simples"""
    return {"mensagem": "Backend funcionando!", "versao": "2.0"}

@app.post("/reset_palavras")
def reset_palavras():
    """Reseta as palavras já usadas"""
    global PALAVRAS_USADAS
    PALAVRAS_USADAS = {
        'facil': set(),
        'medio': set(),
        'dificil': set()
    }
    return {"mensagem": "Palavras resetadas com sucesso!"}

@app.get("/status_palavras")
def status_palavras():
    """Mostra quantas palavras já foram usadas"""
    total_facil = len(obter_palavras_por_dificuldade('facil'))
    total_medio = len(obter_palavras_por_dificuldade('medio'))
    total_dificil = len(obter_palavras_por_dificuldade('dificil'))
    
    return {
        "facil": {
            "total": total_facil,
            "usadas": len(PALAVRAS_USADAS['facil']),
            "restantes": total_facil - len(PALAVRAS_USADAS['facil'])
        },
        "medio": {
            "total": total_medio,
            "usadas": len(PALAVRAS_USADAS['medio']),
            "restantes": total_medio - len(PALAVRAS_USADAS['medio'])
        },
        "dificil": {
            "total": total_dificil,
            "usadas": len(PALAVRAS_USADAS['dificil']),
            "restantes": total_dificil - len(PALAVRAS_USADAS['dificil'])
        }
    }

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