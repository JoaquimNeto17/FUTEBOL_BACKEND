# app.py - VERSÃO COM VALIDAÇÃO DAS LIGAS

import os
import json
from collections import deque
from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv

from config import (
    MODO_CARREIRA_SCHEMA, 
    SYSTEM_INSTRUCTION, 
    LIGAS_PERMITIDAS,
    COMPETICOES_CONTINENTAIS,
    CLUBES_POPULARES_DEMais
)

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("A variável GEMINI_API_KEY não foi encontrada no .env")

client = genai.Client(api_key=GEMINI_API_KEY)

app = Flask(__name__)
CORS(app)

# =========================================================
# SISTEMA ANTI-REPETIÇÃO
# =========================================================

historico_clubes = deque(maxlen=20)
historico_ligas = deque(maxlen=15)
historico_paises = deque(maxlen=10)

# Mapeamento de países por liga
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
    "Major League Soccer (MLS)": "EUA/Canadá",
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

def registrar_desafio(clube, liga):
    """Registra o desafio no histórico"""
    if clube:
        historico_clubes.append(clube.lower())
    if liga:
        historico_ligas.append(liga.lower())
        pais = PAIS_POR_LIGA.get(liga, "Desconhecido")
        historico_paises.append(pais)

def validar_liga(liga):
    """Valida se a liga está na lista de permitidas"""
    if not liga:
        return False
    
    liga_normalizada = liga.strip()
    
    # Verificação exata
    if liga_normalizada in LIGAS_PERMITIDAS:
        return True
    
    # Verificação case-insensitive
    for liga_permitida in LIGAS_PERMITIDAS:
        if liga_normalizada.lower() == liga_permitida.lower():
            return True
    
    return False

def gerar_prompt_com_restricoes():
    """Gera prompt com restrições baseadas no histórico"""
    
    prompt = """Crie um desafio de Modo Carreira para futebol.

REGRAS IMPORTANTES:

1. Use APENAS estas ligas (escolha UMA):
   - Premier League, EFL Championship, EFL League One, EFL League Two
   - Barclays Women's Super League
   - LALIGA EA SPORTS, Liga F Moeve
   - Bundesliga, Google Pixel Frauen-Bundesliga, 3. Liga
   - Ligue 1 McDonald's, Arkema Première Ligue
   - Serie A Enilive
   - Major League Soccer (MLS), National Women's Soccer League (NWSL)
   - Liga Portugal, Belgium Pro League, Eredivisie
   - Liga Profesional de Fútbol (Argentina)
   - Roshn Saudi League, K League, Chinese Super League, A-League
   - Liga 1, Ekstraklasa, Austrian Bundesliga
   - Brack Super League, Superliga, Scottish Premiership
   - SSE Airtricity League Premier Division, Allsvenskan, Eliteserien

2. NÃO repita clubes recentemente usados.
3. Varie entre países e níveis diferentes.
4. Inclua ligas femininas ocasionalmente.
"""
    
    # Adiciona histórico para evitar repetição
    if historico_clubes:
        prompt += f"\n🚫 CLUBES JÁ USADOS RECENTEMENTE (NÃO REPETIR):\n"
        for clube in list(historico_clubes)[-5:]:
            prompt += f"   - {clube}\n"
    
    if historico_paises:
        prompt += f"\n🌍 PAÍSES JÁ USADOS RECENTEMENTE:\n"
        for pais in list(historico_paises)[-3:]:
            prompt += f"   - {pais}\n"
        prompt += "Prefira um país diferente destes!\n"
    
    prompt += """
   
Crie um desafio com:
- Título criativo
- Contexto histórico imersivo
- 4 objetivos específicos
- Sugestão de contratação

Retorne APENAS JSON."""
    
    return prompt

# =========================================================
# MODERAÇÃO
# =========================================================

PALAVRAS_PROIBIDAS = [
    "matar", "assassinar", "bomba", "terrorismo", "violencia",
    "racismo", "nazismo", "preconceito", "homofobia",
    "sexo", "porno", "estupro", "pedofilia",
    "droga", "suicidio", "hackear", "crime"
]

def contem_conteudo_proibido(texto):
    texto = texto.lower()
    return any(palavra in texto for palavra in PALAVRAS_PROIBIDAS)

# =========================================================
# GERAÇÃO DO DESAFIO
# =========================================================

def generate_career_challenge():
    """Gera desafio com validação de ligas"""
    
    prompt = gerar_prompt_com_restricoes()
    
    max_tentativas = 3
    for tentativa in range(max_tentativas):
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    response_schema=MODO_CARREIRA_SCHEMA,
                    max_output_tokens=900,
                    temperature=1.3 + (tentativa * 0.1),  # Aumenta criatividade nas tentativas
                    top_p=0.95,
                    top_k=40,
                    candidate_count=1
                )
            )
            
            desafio = json.loads(response.text)
            clube = desafio.get("clube_escolhido", "")
            liga = desafio.get("liga_do_clube", "")
            
            # VALIDAÇÃO CRÍTICA: Verifica se a liga é permitida
            if not validar_liga(liga):
                print(f"⚠️ Tentativa {tentativa + 1}: Liga inválida '{liga}'. Regenerando...")
                # Força o prompt a ser mais específico
                prompt = f"""⚠️ IMPORTANTE: A liga anterior '{liga}' NÃO é permitida!

Você DEVE usar APENAS uma destas ligas:
{chr(10).join(f'- {l}' for l in LIGAS_PERMITIDAS[:20])}

Crie um desafio com uma liga válida desta lista.
NÃO invente ligas novas.

{prompt}"""
                continue
            
            # Verifica repetição de clube
            if clube.lower() in historico_clubes:
                print(f"⚠️ Tentativa {tentativa + 1}: Clube '{clube}' repetido. Regenerando...")
                prompt = f"CRIE UM DESAFIO COMPLETAMENTE DIFERENTE. NÃO use o clube '{clube}'. {prompt}"
                continue
            
            # Registra e retorna
            registrar_desafio(clube, liga)
            return desafio
            
        except Exception as e:
            print(f"Erro na tentativa {tentativa + 1}: {e}")
            if tentativa == max_tentativas - 1:
                raise
    
    raise Exception("Não foi possível gerar um desafio válido após múltiplas tentativas")

# =========================================================
# ROTAS
# =========================================================

@app.route("/")
def root():
    return jsonify({
        "status": "success",
        "message": "API Gerador de Modo Carreira",
        "version": "3.1",
        "stats": {
            "total_ligas": len(LIGAS_PERMITIDAS),
            "total_competicoes": len(COMPETICOES_CONTINENTAIS),
            "paises_disponiveis": len(set(PAIS_POR_LIGA.values()))
        }
    }), 200

@app.route("/generate", methods=["GET"])
def generate():
    try:
        desafio = generate_career_challenge()
        
        # Moderação final
        if contem_conteudo_proibido(json.dumps(desafio)):
            return jsonify({
                "status": "error",
                "message": "Conteúdo bloqueado pela moderação"
            }), 400
        
        return jsonify({
            "status": "success",
            "stats": {
                "desafios_gerados": len(historico_clubes),
                "ultimos_clubes": list(historico_clubes),
                "ultimas_ligas": list(historico_ligas),
                "validacao_liga_ativa": True
            },
            "dados_desafio": desafio
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/ligas", methods=["GET"])
def listar_ligas():
    """Lista todas as ligas permitidas"""
    return jsonify({
        "total_ligas": len(LIGAS_PERMITIDAS),
        "ligas": LIGAS_PERMITIDAS,
        "competicoes_continentais": COMPETICOES_CONTINENTAIS
    }), 200

@app.route("/stats", methods=["GET"])
def stats():
    """Estatísticas detalhadas"""
    return jsonify({
        "historico_clubes": list(historico_clubes),
        "historico_ligas": list(historico_ligas),
        "historico_paises": list(historico_paises),
        "total_gerados": len(historico_clubes),
        "ligas_permitidas_count": len(LIGAS_PERMITIDAS)
    }), 200

@app.route("/reset", methods=["POST"])
def reset():
    """Reseta histórico"""
    historico_clubes.clear()
    historico_ligas.clear()
    historico_paises.clear()
    return jsonify({
        "status": "success",
        "message": "Histórico resetado com sucesso!"
    }), 200

# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🎮 GERADOR DE MODO CARREIRA v3.1")
    print("=" * 60)
    print(f"✅ {len(LIGAS_PERMITIDAS)} ligas permitidas configuradas")
    print(f"✅ {len(COMPETICOES_CONTINENTAIS)} competições continentais")
    print(f"✅ Sistema anti-repetição ativo")
    print("=" * 60)
    print("📋 LIGAS CARREGADAS:")
    for i, liga in enumerate(LIGAS_PERMITIDAS[:10], 1):
        print(f"   {i}. {liga}")
    print(f"   ... e mais {len(LIGAS_PERMITIDAS) - 10} ligas")
    print("=" * 60)
    print("🌐 Servidor: http://localhost:5000")
    print("📊 Estatísticas: http://localhost:5000/stats")
    print("📋 Listar ligas: http://localhost:5000/ligas")
    print("🎲 Gerar desafio: http://localhost:5000/generate")
    print("=" * 60)
    app.run(debug=True)