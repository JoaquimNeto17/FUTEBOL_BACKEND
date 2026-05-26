# config.py - VERSÃO OTIMIZADA v5.0

# =========================================================
# SCHEMA DO DESAFIO
# =========================================================

MODO_CARREIRA_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "clube_escolhido": {
            "type": "STRING",
            "description": "Nome do clube de futebol para este desafio (deve ser real e existir na liga escolhida)"
        },
        "liga_do_clube": {
            "type": "STRING", 
            "description": "Liga ou campeonato nacional onde o clube joga"
        },
        "titulo_do_desafio": {
            "type": "STRING",
            "description": "Título marcante e criativo para o desafio (máximo 60 caracteres)"
        },
        "contexto_historico": {
            "type": "STRING",
            "description": "Introdução imersiva de 3 a 5 linhas explicando o contexto do desafio"
        },
        "objetivos_da_diretoria": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "Lista com 3 a 4 metas realistas e desafiadoras",
            "minItems": 3,
            "maxItems": 4
        },
        "jogadores_recomendados": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "nome": {
                        "type": "STRING",
                        "description": "Nome completo do jogador real"
                    },
                    "posicao": {
                        "type": "STRING", 
                        "description": "Posição principal (ZAG, LD, LE, VOL, MC, MCO, MD, ME, PD, PE, PL, ATA)"
                    },
                    "clube_atual": {
                        "type": "STRING",
                        "description": "Clube onde joga atualmente (real)"
                    },
                    "idade": {
                        "type": "INTEGER",
                        "description": "Idade do jogador (16-40)"
                    },
                    "justificativa": {
                        "type": "STRING",
                        "description": "Por que ele se encaixa no sistema tático do clube"
                    }
                },
                "required": ["nome", "posicao", "clube_atual", "idade", "justificativa"]
            },
            "description": "Lista com 3 a 5 jogadores REAIS que se encaixam no perfil do clube",
            "minItems": 3,
            "maxItems": 5
        }
    },
    "required": [
        "clube_escolhido",
        "liga_do_clube", 
        "titulo_do_desafio",
        "contexto_historico",
        "objetivos_da_diretoria",
        "jogadores_recomendados"
    ]
}

# =========================================================
# LIGAS PERMITIDAS
# =========================================================

LIGAS_PERMITIDAS = [
    # Inglaterra
    "Premier League",
    "EFL Championship", 
    "EFL League One",
    "EFL League Two",
    "Barclays Women's Super League",
    
    # Espanha
    "LALIGA EA SPORTS",
    "Liga F Moeve",
    
    # Alemanha
    "Bundesliga",
    "Google Pixel Frauen-Bundesliga",
    "3. Liga",
    
    # França
    "Ligue 1 McDonald's",
    "Arkema Première Ligue",
    
    # Itália
    "Serie A Enilive",
    
    # EUA/Canadá
    "Major League Soccer (MLS)",
    "National Women's Soccer League (NWSL)",
    
    # Portugal
    "Liga Portugal",
    
    # Bélgica
    "Belgium Pro League",
    
    # Holanda
    "Eredivisie",
    
    # Argentina
    "Liga Profesional de Fútbol (Argentina)",
    
    # Arábia Saudita
    "Roshn Saudi League",
    
    # Coreia do Sul
    "K League",
    
    # China
    "Chinese Super League",
    
    # Austrália
    "A-League",
    
    # Indonésia
    "Liga 1",
    
    # Polônia
    "Ekstraklasa",
    
    # Áustria
    "Austrian Bundesliga",
    
    # Suíça
    "Brack Super League",
    
    # Dinamarca
    "Superliga",
    
    # Escócia
    "Scottish Premiership",
    
    # Irlanda
    "SSE Airtricity League Premier Division",
    
    # Suécia
    "Allsvenskan",
    
    # Noruega
    "Eliteserien"
]

# =========================================================
# COMPETIÇÕES CONTINENTAIS
# =========================================================

COMPETICOES_CONTINENTAIS = [
    "UEFA Champions League",
    "UEFA Europa League",
    "UEFA Europa Conference League",
    "UEFA Super Cup",
    "UEFA Women's Champions League",
    "CONMEBOL Libertadores",
    "CONMEBOL Sudamericana",
    "CONMEBOL Recopa",
    "FIFA Club World Cup",
    "FIFA Intercontinental Cup"
]

# =========================================================
# INSTRUÇÃO DO SISTEMA PARA IA (OTIMIZADA)
# =========================================================

SYSTEM_INSTRUCTION = f"""Você é um especialista em scout e gestão de futebol, criando desafios de Modo Carreira para EA FC 26.

========================================
LIGAS PERMITIDAS (USE SOMENTE ESTAS)
========================================

{chr(10).join(f'• {liga}' for liga in LIGAS_PERMITIDAS[:30])}

========================================
REGRAS OBRIGATÓRIAS
========================================

1. **JOGADORES REAIS APENAS**
   - NUNCA invente jogadores
   - Use nomes reais, clubes reais, idades reais
   - Pesquise mentalmente seu banco de dados de futebol

2. **CONTEXTO DO CLUBE**
   - Times pequenos → jovens promessas ou veteranos
   - Times médios → jogadores de ligas secundárias
   - Times grandes → estrelas consolidadas
   - Respeite o orçamento implícito da liga

3. **VARIEDADE DE PERFIS**
   - Jovens (18-22 anos) - potencial de revenda
   - Auge (23-28 anos) - performance imediata
   - Veteranos (29+ anos) - liderança e experiência

4. **POSIÇÕES E ESTILOS**
   - Defesa: solidez, antecipação, força física
   - Meio-campo: criatividade, passe, visão de jogo
   - Ataque: velocidade, finalização, 1x1

5. **OBJETIVOS REALISTAS**
   - Baseados na realidade do clube
   - Misture curto, médio e longo prazo
   - Inclua metas de desenvolvimento de jovens

========================================
FORMATO DE RESPOSTA
========================================

Retorne APENAS JSON válido, sem markdown, sem texto extra.
Use português do Brasil para todos os textos.

SEJA CRIATIVO, IMPREVISÍVEL E REALISTA!"""

# =========================================================
# CONFIGURAÇÕES ADICIONAIS
# =========================================================

# Limites de rate limiting (opcional)
RATE_LIMIT = {
    "requests_per_minute": 10,
    "requests_per_day": 1000
}

# Timeout em segundos
REQUEST_TIMEOUT = 30