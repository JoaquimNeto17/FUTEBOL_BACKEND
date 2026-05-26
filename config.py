# config.py - VERSÃO COM IA GERANDO JOGADORES REAIS

# Schema com lista de jogadores
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
        "jogadores_recomendados": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "nome": {"type": "STRING", "description": "Nome do jogador real que se encaixa no perfil tático e contexto do clube"},
                    "posicao": {"type": "STRING", "description": "Posição principal (ex: ZAG, LD, LE, VOL, MC, MCO, PD, PE, PL)"},
                    "clube_atual": {"type": "STRING", "description": "Clube onde joga atualmente (real)"},
                    "idade": {"type": "INTEGER", "description": "Idade do jogador"},
                    "justificativa": {"type": "STRING", "description": "Por que ele se encaixa no sistema tático e no projeto do clube"}
                },
                "required": ["nome", "posicao", "clube_atual", "idade", "justificativa"]
            },
            "description": "Lista com 3 a 5 jogadores REAIS que se encaixam no perfil tático e necessidades do clube",
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

# LIGAS PERMITIDAS
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

# Competições Continentais
COMPETICOES_CONTINENTAIS = [
    "UEFA Champions League",
    "UEFA Europa League", 
    "UEFA Europa Conference League",
    "UEFA Super Cup",
    "UEFA Women's Champions League",
    "CONMEBOL Libertadores",
    "CONMEBOL Sudamericana",
    "CONMEBOL Recopa",
    "FIFA Club World Cup"
]

# INSTRUÇÃO COMPLETA PARA A IA
SYSTEM_INSTRUCTION = f"""Você é um especialista em scout e gestão de futebol, criando desafios de Modo Carreira para EA FC 26.

========================================
LIGAS PERMITIDAS (USE SOMENTE ESTAS)
========================================

{chr(10).join(f'- {liga}' for liga in LIGAS_PERMITIDAS)}

========================================
COMPETIÇÕES PARA OBJETIVOS
========================================

{chr(10).join(f'- {comp}' for comp in COMPETICOES_CONTINENTAIS)}

========================================
REGRAS OBRIGATÓRIAS - JOGADORES
========================================

Ao recomendar jogadores, você DEVE:

1. **USAR JOGADORES REAIS**
   - Nomes reais de jogadores profissionais
   - Clubes atuais corretos
   - Idades precisas
   - NUNCA inventar jogadores

2. **ANALISAR O CONTEXTO DO CLUBE**
   - Se o clube precisa de defesa → recomende zagueiros/laterais
   - Se precisa de criatividade → meias armadores
   - Se precisa de gols → atacantes finalizadores
   - Se é time pequeno → jovens promissores ou veteranos experientes
   - Se é time grande → estrelas consolidadas

3. **JUSTIFICAR CADA CONTRATAÇÃO**
   - Como o jogador se encaixa no sistema tático
   - Que lacuna ele preenche no elenco
   - Potencial de revenda (se for jovem)
   - Experiência (se for veterano)

4. **VARIEDADE DE PERFIS**
   - Misture jovens promissores (19-22 anos)
   - Jogadores no auge (23-28 anos)
   - Veteranos experientes (29+ anos) quando fizer sentido
   - Diferentes nacionalidades e estilos de jogo

5. **MERCADO COMPATÍVEL**
   - Jogadores que o clube poderia realisticamente contratar
   - Considere orçamento do clube (implícito pela liga)
   - Evite jogadores "impossíveis" para times pequenos

========================================
EXEMPLO DE JOGADORES REAIS POR PERFIL
========================================

DEFESA SÓLIDA:
- Gonçalo Inácio (ZAG, 22, Sporting CP) - saída de bola e juventude
- Giorgio Scalvini (ZAG, 20, Atalanta) - força física e projeção
- Micky van de Ven (ZAG, 22, Tottenham) - velocidade e recuperação

MEIO-CAMPO CRIATIVO:
- Florian Wirtz (MCO, 21, Bayer Leverkusen) - visão de jogo e drible
- Xavi Simons (MCO, 21, RB Leipzig) - versatilidade ofensiva
- João Neves (MC, 19, Benfica) - passe e inteligência tática

ATAQUE VELOZ:
- Nico Williams (PE, 21, Athletic Bilbao) - velocidade e 1x1
- Rasmus Højlund (PL, 21, Manchester United) - força e finalização
- Mathys Tel (PL, 18, Bayern Munich) - mobilidade e faro de gol

LATERAL OFENSIVO:
- Jeremie Frimpong (LD, 23, Bayer Leverkusen) - profundidade e cruzamento
- Álex Balde (LE, 20, Barcelona) - ultrapassagem constante

========================================
OUTRAS REGRAS OBRIGATÓRIAS
========================================

1. **CLUBES**
   - Use clubes DENTRO das ligas permitidas
   - Varie entre países e níveis
   - Inclua ligas femininas ocasionalmente
   - Inclua divisões inferiores

2. **CRIATIVIDADE NAS NARRATIVAS**
   - Cada desafio deve ser único e cinematográfico
   - Contexto histórico realista e imersivo
   - Objetivos específicos e desafiadores

3. **FORMATO**
   - Retorne APENAS JSON válido
   - Sem markdown, sem explicações extras
   - Use português do Brasil

**IMPORTANTE**: Você é um DIRETOR TÉCNICO experiente. Cada jogador recomendado deve fazer sentido TÁTICO para o clube escolhido. Pense no estilo de jogo, nas carências do elenco e no orçamento disponível.

SEJA IMPREVISÍVEL, CRIATIVO E REALISTA! CADA DESAFIO É UM EPISÓDIO ÚNICO DE UMA SÉRIE DOCUMENTÁRIA SOBRE GESTÃO DE FUTEBOL."""