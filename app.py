# =========================================================
# app.py - GERADOR DE MODO CARREIRA OTIMIZADO v4.0
# =========================================================

import os
import json
import random
from collections import deque

from flask import Flask, jsonify
from flask_cors import CORS

from google import genai
from google.genai import types

from dotenv import load_dotenv

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

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("A variável GEMINI_API_KEY não foi encontrada.")

client = genai.Client(api_key=GEMINI_API_KEY)

app = Flask(__name__)
CORS(app)

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
# CLUBES POR LIGA
# =========================================================

CLUBES_POR_LIGA = {
    "Premier League": [
        "Brighton",
        "Crystal Palace",
        "Wolves",
        "Bournemouth",
        "Brentford"
    ],

    "Bundesliga": [
        "Stuttgart",
        "Mainz",
        "Werder Bremen",
        "Augsburg"
    ],

    "Serie A Enilive": [
        "Torino",
        "Udinese",
        "Parma",
        "Genoa"
    ],

    "LALIGA EA SPORTS": [
        "Real Betis",
        "Celta Vigo",
        "Getafe",
        "Osasuna"
    ],

    "Liga Portugal": [
        "Braga",
        "Boavista",
        "Vitória SC"
    ],

    "Eredivisie": [
        "AZ Alkmaar",
        "Twente",
        "Heerenveen"
    ],

    "Scottish Premiership": [
        "Hearts",
        "Hibernian",
        "Aberdeen"
    ]
}

# =========================================================
# MODERAÇÃO
# =========================================================

PALAVRAS_PROIBIDAS = [
    "matar",
    "terrorismo",
    "nazismo",
    "racismo",
    "sexo",
    "porno",
    "droga",
    "suicidio",
    "crime"
]

def contem_conteudo_proibido(texto):
    texto = texto.lower()
    return any(p in texto for p in PALAVRAS_PROIBIDAS)

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
# ESCOLHAS INTELIGENTES
# =========================================================

def escolher_liga():

    ligas_disponiveis = [
        liga for liga in LIGAS_PERMITIDAS
        if liga.lower() not in historico_ligas
    ]

    if not ligas_disponiveis:
        ligas_disponiveis = LIGAS_PERMITIDAS

    return random.choice(ligas_disponiveis)

def escolher_clube(liga):

    clubes = CLUBES_POR_LIGA.get(liga)

    if not clubes:
        return None

    clubes_disponiveis = [
        clube for clube in clubes
        if clube.lower() not in historico_clubes
    ]

    if not clubes_disponiveis:
        clubes_disponiveis = clubes

    return random.choice(clubes_disponiveis)

# =========================================================
# PROMPT OTIMIZADO
# =========================================================

def gerar_prompt(liga, clube):

    clubes_bloqueados = ", ".join(list(historico_clubes)[-5:])
    paises_bloqueados = ", ".join(list(historico_paises)[-3:])

    prompt = f"""
Crie um desafio de Modo Carreira extremamente criativo.

LIGA:
{liga}

CLUBE:
{clube}

REGRAS:
- Não repita ideias genéricas
- Crie narrativa cinematográfica
- Use contexto histórico realista
- Gere objetivos difíceis
- Faça algo imersivo

EVITAR:
Clubes recentes: {clubes_bloqueados}
Países recentes: {paises_bloqueados}

Retorne APENAS JSON válido.
"""

    return prompt

# =========================================================
# GERAÇÃO
# =========================================================

def generate_career_challenge():

    max_tentativas = 2

    for tentativa in range(max_tentativas):

        try:

            liga = escolher_liga()

            clube = escolher_clube(liga)

            if not clube:
                clube = "Escolha automaticamente"

            prompt = gerar_prompt(liga, clube)

            response = client.models.generate_content(

                model="gemini-2.5-flash-lite",

                contents=prompt,

                config=types.GenerateContentConfig(

                    system_instruction=SYSTEM_INSTRUCTION,

                    response_mime_type="application/json",

                    response_schema=MODO_CARREIRA_SCHEMA,

                    temperature=1.05,

                    top_p=0.9,

                    top_k=32,

                    max_output_tokens=650
                )
            )

            texto = response.text.strip()

            desafio = json.loads(texto)

            liga_gerada = desafio.get("liga_do_clube", liga)
            clube_gerado = desafio.get("clube_escolhido", clube)

            # =========================================================
            # VALIDAÇÃO
            # =========================================================

            if not validar_liga(liga_gerada):

                print(f"Liga inválida: {liga_gerada}")

                continue

            if clube_gerado.lower() in historico_clubes:

                print(f"Clube repetido: {clube_gerado}")

                continue

            registrar_desafio(clube_gerado, liga_gerada)

            return desafio

        except Exception as e:

            print(f"Erro tentativa {tentativa + 1}: {e}")

            if tentativa == max_tentativas - 1:
                raise

    raise Exception("Falha ao gerar desafio válido.")

# =========================================================
# ROTAS
# =========================================================

@app.route("/")
def root():

    return jsonify({
        "status": "success",
        "api": "Gerador de Modo Carreira",
        "version": "4.0",
        "modelo": "gemini-2.5-flash-lite",
        "ligas": len(LIGAS_PERMITIDAS)
    })

@app.route("/generate", methods=["GET"])
def generate():

    try:

        desafio = generate_career_challenge()

        if contem_conteudo_proibido(json.dumps(desafio)):

            return jsonify({
                "status": "error",
                "message": "Conteúdo bloqueado."
            }), 400

        return jsonify({
            "status": "success",
            "dados_desafio": desafio,
            "stats": {
                "historico_clubes": list(historico_clubes),
                "historico_ligas": list(historico_ligas),
                "historico_paises": list(historico_paises)
            }
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
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
        "competicoes": COMPETICOES_CONTINENTAIS
    })

@app.route("/reset", methods=["POST"])
def reset():

    historico_clubes.clear()
    historico_ligas.clear()
    historico_paises.clear()

    return jsonify({
        "status": "success",
        "message": "Histórico resetado."
    })

# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("🎮 GERADOR DE MODO CARREIRA v4.0")
    print("=" * 60)

    print(f"✅ {len(LIGAS_PERMITIDAS)} ligas carregadas")
    print(f"✅ Sistema anti-repetição ativo")
    print(f"✅ Modelo: gemini-2.5-flash-lite")

    print("=" * 60)

    print("🌐 API:")
    print("http://localhost:5000")

    print("=" * 60)

    print("📌 ROTAS:")
    print("/generate")
    print("/stats")
    print("/ligas")
    print("/reset")

    print("=" * 60)

    app.run(debug=True)