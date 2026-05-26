# =========================================================
# app.py - GERADOR DE MODO CARREIRA OTIMIZADO v5.0 (CORRIGIDO)
# =========================================================

import os
import json
import random
import time
from collections import deque

from flask import Flask, jsonify
from flask_cors import CORS

from google import genai
from google.genai import types

from dotenv import load_dotenv

# Importação perfeitamente sincronizada com o config.py
from config import (
    MODO_CARREIRA_SCHEMA,
    SYSTEM_INSTRUCTION,
    LIGAS_PERMITIDAS,
    COMPETICOES_CONTINENTAIS
)

# =========================================================
# CONFIGURAÇÃO INICIAL
# =========================================================

load_dotenv()

# O SDK google-genai busca automaticamente a variável GEMINI_API_KEY no ambiente.
try:
    client = genai.Client()
except Exception as e:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("A variável GEMINI_API_KEY não foi encontrada no arquivo .env")
    client = genai.Client(api_key=GEMINI_API_KEY)

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

# =========================================================
# MODELOS DISPONÍVEIS
# =========================================================

MODELOS = [
    "gemini-2.0-flash",      # Mais estável, rápido e excelente com Structured Outputs
    "gemini-1.5-flash",      # Fallback confiável
]

# =========================================================
# HISTÓRICO ANTI-REPETIÇÃO
# =========================================================

historico_clubes = deque(maxlen=20)
historico_ligas = deque(maxlen=10)
historico_paises = deque(maxlen=8)

# =========================================================
# PAÍSES POR LIGA
# =========================================================

PAIS_POR_LIGA = {
    "Premier League": "Inglaterra",
    "EFL Championship": "Inglaterra",
    "EFL League One": "Inglaterra",
    "EFL League Two": "Inglaterra",
    "Barclays Women's Super League": "Inglaterra",

    "LALIGA EA SPORTS": "Espanha",
    "Liga F Moeve": "Espanha",

    "Bundesliga": "Alemanha",
    "Google Pixel Frauen-Bundesliga": "Alemanha",
    "3. Liga": "Alemanha",

    "Ligue 1 McDonald's": "França",
    "Arkema Première Ligue": "França",

    "Serie A Enilive": "Itália",

    "Major League Soccer (MLS)": "EUA",
    "National Women's Soccer League (NWSL)": "EUA",

    "Liga Portugal": "Portugal",
    "Belgium Pro League": "Bélgica",
    "Eredivisie": "Holanda",

    "Liga Profesional de Fútbol (Argentina)": "Argentina",

    "Roshn Saudi League": "Arábia Saudita",
    "K League": "Coreia do Sul",
    "Chinese Super League": "China",

    "A-League": "Austrália",
    "Liga 1": "Indonésia",

    "Ekstraklasa": "Polônia",
    "Austrian Bundesliga": "Áustria",

    "Brack Super League": "Suíça",
    "Superliga": "Dinamarca",

    "Scottish Premiership": "Escócia",

    "SSE Airtricity League Premier Division": "Irlanda",

    "Allsvenskan": "Suécia",
    "Eliteserien": "Noruega"
}

# =========================================================
# MODERAÇÃO
# =========================================================

PALAVRAS_PROIBIDAS = [
    "matar", "terrorismo", "nazismo", "racismo", 
    "sexo", "porno", "droga", "suicidio", "crime"
]

def contem_conteudo_proibido(texto):
    texto = texto.lower()
    return any(palavra in texto for palavra in PALAVRAS_PROIBIDAS)

# =========================================================
# VALIDAÇÃO
# =========================================================

def validar_liga(liga):
    return liga in LIGAS_PERMITIDAS

# =========================================================
# HISTÓRICO
# =========================================================

def registrar_desafio(clube, liga):
    historico_clubes.append(clube.lower())
    historico_ligas.append(liga.lower())
    pais = PAIS_POR_LIGA.get(liga)
    if pais:
        historico_paises.append(pais)

# =========================================================
# ESCOLHER LIGA
# =========================================================

def escolher_liga():
    ligas_disponiveis = [
        liga for liga in LIGAS_PERMITIDAS 
        if liga.lower() not in historico_ligas
    ]
    
    if not ligas_disponiveis:
        ligas_disponiveis = LIGAS_PERMITIDAS
    
    return random.choice(ligas_disponiveis)

# =========================================================
# PROMPT
# =========================================================

def gerar_prompt(liga):
    clubes_bloqueados = ", ".join(list(historico_clubes)[-5:])
    paises_bloqueados = ", ".join(list(historico_paises)[-3:])
    
    prompt = f"""Crie um desafio criativo e realista de Modo Carreira FIFA/EA FC.

LIGA SELECIONADA: {liga}

REGRAS IMPORTANTES:
- Escolha um clube REALISTA dessa liga (NÃO os mais óbvios como Real Madrid, Bayern, PSG)
- Evite clubes recentes: {clubes_bloqueados}
- Evite países recentes: {paises_bloqueados}
- Crie uma narrativa imersiva com contexto histórico real
- Defina 3-4 objetivos específicos e desafiadores
- Recomende 3-5 jogadores REAIS que se encaixam no perfil do clube

Retorne APENAS o JSON, sem markdown ou texto extra."""
    
    return prompt

# =========================================================
# GERAÇÃO DO DESAFIO
# =========================================================

def generate_career_challenge():
    max_tentativas = 3
    
    for tentativa in range(max_tentativas):
        try:
            liga = escolher_liga()
            prompt = gerar_prompt(liga)
            modelo = random.choice(MODELOS)
            
            print(f"\n🔄 Tentativa {tentativa + 1}/{max_tentativas}")
            print(f"📌 Liga: {liga}")
            print(f"🤖 Modelo: {modelo}")
            
            response = client.models.generate_content(
                model=modelo,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    response_schema=MODO_CARREIRA_SCHEMA,
                    temperature=0.75,  
                    max_output_tokens=1500
                )
            )
            
            if not response or not response.text:
                print("❌ Resposta vazia da IA")
                continue
            
            texto = response.text.strip()
            
            # Limpeza preventiva contra blocos de código Markdown indesejados
            if texto.startswith("```json"):
                texto = texto.split("```json")[1].split("```")[0].strip()
            elif texto.startswith("```"):
                texto = texto.split("```")[1].split("```")[0].strip()
            
            desafio = json.loads(texto)
            
            # Validações
            liga_gerada = desafio.get("liga_do_clube", liga)
            clube_gerado = desafio.get("clube_escolhido", "")
            
            if not validar_liga(liga_gerada):
                print(f"⚠️ Liga inválida gerada pela IA: {liga_gerada}")
                continue
            
            if clube_gerado.lower() in historico_clubes:
                print(f"⚠️ Clube repetido detectado: {clube_gerado}")
                continue
            
            # Registrar no histórico
            registrar_desafio(clube_gerado, liga_gerada)
            
            print(f"✅ Desafio gerado com sucesso!")
            print(f"⚽ Clube: {clube_gerado}")
            print(f"🏆 Liga: {liga_gerada}")
            
            return desafio
            
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON: {e}")
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Erro na tentativa {tentativa + 1}: {str(e)}")
            time.sleep(2)
    
    # Fallback realista para evitar travar o frontend em caso de falha de conexão externa
    print("🚨 Todas as tentativas falharam. Acionando modo de contingência.")
    return {
        "clube_escolhido": "Borussia Dortmund",
        "liga_do_clube": "Bundesliga",
        "titulo_do_desafio": "A Muralha Amarela Amortecida",
        "contexto_historico": "O Dortmund estagnou na Bundesliga. Sua missão é reconstruir a identidade de revelar jovens talentos e quebrar a hegemonia nacional usando raça e precisão tática.",
        "objetivos_da_diretoria": [
            "Chegar às quartas de final da UEFA Champions League.",
            "Terminar no G3 da Bundesliga na primeira temporada.",
            "Desenvolver pelo menos 2 jogadores da base com mais de 5 pontos de evolução."
        ],
        "jogadores_recomendados": [
            {
                "nome": "Jamie Gittens",
                "posicao": "PE",
                "clube_atual": "Borussia Dortmund",
                "idade": 21,
                "justificativa": "Velocidade pura e quebra de linhas no drible para furar defesas retrancadas."
            }
        ]
    }

# =========================================================
# ROTAS DA API
# =========================================================

@app.route("/")
def root():
    return jsonify({
        "status": "success",
        "api": "Gerador de Modo Carreira",
        "version": "5.0",
        "modelos_disponiveis": MODELOS,
        "total_ligas": len(LIGAS_PERMITIDAS)
    })

@app.route("/generate", methods=["GET"])
def generate():
    try:
        desafio = generate_career_challenge()
        
        # Verificar conteúdo proibido
        if contem_conteudo_proibido(json.dumps(desafio)):
            return jsonify({
                "status": "error",
                "message": "Conteúdo blocoado pelo sistema de moderação."
            }), 400
        
        return jsonify({
            "status": "success",
            "dados_desafio": desafio,
            "stats": {
                "historico_clubes": list(historico_clubes),
                "historico_ligas": list(historico_ligas),
                "historico_paises": list(historico_paises),
                "total_gerados": len(historico_clubes)
            }
        })
        
    except Exception as e:
        print(f"❌ Erro na rota /generate: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Erro interno: {str(e)}"
        }), 500

@app.route("/stats")
def stats():
    return jsonify({
        "historico_clubes": list(historico_clubes),
        "historico_ligas": list(historico_ligas),
        "historico_paises": list(historico_paises),
        "total_desafios": len(historico_clubes)
    })

@app.route("/ligas")
def ligas():
    return jsonify({
        "total": len(LIGAS_PERMITIDAS),
        "ligas": LIGAS_PERMITIDAS,
        "competicoes_continentais": COMPETICOES_CONTINENTAIS
    })

@app.route("/reset", methods=["POST"])
def reset():
    historico_clubes.clear()
    historico_ligas.clear()
    historico_paises.clear()
    return jsonify({
        "status": "success",
        "message": "Histórico de desafios resetado com sucesso."
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "modelos": MODELOS
    })

# =========================================================
# EXECUÇÃO DO FLASK
# =========================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🎮 GERADOR DE MODO CARREIRA v5.0")
    print("=" * 60)
    print(f"✅ {len(LIGAS_PERMITIDAS)} ligas carregadas")
    print("✅ Sistema anti-repetição ativo")
    print(f"✅ Modelos mapeados: {', '.join(MODELOS)}")
    print("=" * 60)
    print("🌐 API rodando em: http://localhost:5000")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=5000, debug=True)