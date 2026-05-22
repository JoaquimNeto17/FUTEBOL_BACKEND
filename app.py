# app.py

import os
import json
import random
from flask import Flask, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv

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
# HISTÓRICO DE TIMES GERADOS (em memória, reseta ao reiniciar)
# =========================================================

historico_times = []       # ex: ["Valencia", "Vasco da Gama", ...]
historico_paises = []      # ex: ["Espanha", "Brasil", ...]
MAX_HISTORICO = 20         # quantos guardar antes de começar a limpar

# =========================================================
# LISTA DE SEEDS ALEATÓRIOS PARA FORÇAR VARIEDADE
# =========================================================

SEEDS_PERFIL = [
    "gigante em crise financeira grave",
    "clube pequeno com torcida apaixonada",
    "clube histórico esquecido em divisão inferior",
    "clube recém-promovido sem estrutura",
    "clube feminino em crescimento",
    "clube formador de talentos sem dinheiro",
    "clube com elenco envelhecido precisando de renovação",
    "clube jovem querendo vencer seu primeiro título nacional",
    "clube com seca de mais de 20 anos sem título",
    "clube de cidade pequena que quer chegar à elite",
    "clube emergente de liga asiática ou americana",
    "clube com dívida enorme tentando sobreviver",
    "clube com rivalidade histórica não resolvida",
    "clube que perdeu todos os seus craques e precisa reconstruir",
]

SEEDS_RESTRICAO = [
    "usando apenas jogadores da própria base nas 2 primeiras temporadas",
    "sem contratar jogadores com mais de 27 anos",
    "com limite de orçamento de transferências muito baixo",
    "contratando apenas jogadores nacionais por 3 temporadas",
    "sem vender nenhum jogador da base nas primeiras 2 temporadas",
    "priorizando um estilo de jogo específico (ex: posse de bola, contra-ataque, pressão alta)",
    "sem usar o mercado de transferências na primeira temporada",
    "montando um elenco com média de idade máxima de 24 anos",
]

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
    texto_lower = texto.lower()
    for palavra in PALAVRAS_PROIBIDAS:
        if palavra in texto_lower:
            return True
    return False

# =========================================================
# GERAÇÃO DO DESAFIO
# =========================================================

def generate_career_challenge():
    global historico_times, historico_paises

    # --- Monta instrução de exclusão dinâmica ---
    exclusao_times = ""
    if historico_times:
        lista_excluir = ", ".join(historico_times[-10:])  # últimos 10 times
        exclusao_times = (
            f"\n\nATENÇÃO: Os seguintes clubes já foram usados recentemente. "
            f"É PROIBIDO usá-los agora: {lista_excluir}."
        )

    exclusao_paises = ""
    if historico_paises:
        # pega os 3 países mais repetidos recentemente
        ultimos_paises = historico_paises[-6:]
        exclusao_paises = (
            f" Também evite clubes dos seguintes países usados recentemente: "
            f"{', '.join(set(ultimos_paises))}."
        )

    # --- Escolhe um seed aleatório para forçar criatividade ---
    seed_perfil = random.choice(SEEDS_PERFIL)
    seed_restricao = random.choice(SEEDS_RESTRICAO)

    conteudo_prompt = (
        f"Gere agora um desafio de Modo Carreira para um clube com este perfil: '{seed_perfil}'. "
        f"O desafio deve incluir a seguinte restrição especial: '{seed_restricao}'. "
        f"Escolha um clube DIFERENTE e SURPREENDENTE que se encaixe nesse perfil."
        f"{exclusao_times}{exclusao_paises}"
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",   # modelo corrigido
        contents=conteudo_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=MODO_CARREIRA_SCHEMA,
            temperature=1.2,             # mais alto = mais aleatório
            max_output_tokens=600,
        )
    )

    resultado_texto = response.text

    # --- Extrai o clube gerado e salva no histórico ---
    try:
        dados = json.loads(resultado_texto)
        clube = dados.get("clube_escolhido", "")
        liga = dados.get("liga_do_clube", "")

        if clube:
            historico_times.append(clube)
            if len(historico_times) > MAX_HISTORICO:
                historico_times.pop(0)

        # Tenta deduzir o país a partir da liga (heurística simples)
        pais_deduzido = deduzir_pais(liga)
        if pais_deduzido:
            historico_paises.append(pais_deduzido)
            if len(historico_paises) > MAX_HISTORICO:
                historico_paises.pop(0)

    except (json.JSONDecodeError, AttributeError):
        pass  # se der erro aqui, o erro real é tratado na rota

    return resultado_texto


def deduzir_pais(liga: str) -> str:
    """Heurística simples: mapeia palavras-chave da liga para países."""
    liga_lower = liga.lower()
    mapeamento = {
        "premier": "Inglaterra",
        "championship": "Inglaterra",
        "laliga": "Espanha",
        "bundesliga": "Alemanha",
        "ligue": "França",
        "serie a": "Itália",
        "mls": "EUA",
        "brasileirao": "Brasil",
        "brasileirão": "Brasil",
        "liga portugal": "Portugal",
        "eredivisie": "Holanda",
        "pro league": "Bélgica",
        "liga profesional": "Argentina",
        "saudi": "Arábia Saudita",
        "k league": "Coreia",
        "chinese": "China",
        "a-league": "Austrália",
        "liga 1": "Peru",
        "ekstraklasa": "Polônia",
        "allsvenskan": "Suécia",
        "eliteserien": "Noruega",
        "scottish": "Escócia",
        "airtricity": "Irlanda",
    }
    for chave, pais in mapeamento.items():
        if chave in liga_lower:
            return pais
    return ""


# =========================================================
# ROTAS
# =========================================================

@app.route("/")
def root():
    return jsonify({
        "status": "success",
        "message": "API Gerador de Modo Carreira funcionando!",
        "version": "2.0"
    }), 200


@app.route("/generate", methods=["GET"])
def generate():
    try:
        desafio_json_string = generate_career_challenge()

        if contem_conteudo_proibido(desafio_json_string):
            return jsonify({
                "status": "error",
                "message": "A resposta gerada foi bloqueada por conter termos sensíveis."
            }), 400

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


@app.route("/historico", methods=["GET"])
def historico():
    """Rota de debug: mostra os times e países usados recentemente."""
    return jsonify({
        "status": "success",
        "times_recentes": historico_times,
        "paises_recentes": historico_paises
    }), 200


# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)