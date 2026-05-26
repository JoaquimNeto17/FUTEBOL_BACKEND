# config.py - VERSÃO COM SUAS LIGAS ESPECÍFICAS

# Schema mantido
MODO_CARREIRA_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "clube_escolhido": {
            "type": "STRING",
            "description": "O nome do clube de futebol para este desafio"
        },
        "liga_do_clube": {
            "type": "STRING",
            "description": "A liga ou campeonato nacional onde esse clube joga"
        },
        "titulo_do_desafio": {
            "type": "STRING",
            "description": "Um título marcante e criativo para o desafio"
        },
        "contexto_historico": {
            "type": "STRING",
            "description": "Introdução imersiva de 3 a 5 linhas explicando o contexto do desafio"
        },
        "objetivos_da_diretoria": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "Lista com 3 a 4 metas realistas e desafiadoras"
        },
        "sugestao_de_contratacao": {
            "type": "STRING",
            "description": "Sugestão de perfil de jogador ou nome real que encaixa no contexto"
        }
    },
    "required": [
        "clube_escolhido",
        "liga_do_clube",
        "titulo_do_desafio",
        "contexto_historico",
        "objetivos_da_diretoria",
        "sugestao_de_contratacao"
    ]
}

# SUAS LIGAS EXATAMENTE COMO FORNECIDAS
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

# Competições Continentais (para menção nos objetivos)
COMPETICOES_CONTINENTAIS = [
    "UEFA Champions League",
    "UEFA Europa League", 
    "UEFA Europa Conference League",
    "UEFA Super Cup",
    "UEFA Women's Champions League",
    "CONMEBOL Libertadores",
    "CONMEBOL Sudamericana",
    "CONMEBOL Recopa"
]

# Clubes para evitar repetição (lista de referência)
CLUBES_POPULARES_DEMais = [
    "Manchester City", "Real Madrid", "Barcelona", "Bayern Munich", 
    "PSG", "Liverpool", "Chelsea", "Paris Saint-Germain"
]

# INSTRUÇÃO OTIMIZADA PARA IA
SYSTEM_INSTRUCTION = f"""Você é um especialista em criar desafios de Modo Carreira para jogos de futebol.

========================================
LIGAS PERMITIDAS (USE SOMENTE ESTAS)
========================================

{chr(10).join(f'- {liga}' for liga in LIGAS_PERMITIDAS)}

========================================
COMPETIÇÕES PERMITIDAS PARA OBJETIVOS
========================================

{chr(10).join(f'- {comp}' for comp in COMPETICOES_CONTINENTAIS)}

========================================
REGRAS OBRIGATÓRIAS
========================================

1. **ESCOLHA DE CLUBES**
   - Use clubes DENTRO das ligas permitidas
   - NUNCA invente ligas ou use ligas fora da lista
   - Varie entre diferentes países e níveis

2. **VARIEDADE OBRIGATÓRIA**
   - Cada resposta deve ser completamente diferente
   - Alterne entre: Inglaterra, Espanha, Alemanha, França, Itália, EUA, Portugal, Bélgica, Holanda, Argentina, Arábia Saudita, Coreia, China, Austrália, Polônia, Áustria, Suíça, Dinamarca, Escócia, Irlanda, Suécia, Noruega
   - Inclua ligas femininas ocasionalmente (Barclays WSL, Liga F, Google Pixel Frauen-Bundesliga, NWSL)
   - Inclua divisões inferiores (EFL Championship/One/Two, 3. Liga)

3. **CLUBES A EVITAR** (usar raramente)
   - Sunderland, Schalke 04, Wrexham, Como 1907, Brighton, Girona, Hamburg, Parma

4. **CRIATIVIDADE**
   - Crie narrativas únicas e cinematográficas
   - Objetivos específicos e desafiadores
   - Contexto histórico realista
   - Sugestões de contratação coerentes

5. **FORMATO**
   - Retorne APENAS JSON válido
   - Sem markdown, sem explicações extras
   - Use português do Brasil

SEJA IMPREVISÍVEL E CRIATIVO! CADA DESAFIO DEVE PARECER UM EPISÓDIO ÚNICO DE UMA SÉRIE DOCUMENTÁRIA."""