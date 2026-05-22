# app.py

import os
import json
from flask import Flask, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Importa o novo schema e instrução do config.py
from config import MODO_CARREIRA_SCHEMA, SYSTEM_INSTRUCTION

# =========================================================
# CONFIGURAÇÕES INICIAIS
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("A variável GEMINI_API_KEY não foi encontrada no .env")

client = genai.Client(api_key=GEMINI_API_KEY)

app = Flask(__name__)
CORS(app)

# =========================================================
# SEGURANÇA / MODERAÇÃO
# =========================================================

PALAVRAS_PROIBIDAS = [
    "matar", "assassinar", "bomba", "terrorismo", "arma", "violencia",
    "racismo", "nazismo", "preconceito", "homofobia",
    "sexo", "porno", "pornografia", "estupr", "pedofilia",
    "cocaina", "maconha", "droga", "crack",
    "suicidio", "automutilacao",
    "hackear", "crime",
    "ignore previous instructions", "ignore all instructions",
    "developer mode", "dan mode", "jailbreak", "system instruction", "prompt injection"
]

def contem_conteudo_proibido(texto):
    texto = texto.lower()
    for palavra in PALAVRAS_PROIBIDAS:
        if palavra in texto:
            return True
    return False

# =========================================================
# GERAÇÃO DO DESAFIO (OTIMIZADA)
# =========================================================

def generate_career_challenge():

    conteudo_prompt = """
    Gere um desafio criativo e realista de Modo Carreira para um clube de futebol.

    Escolha aleatoriamente:
    - um clube
    - uma narrativa
    - objetivos
    - regras
    - dificuldades

    O desafio deve ser:
    - original
    - imersivo
    - variado
    - divertido
    - sem repetir ideias genéricas
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=conteudo_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,

            response_mime_type="application/json",
            response_schema=MODO_CARREIRA_SCHEMA,

            # MAIS RÁPIDO
            max_output_tokens=700,

            # MAIS CRIATIVO SEM VIRAR CAOS
            temperature=1.25,
            top_p=0.95,
            top_k=40,

            # EVITA RESPOSTAS MUITO LONGAS
            candidate_count=1
        )
    )

    return response.text

    return response.text

# =========================================================
# ROTAS
# =========================================================

@app.route("/")
def root():
    return jsonify({
        "status": "success",
        "message": "API Gerador de Modo Carreira funcionando!",
        "version": "1.0"
    }), 200

@app.route("/generate", methods=["GET"])
def generate():
    try:
        # =================================================
        # GERAÇÃO DIRETAMENTE PELA IA
        # =================================================
        desafio_json_string = generate_career_challenge()

        # =================================================
        # MODERAÇÃO DA RESPOSTA
        # =================================================
        if contem_conteudo_proibido(desafio_json_string):
            return jsonify({
                "status": "error",
                "message": "A resposta gerada foi bloqueada por conter termos sensíveis."
            }), 400

        # =================================================
        # CONVERTE JSON E ENTREGA O RESULTADO
        # =================================================
        desafio_estruturado = json.loads(desafio_json_string)

        return jsonify({
            "status": "success",
            "dados_desafio": desafio_estruturado
        }), 200

    except json.JSONDecodeError:
        return jsonify({
            "status": "error",
            "message": "Erro ao interpretar o JSON gerado pela IA."
        }), 500

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro interno: {str(e)}"
        }), 500

# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)