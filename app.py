# =========================================================
# app.py - GERADOR DE MODO CARREIRA OTIMIZADO v4.2
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
# MODELOS DISPONÍVEIS
# =========================================================

MODELOS = [
    "gemini-3.1-flash-lite",
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

    return any(
        palavra in texto
        for palavra in PALAVRAS_PROIBIDAS
    )

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
        liga
        for liga in LIGAS_PERMITIDAS
        if liga.lower() not in historico_ligas
    ]

    if not ligas_disponiveis:
        ligas_disponiveis = LIGAS_PERMITIDAS

    return random.choice(ligas_disponiveis)

# =========================================================
# PROMPT
# =========================================================

def gerar_prompt(liga):

    clubes_bloqueados = ", ".join(
        list(historico_clubes)[-5:]
    )

    paises_bloqueados = ", ".join(
        list(historico_paises)[-3:]
    )

    prompt = f"""
Crie um desafio criativo e realista de Modo Carreira FIFA.

LIGA:
{liga}

IMPORTANTE:
- Escolha um clube REALISTA dessa liga
- NÃO escolha clubes extremamente óbvios
- Evite repetir clubes recentes

Crie:
- narrativa imersiva
- objetivos difíceis
- restrições únicas
- contexto realista

Evite repetir:
Clubes recentes: {clubes_bloqueados}
Países recentes: {paises_bloqueados}

Retorne apenas JSON válido.
"""

    return prompt

# =========================================================
# GERAÇÃO
# =========================================================

def generate_career_challenge():

    max_tentativas = 3

    for tentativa in range(max_tentativas):

        try:

            liga = escolher_liga()

            prompt = gerar_prompt(liga)

            modelo = random.choice(MODELOS)

            print(f"Modelo usado: {modelo}")

            response = client.models.generate_content(

                model=modelo,

                contents=prompt,

                config=types.GenerateContentConfig(

                    system_instruction=SYSTEM_INSTRUCTION,

                    response_mime_type="application/json",

                    response_schema=MODO_CARREIRA_SCHEMA,

                    temperature=0.9,

                    top_p=0.9,

                    top_k=32,

                    max_output_tokens=500
                )
            )

            if not response.text:

                raise Exception("Resposta vazia da IA.")

            texto = response.text.strip()

            desafio = json.loads(texto)

            liga_gerada = desafio.get(
                "liga_do_clube",
                liga
            )

            clube_gerado = desafio.get(
                "clube_escolhido",
                "Clube não informado"
            )

            # =========================================================
            # VALIDAÇÃO
            # =========================================================

            if not validar_liga(liga_gerada):

                print(f"Liga inválida: {liga_gerada}")

                continue

            if clube_gerado.lower() in historico_clubes:

                print(f"Clube repetido: {clube_gerado}")

                continue

            registrar_desafio(
                clube_gerado,
                liga_gerada
            )

            return desafio

        except json.JSONDecodeError:

            print("JSON inválido recebido.")

            time.sleep(2)

        except Exception as e:

            print(f"Erro tentativa {tentativa + 1}: {e}")

            time.sleep(2)

    return {
        "erro": True,
        "mensagem": "IA temporariamente indisponível."
    }

# =========================================================
# ROTAS
# =========================================================

@app.route("/")
def root():

    return jsonify({
        "status": "success",
        "api": "Gerador de Modo Carreira",
        "version": "4.2",
        "modelos": MODELOS,
        "ligas": len(LIGAS_PERMITIDAS)
    })

@app.route("/generate", methods=["GET"])
def generate():

    try:

        desafio = generate_career_challenge()

        if contem_conteudo_proibido(
            json.dumps(desafio)
        ):

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
    print("🎮 GERADOR DE MODO CARREIRA v4.2")
    print("=" * 60)

    print(f"✅ {len(LIGAS_PERMITIDAS)} ligas carregadas")
    print("✅ Sistema anti-repetição ativo")
    print(f"✅ Modelos: {', '.join(MODELOS)}")

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

    app.run(host="0.0.0.0", port=5000)