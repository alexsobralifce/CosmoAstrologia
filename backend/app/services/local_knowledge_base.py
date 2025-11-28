"""
Base local de conhecimento astrológico para uso quando o índice RAG completo
não estiver disponível. As descrições aqui servem como contexto para gerar
interpretações rápidas de planetas em signos, casas e aspectos.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


PLANET_ALIASES = {
    "sol": "Sol",
    "sun": "Sol",
    "lua": "Lua",
    "moon": "Lua",
    "mercurio": "Mercúrio",
    "mercury": "Mercúrio",
    "venus": "Vênus",
    "marte": "Marte",
    "mars": "Marte",
    "jupiter": "Júpiter",
    "saturno": "Saturno",
    "saturn": "Saturno",
    "urano": "Urano",
    "uranus": "Urano",
    "netuno": "Netuno",
    "neptune": "Netuno",
    "plutao": "Plutão",
    "pluto": "Plutão",
}


SIGN_ALIASES = {
    "aries": "Áries",
    "touro": "Touro",
    "geminis": "Gêmeos",
    "gemeos": "Gêmeos",
    "cancer": "Câncer",
    "leao": "Leão",
    "virgem": "Virgem",
    "libra": "Libra",
    "escorpiao": "Escorpião",
    "sagitario": "Sagitário",
    "capricornio": "Capricórnio",
    "aquario": "Aquário",
    "peixes": "Peixes",
}


PLANET_ARCHETYPES: Dict[str, Dict[str, str]] = {
    "Sol": {
        "essence": "O Sol expressa a identidade, a vitalidade e a consciência criativa. Indica onde buscamos reconhecimento e de que maneira iluminamos o mundo.",
        "focus": "Fala sobre propósito pessoal, liderança e confiança para nos colocarmos no centro da própria história.",
        "gift": "Coragem para brilhar, clareza de objetivos e força de vontade.",
        "shadow": "Orgulho excessivo ou necessidade de aprovação constante.",
    },
    "Lua": {
        "essence": "A Lua traduz necessidades emocionais, memória afetiva e instintos de proteção.",
        "focus": "Mostra como nutrimos a nós mesmos e aos outros, além do ritmo emocional diário.",
        "gift": "Empatia, sensibilidade e conexão com o passado.",
        "shadow": "Humor instável ou apego a padrões confortáveis.",
    },
    "Mercúrio": {
        "essence": "Mercúrio rege pensamento, comunicação e aprendizado.",
        "focus": "Indica como processamos informações, articulamos ideias e negociamos.",
        "gift": "Versatilidade mental, curiosidade e habilidade diplomática.",
        "shadow": "Dispersão ou racionalização excessiva dos sentimentos.",
    },
    "Vênus": {
        "essence": "Vênus fala sobre prazer, estética, valores e relacionamentos.",
        "focus": "Mostra o que apreciamos, como cultivamos harmonia e o estilo de vínculo afetivo.",
        "gift": "Carisma, senso artístico e capacidade de atrair recursos.",
        "shadow": "Complacência ou dependência da aprovação externa.",
    },
    "Marte": {
        "essence": "Marte representa impulso, coragem e atitude.",
        "focus": "Revela como agimos frente a desafios e defendemos nossos desejos.",
        "gift": "Força, iniciativa e autenticidade.",
        "shadow": "Impulsividade, reatividade ou competitividade exagerada.",
    },
    "Júpiter": {
        "essence": "Júpiter é expansão, fé e oportunidades.",
        "focus": "Aponta onde buscamos sentido, prosperidade e crescimento intelectual.",
        "gift": "Otimismo, generosidade e visão estratégica.",
        "shadow": "Excesso de confiança ou promessas maiores do que a execução.",
    },
    "Saturno": {
        "essence": "Saturno simboliza estrutura, responsabilidade e maturidade.",
        "focus": "Mostra lições de disciplina, limites e construção a longo prazo.",
        "gift": "Resiliência, domínio técnico e liderança consciente.",
        "shadow": "Rigidez, medo do fracasso ou pessimismo.",
    },
    "Urano": {
        "essence": "Urano traz inovação, independência e revoluções pessoais.",
        "focus": "Indica onde buscamos liberdade para experimentar novos caminhos.",
        "gift": "Originalidade, visão futurista e coragem para quebrar padrões.",
        "shadow": "Impulsividade, instabilidade ou rebeldia sem causa.",
    },
    "Netuno": {
        "essence": "Netuno fala sobre imaginação, espiritualidade e compaixão.",
        "focus": "Aponta áreas onde buscamos transcendência e conexão com o invisível.",
        "gift": "Intuição, inspiração artística e vocação para servir.",
        "shadow": "Ilusões, escapismo ou falta de limites saudáveis.",
    },
    "Plutão": {
        "essence": "Plutão representa transformação profunda, poder e renascimento.",
        "focus": "Mostra onde enfrentamos crises que nos convidam a regenerar.",
        "gift": "Força psíquica, magnetismo e capacidade de cura.",
        "shadow": "Controle, obsessão ou medo da vulnerabilidade.",
    },
}


SIGN_TRAITS: Dict[str, Dict[str, str]] = {
    "Áries": {
        "element": "Fogo",
        "modality": "Cardinal",
        "keywords": "iniciativa, coragem, franqueza",
        "needs": "agir com liberdade, liderar e testar limites",
        "shadow": "impulsividade e impaciência",
    },
    "Touro": {
        "element": "Terra",
        "modality": "Fixo",
        "keywords": "estabilidade, valores sensoriais, perseverança",
        "needs": "construir segurança e desfrutar do que é tangível",
        "shadow": "teimosia e apego ao conforto",
    },
    "Gêmeos": {
        "element": "Ar",
        "modality": "Mutável",
        "keywords": "curiosidade, diálogo, multiplicidade",
        "needs": "variedade mental e troca constante",
        "shadow": "dispersão e superficialidade",
    },
    "Câncer": {
        "element": "Água",
        "modality": "Cardinal",
        "keywords": "cuidado, memória, proteção",
        "needs": "pertencer emocionalmente e nutrir vínculos",
        "shadow": "hipersensibilidade e retraimento defensivo",
    },
    "Leão": {
        "element": "Fogo",
        "modality": "Fixo",
        "keywords": "criação, generosidade, protagonismo",
        "needs": "ser reconhecido e expressar talento",
        "shadow": "orgulho e drama",
    },
    "Virgem": {
        "element": "Terra",
        "modality": "Mutável",
        "keywords": "análise, serviço, refinamento",
        "needs": "aperfeiçoar processos e ser útil",
        "shadow": "crítica excessiva e ansiedade por controle",
    },
    "Libra": {
        "element": "Ar",
        "modality": "Cardinal",
        "keywords": "diplomacia, estética, justiça",
        "needs": "harmonia social e parcerias equilibradas",
        "shadow": "indecisão ou desejo de agradar a todos",
    },
    "Escorpião": {
        "element": "Água",
        "modality": "Fixo",
        "keywords": "intensidade, mistério, regeneração",
        "needs": "consagrar-se a experiências transformadoras",
        "shadow": "controle emocional e ciúmes",
    },
    "Sagitário": {
        "element": "Fogo",
        "modality": "Mutável",
        "keywords": "expansão, filosofia, aventura",
        "needs": "explorar horizontes e defender ideais",
        "shadow": "exagero e falta de tato",
    },
    "Capricórnio": {
        "element": "Terra",
        "modality": "Cardinal",
        "keywords": "meta, estrutura, responsabilidade",
        "needs": "conquistar autonomia e resultados concretos",
        "shadow": "rigidez e pessimismo",
    },
    "Aquário": {
        "element": "Ar",
        "modality": "Fixo",
        "keywords": "originalidade, coletividade, visão futurista",
        "needs": "inovar modelos e preservar liberdade intelectual",
        "shadow": "distanciamento afetivo e rebeldia",
    },
    "Peixes": {
        "element": "Água",
        "modality": "Mutável",
        "keywords": "sensibilidade, imaginação, entrega",
        "needs": "romper barreiras do ego e servir ao coletivo",
        "shadow": "confusão e escapismo",
    },
}


HOUSE_THEMES: Dict[int, Dict[str, str]] = {
    1: {
        "focus": "identidade, estilo pessoal e iniciativa", 
        "question": "Como eu me apresento e inicio novos ciclos?",
        "category": "angular",
        "description": "Casa Angular - Ação e pilares da vida. Identidade, corpo físico, primeira impressão, máscara social (Ascendente)."
    },
    2: {
        "focus": "valores, finanças e autoestima", 
        "question": "Do que preciso para sentir segurança material?",
        "category": "sucedente",
        "description": "Casa Sucedente - Segurança e recursos. Valores pessoais, recursos materiais, talentos naturais, possessões."
    },
    3: {
        "focus": "comunicação, estudos e laços fraternos", 
        "question": "Como troco ideias e circulo pelas minhas redes próximas?",
        "category": "cadente",
        "description": "Casa Cadente - Aprendizado e transição. Comunicação, estudos básicos, irmãos, vizinhança, deslocamentos curtos."
    },
    4: {
        "focus": "família, raízes e intimidade emocional", 
        "question": "Onde ancoro minha vida interior?",
        "category": "angular",
        "description": "Casa Angular - Ação e pilares da vida. Família, raízes, lar, vida privada, fundamentos emocionais (IC - Fundo do Céu)."
    },
    5: {
        "focus": "criatividade, romance e expressão lúdica", 
        "question": "De que modo celebro meus talentos e prazeres?",
        "category": "sucedente",
        "description": "Casa Sucedente - Segurança e recursos. Criatividade, romance, filhos, expressão lúdica, jogos, especulação."
    },
    6: {
        "focus": "rotina, saúde e serviço", 
        "question": "Como organizo o cotidiano e cuido do meu corpo?",
        "category": "cadente",
        "description": "Casa Cadente - Aprendizado e transição. Rotina, saúde, trabalho diário, serviço, aperfeiçoamento, animais de estimação."
    },
    7: {
        "focus": "parcerias, contratos e espelhamentos", 
        "question": "Quais qualidades busco nos relacionamentos?",
        "category": "angular",
        "description": "Casa Angular - Ação e pilares da vida. Parcerias, relacionamentos íntimos, casamento, contratos, espelhamentos (Descendente)."
    },
    8: {
        "focus": "transformação, recursos compartilhados e intimidade profunda", 
        "question": "Como lido com entregas e renascimentos?",
        "category": "sucedente",
        "description": "Casa Sucedente - Segurança e recursos. Transformação, recursos compartilhados, intimidade profunda, regeneração, heranças."
    },
    9: {
        "focus": "propósito, estudos superiores e viagens", 
        "question": "Que crenças expandem minha visão de mundo?",
        "category": "cadente",
        "description": "Casa Cadente - Aprendizado e transição. Propósito, estudos superiores, filosofia, viagens longas, crenças, expansão mental."
    },
    10: {
        "focus": "carreira, vocação e reputação", 
        "question": "Como quero ser reconhecido no mundo?",
        "category": "angular",
        "description": "Casa Angular - Ação e pilares da vida. Carreira, vocação, reputação pública, objetivos de vida, autoridade (MC - Meio do Céu)."
    },
    11: {
        "focus": "amizades, coletivos e futuro", 
        "question": "Quais causas desejo apoiar com minha rede?",
        "category": "sucedente",
        "description": "Casa Sucedente - Segurança e recursos. Amizades, coletivos, grupos, ideais, futuro, causas sociais, esperanças."
    },
    12: {
        "focus": "inconsciente, espiritualidade e retiros", 
        "question": "Do que preciso para recarregar e escutar minha intuição?",
        "category": "cadente",
        "description": "Casa Cadente - Aprendizado e transição. Inconsciente, espiritualidade, retiros, karma, limitações, transcendência, segredos."
    },
}


ASPECT_MEANINGS: Dict[str, str] = {
    "conjunção": "Integra energias semelhantes; pode intensificar tanto talentos quanto desafios por falta de distância crítica. Fusão intensa de energias que precisa ser expressa de forma integrada.",
    "oposição": "Pede conciliação entre polos; projeta qualidades no outro para que ocorra equilíbrio consciente. Polaridade e necessidade de equilíbrio entre extremos.",
    "quadratura": "Gera tensão criativa; obriga a agir e reorganizar prioridades para evitar estagnação. O aspecto mais desafiador, mas também o mais transformador. Conflitos internos que exigem ação e resolução.",
    "trígono": "Facilita o fluxo; talentos naturais podem ser potencializados com consciência e gratidão. O aspecto mais harmonioso, representando talentos naturais e facilidades.",
    "sextil": "Oferta oportunidades sutis; exige movimento intencional para aproveitar as portas abertas. Oportunidades e cooperação, potencial que pode ser desenvolvido com esforço consciente.",
    "quincúncio": "Ajuste e adaptação. Planetas em signos incompatíveis, exigindo ajustes práticos e mudanças de perspectiva. Aspecto de saúde e bem-estar, indicando áreas que precisam de atenção cuidadosa.",
    "semissextil": "Conexão leve e sutil. Representa pequenas oportunidades e conexões que podem ser desenvolvidas com atenção consciente.",
    "quintil": "Talento criativo. Conexão que facilita expressão artística e criatividade. Revela talentos artísticos, criatividade e expressão única.",
    "sesqui-quadratura": "Tensão residual. Representa ajustes finos necessários após grandes transformações. Energia de refinamento e polimento.",
}


@dataclass
class KnowledgeChunk:
    text: str
    source: str = "Base Local - Conhecimento Astrológico"
    page: int = 1
    chunk_index: int = 0
    score: float = 1.0

    def as_dict(self) -> Dict[str, any]:
        return {
            "text": self.text,
            "source": self.source,
            "page": self.page,
            "chunk_index": self.chunk_index,
            "score": self.score,
        }


class LocalKnowledgeBase:
    """Fornece textos curtos de referência quando o índice vetorial não está disponível."""

    def __init__(self) -> None:
        self.planets = PLANET_ARCHETYPES
        self.signs = SIGN_TRAITS
        self.houses = HOUSE_THEMES
        self.aspects = ASPECT_MEANINGS

    def normalize_planet(self, name: Optional[str]) -> Optional[str]:
        if not name:
            return None
        key = name.strip().lower()
        return PLANET_ALIASES.get(key, name.strip().title())

    def normalize_sign(self, name: Optional[str]) -> Optional[str]:
        if not name:
            return None
        key = name.strip().lower()
        return SIGN_ALIASES.get(key, name.strip().title())

    def _planet_section(self, planet: str) -> Optional[str]:
        data = self.planets.get(planet)
        if not data:
            return None
        return (
            f"{planet}: {data['essence']} {data['focus']} "
            f"Pontos fortes: {data['gift']}. Alcance doado quando trabalhamos as sombras: {data['shadow']}."
        )

    def _sign_section(self, sign: str) -> Optional[str]:
        data = self.signs.get(sign)
        if not data:
            return None
        return (
            f"{sign} ({data['element']} • {data['modality']}): palavras-chave {data['keywords']}. "
            f"Busca essencial: {data['needs']}. Atenção para {data['shadow']}."
        )

    def _planet_sign_combo(self, planet: str, sign: str) -> str:
        planet_data = self.planets.get(planet, {})
        sign_data = self.signs.get(sign, {})
        element = sign_data.get("element", "um elemento")
        modality = sign_data.get("modality", "um modo")
        needs = sign_data.get("needs", "necessidades específicas")
        gift = planet_data.get("gift", "potenciais criativos")

        return (
            f"Quando {planet} está em {sign}, a expressão do planeta canaliza o elemento {element} e o dinamismo "
            f"{modality.lower()}. Há foco em {needs}, e os dons naturais ({gift}) ficam mais evidentes quando existe "
            f"consciência sobre {sign_data.get('shadow', 'os excessos do signo')}."
        )

    def _house_section(self, house: int, planet: Optional[str], sign: Optional[str]) -> Optional[str]:
        data = self.houses.get(house)
        if not data:
            return None
        prefix = "Esta casa trata de"
        if planet:
            prefix = f"{planet} nesta casa evidencia"
        
        category_info = ""
        if 'category' in data:
            category_names = {
                'angular': 'Casa Angular (Ação e Pilares da Vida)',
                'sucedente': 'Casa Sucedente (Segurança e Recursos)',
                'cadente': 'Casa Cadente (Aprendizado e Transição)'
            }
            category_info = f" {category_names.get(data['category'], '')}."
        
        description = data.get('description', '')
        if description:
            description = f" {description}"
        
        return (
            f"{prefix} {data['focus']}.{category_info}{description} "
            f"Pergunta-chave: {data['question']} "
            f"{'A energia de ' + sign + ' colore os objetivos' if sign else ''}".strip()
        )

    def _aspect_section(self, aspect: str, planet: Optional[str], sign: Optional[str]) -> Optional[str]:
        aspect_key = aspect.strip().lower() if aspect else None
        if not aspect_key:
            return None
        meaning = self.aspects.get(aspect_key)
        if not meaning:
            return None
        subject = planet or "os planetas envolvidos"
        
        # Adicionar informações sobre tipo de aspecto (harmônico, tenso, neutro)
        aspect_types = {
            'conjunção': 'neutro',
            'oposição': 'tenso',
            'quadratura': 'tenso',
            'trígono': 'harmônico',
            'sextil': 'harmônico',
            'quincúncio': 'ajuste',
            'semissextil': 'neutro',
            'quintil': 'criativo',
            'sesqui-quadratura': 'tenso',
        }
        
        aspect_type = aspect_types.get(aspect_key, '')
        type_info = ""
        if aspect_type == 'harmônico':
            type_info = " Este é um aspecto harmônico que facilita o fluxo natural de energia."
        elif aspect_type == 'tenso':
            type_info = " Este é um aspecto tenso que exige ação e crescimento através de desafios."
        elif aspect_type == 'criativo':
            type_info = " Este é um aspecto criativo que revela talentos artísticos e expressão única."
        elif aspect_type == 'ajuste':
            type_info = " Este aspecto exige ajustes práticos e adaptações."
        
        return f"O aspecto de {aspect.lower()} envolvendo {subject} lembra que {meaning}.{type_info}"

    def _get_element_interpretation(self, query: str) -> Optional[str]:
        """Gera interpretação específica sobre elementos e modalidades."""
        query_lower = query.lower()
        
        # Definir interpretações específicas para cada elemento
        element_interpretations = {
            "fogo": {
                "predominante": "Quando o elemento Fogo é predominante no mapa astral, você possui uma natureza energética, entusiástica e dinâmica. Sua personalidade é marcada pela iniciativa, coragem e desejo de liderar. Você tende a agir de forma espontânea e direta, com grande capacidade de inspirar outros. Seu comportamento é caracterizado pela busca de novos desafios e experiências que permitam expressar sua criatividade e paixão pela vida.",
                "ausente": "A ausência ou baixa presença do elemento Fogo pode indicar dificuldades para tomar iniciativas ou expressar entusiasmo de forma natural. Você pode se beneficiar desenvolvendo mais confiança em suas capacidades e permitindo-se assumir riscos calculados. Busque atividades que despertem sua paixão e energia vital."
            },
            "terra": {
                "predominante": "Com o elemento Terra predominante, você possui uma natureza prática, estável e focada na realidade concreta. Sua personalidade é marcada pela perseverança, senso de responsabilidade e capacidade de construir bases sólidas. Você valoriza a segurança, a tradição e tem facilidade para materializar seus projetos. Seu comportamento reflete prudência e metodismo na abordagem dos desafios da vida.",
                "ausente": "A ausência do elemento Terra pode indicar dificuldades para lidar com questões práticas e materiais do dia a dia. Você pode tender a ser muito idealista ou disperso, tendo dificuldade para concretizar seus planos. É importante desenvolver mais disciplina, organização e atenção aos detalhes práticos da vida."
            },
            "ar": {
                "predominante": "Com o elemento Ar predominante no seu mapa astral, você possui uma natureza mental ágil, comunicativa e sociável. Sua personalidade é caracterizada pela curiosidade intelectual, facilidade de expressão e necessidade de troca de ideias. Você tem uma mente versátil que busca constantemente novos conhecimentos e conexões. Seu comportamento reflete uma abordagem racional e objetiva da vida, priorizando a comunicação e o relacionamento social.",
                "ausente": "A ausência do elemento Ar pode indicar dificuldades na comunicação e no pensamento abstrato. Você pode tender a ser mais emocional ou prático, mas com menor habilidade para verbalizar seus sentimentos ou analisar situações de forma objetiva. Desenvolver habilidades de comunicação e buscar mais interação social pode ser benéfico."
            },
            "água": {
                "predominante": "Quando o elemento Água é predominante, você possui uma natureza emocional profunda, intuitiva e empática. Sua personalidade é marcada pela sensibilidade, capacidade de compreender os sentimentos alheios e forte conexão com o mundo inconsciente. Você tende a ser receptivo, imaginativo e possui uma rica vida interior. Seu comportamento reflete a busca por vínculos emocionais significativos e experiências que nutram sua alma.",
                "ausente": "A ausência do elemento Água pode indicar dificuldades para acessar e expressar emoções de forma saudável. Você pode tender a ser muito racional ou prático, mas com menor capacidade empática ou intuição. É importante desenvolver sua sensibilidade emocional e permitir-se ser mais receptivo aos sentimentos próprios e alheios."
            }
        }
        
        # Identificar qual elemento está sendo consultado (procurar padrões específicos)
        interpretacao_parts = []
        
        # Procurar por padrões específicos de "elemento X predominante"
        import re
        predominante_match = re.search(r'elemento\s+(\w+)\s+predominante', query_lower)
        if predominante_match:
            elemento_pred = predominante_match.group(1)
            if elemento_pred in element_interpretations:
                interpretacao_parts.append(element_interpretations[elemento_pred]["predominante"])
        
        # Procurar por padrões específicos de "elemento X ausente" ou "falta"
        ausente_match = re.search(r'elemento\s+(\w+)\s+(?:ausente|falta)', query_lower)
        if ausente_match:
            elemento_aus = ausente_match.group(1)
            if elemento_aus in element_interpretations:
                interpretacao_parts.append(f"\n\nQuanto à ausência do elemento {elemento_aus.title()}: {element_interpretations[elemento_aus]['ausente']}")
        
        # Adicionar informações sobre modalidades se mencionadas
        if "modalidade" in query_lower:
            modalidade_info = self._get_modality_info()
            if modalidade_info:
                interpretacao_parts.append(f"\n\n{modalidade_info}")
        
        if interpretacao_parts:
            return "\n\n".join(interpretacao_parts)
        
        # Se não encontrou elemento específico, retornar interpretação geral
        if "elemento" in query_lower and "predominante" in query_lower:
            return "O elemento predominante no seu mapa astral influencia significativamente sua personalidade e comportamento. Ele representa a energia principal que guia suas ações e reações no mundo. Compreender essa influência ajuda a reconhecer seus talentos naturais e áreas de maior facilidade na vida."
        
        if "elemento" in query_lower and ("ausente" in query_lower or "falta" in query_lower):
            return "A ausência ou baixa presença de um elemento no mapa astral indica áreas que podem requerer maior atenção e desenvolvimento consciente. Não significa uma deficiência, mas sim uma oportunidade de crescimento através da integração consciente dessas qualidades em sua vida."
        
        return None

    def _get_modality_info(self) -> str:
        """Retorna informações sobre modalidades astrológicas."""
        return """As modalidades astrológicas representam diferentes formas de expressão da energia:

**Cardinal**: Signos de iniciação (Áries, Câncer, Libra, Capricórnio). Pessoas com predominância cardinal são líderes naturais, iniciadoras de projetos e mudanças. Gostam de começar coisas novas e têm facilidade para tomar decisões.

**Fixo**: Signos de estabilização (Touro, Leão, Escorpião, Aquário). Pessoas com predominância fixa são persistentes, determinadas e focadas. Têm grande capacidade de concentração e preferem aprofundar-se em projetos já iniciados.

**Mutável**: Signos de adaptação (Gêmeos, Virgem, Sagitário, Peixes). Pessoas com predominância mutável são flexíveis, adaptáveis e versáteis. Têm facilidade para se ajustar a mudanças e lidar com múltiplas situações simultaneamente."""

    def _get_regent_interpretation(self, query: str) -> Optional[str]:
        """Gera interpretação específica sobre regentes do mapa."""
        query_lower = query.lower()
        
        # Definir interpretações específicas para cada regente
        regent_interpretations = {
            "sol": {
                "core": "Como regente do seu mapa, o Sol representa sua essência vital e sua jornada de autodescobrimento. Você está aqui para brilhar, liderar e expressar sua individualidade única.",
                "practical": "Na vida prática, isso significa que você se realiza quando está no centro das atenções, liderando projetos ou inspirando outros. Sua confiança e criatividade são seus maiores recursos. Busque atividades que permitam expressar sua personalidade autêntica e desenvolver seus talentos únicos."
            },
            "lua": {
                "core": "A Lua como regente do seu mapa indica uma jornada profundamente emocional e intuitiva. Sua missão de vida está conectada ao cuidado, nutrição e criação de vínculos emocionais significativos.",
                "practical": "Você se realiza cuidando de outros, criando ambientes acolhedores ou trabalhando com temas relacionados à família, lar e bem-estar emocional. Sua intuição é um guia poderoso - confie nela. Desenvolva sua capacidade empática e use sua sensibilidade como força."
            },
            "mercúrio": {
                "core": "Mercúrio como regente revela uma jornada centrada na comunicação, aprendizado e troca de ideias. Você está aqui para conectar pessoas, informações e conceitos.",
                "practical": "Sua realização vem através da escrita, ensino, comunicação ou trabalho com informações. Você tem facilidade para aprender rapidamente e adaptar-se a novas situações. Desenvolva suas habilidades comunicativas e use sua versatilidade mental para resolver problemas complexos."
            },
            "vênus": {
                "core": "Com Vênus como regente, sua jornada está centrada na busca pela beleza, harmonia e relacionamentos significativos. Você veio para criar conexões e trazer mais amor ao mundo.",
                "practical": "Você se realiza em atividades relacionadas à arte, beleza, relacionamentos ou diplomacia. Sua capacidade de harmonizar conflitos e criar ambientes belos é um dom natural. Cultive relacionamentos saudáveis e use sua sensibilidade estética para inspirar outros."
            },
            "marte": {
                "core": "Marte como regente indica uma jornada de ação, coragem e pioneirismo. Você está aqui para iniciar, conquistar e abrir novos caminhos.",
                "practical": "Sua energia se manifesta melhor em situações que exigem liderança, competição saudável ou defesa de causas importantes. Você tem a capacidade natural de iniciar projetos e motivar outros. Canalize sua energia de forma construtiva e não tenha medo de assumir riscos calculados."
            },
            "júpiter": {
                "core": "Júpiter como regente revela uma jornada de expansão, sabedoria e busca por significado. Você está aqui para ensinar, inspirar e expandir horizontes.",
                "practical": "Você se realiza através do ensino, viagens, filosofia ou trabalho com culturas diferentes. Sua visão ampla e otimismo natural são recursos valiosos. Busque oportunidades de crescimento pessoal e compartilhe sua sabedoria com outros de forma generosa."
            },
            "saturno": {
                "core": "Saturno como regente indica uma jornada de responsabilidade, estrutura e conquistas duradouras. Você veio para construir algo sólido e deixar um legado.",
                "practical": "Sua realização vem através da disciplina, trabalho árduo e construção de estruturas duradouras. Você tem a capacidade de transformar obstáculos em degraus para o sucesso. Desenvolva paciência e persistência - seus esforços serão recompensados a longo prazo."
            },
            "urano": {
                "core": "Urano como regente revela uma jornada de inovação, originalidade e quebra de padrões. Você está aqui para revolucionar e trazer mudanças necessárias.",
                "practical": "Você se realiza quando pode expressar sua individualidade única e contribuir para mudanças progressivas. Sua mente inovadora e capacidade de ver o futuro são dons especiais. Abrace sua originalidade e não tenha medo de ser diferente."
            },
            "netuno": {
                "core": "Netuno como regente indica uma jornada espiritual e criativa profunda. Você está aqui para inspirar, curar e conectar-se com dimensões mais sutis da existência.",
                "practical": "Sua realização vem através da arte, espiritualidade, cura ou serviço compassivo aos outros. Sua intuição e sensibilidade são extraordinárias. Desenvolva práticas espirituais e use sua imaginação criativa para inspirar e curar."
            },
            "plutão": {
                "core": "Plutão como regente revela uma jornada de transformação profunda e regeneração. Você está aqui para transformar a si mesmo e ajudar outros em processos de mudança.",
                "practical": "Você se realiza em situações que envolvem transformação, cura psicológica ou trabalho com crises. Sua capacidade de ver além das aparências e promover mudanças profundas é um dom raro. Use seu poder de transformação de forma ética e construtiva."
            }
        }
        
        # Detectar qual regente está sendo consultado
        regent_mentioned = None
        for regent_key, interpretations in regent_interpretations.items():
            if regent_key in query_lower:
                regent_mentioned = regent_key
                break
        
        # Também verificar pelos nomes completos
        regent_names = {
            "sol": "sol",
            "lua": "lua", 
            "mercúrio": "mercurio",
            "vênus": "venus",
            "marte": "marte",
            "júpiter": "jupiter",
            "saturno": "saturno",
            "urano": "urano",
            "netuno": "netuno",
            "plutão": "plutao"
        }
        
        if not regent_mentioned:
            for full_name, key in regent_names.items():
                if full_name in query_lower or key in query_lower:
                    regent_mentioned = full_name if full_name in regent_interpretations else key
                    break
        
        if regent_mentioned and regent_mentioned in regent_interpretations:
            interpretation = regent_interpretations[regent_mentioned]
            
            # Detectar casa se mencionada
            casa_info = ""
            import re
            casa_match = re.search(r'casa\s+(\d+)', query_lower)
            if casa_match:
                casa_num = int(casa_match.group(1))
                casa_meanings = {
                    1: "A Casa 1 amplifica sua necessidade de expressar sua identidade pessoal e liderar pelo exemplo.",
                    2: "A Casa 2 conecta sua missão aos recursos materiais, valores pessoais e talentos naturais.",
                    3: "A Casa 3 enfatiza a comunicação, aprendizado e conexões com o ambiente próximo.",
                    4: "A Casa 4 conecta sua jornada às raízes familiares, lar e fundamentos emocionais.",
                    5: "A Casa 5 amplifica sua criatividade, autoexpressão e capacidade de inspirar alegria nos outros.",
                    6: "A Casa 6 conecta sua missão ao serviço, saúde e aperfeiçoamento de rotinas diárias.",
                    7: "A Casa 7 enfatiza parcerias, relacionamentos e capacidade de cooperação.",
                    8: "A Casa 8 intensifica sua jornada de transformação, cura e regeneração pessoal.",
                    9: "A Casa 9 expande sua busca por sabedoria, filosofia e conexões com culturas diferentes.",
                    10: "A Casa 10 conecta sua missão à carreira, reputação e contribuição pública.",
                    11: "A Casa 11 enfatiza sua conexão com grupos, amizades e ideais coletivos.",
                    12: "A Casa 12 aprofunda sua jornada espiritual, intuição e capacidade de transcendência."
                }
                
                if casa_num in casa_meanings:
                    casa_info = f"\n\n{casa_meanings[casa_num]}"
            
            return f"{interpretation['core']}\n\n{interpretation['practical']}{casa_info}"
        
        # Interpretação geral sobre regentes
        if "regente do mapa" in query_lower:
            return """O regente do mapa é o planeta que governa seu signo ascendente e representa o 'CEO' da sua personalidade. Este planeta atua como seu guia principal, influenciando como você aborda a vida e quais são suas prioridades naturais.

O regente revela sua missão de vida fundamental e as qualidades que você deve desenvolver para alcançar seu potencial máximo. Compreender seu regente oferece insights profundos sobre seus talentos naturais, desafios principais e a melhor forma de navegar sua jornada pessoal.

Quando você alinha suas ações com as qualidades do seu regente, experimenta maior fluidez, realização e autenticidade na vida."""
        
        return None

    def get_context(
        self,
        planet: Optional[str] = None,
        sign: Optional[str] = None,
        house: Optional[int] = None,
        aspect: Optional[str] = None,
        query: Optional[str] = None,
    ) -> List[Dict[str, any]]:
        planet_name = self.normalize_planet(planet)
        sign_name = self.normalize_sign(sign)
        sections: List[str] = []

        planet_section = self._planet_section(planet_name) if planet_name else None
        if planet_section:
            sections.append(planet_section)

        sign_section = self._sign_section(sign_name) if sign_name else None
        if sign_section:
            sections.append(sign_section)

        if planet_name and sign_name:
            sections.append(self._planet_sign_combo(planet_name, sign_name))

        if house and isinstance(house, int):
            house_section = self._house_section(house, planet_name, sign_name)
            if house_section:
                sections.append(house_section)

        aspect_section = self._aspect_section(aspect, planet_name, sign_name)
        if aspect_section:
            sections.append(aspect_section)

        # Verificar se é uma consulta sobre elementos ou modalidades
        if query and ("elemento" in query.lower() or "modalidade" in query.lower()):
            element_interpretation = self._get_element_interpretation(query)
            if element_interpretation:
                sections.append(element_interpretation)
        elif query and "regente do mapa" in query.lower():
            regent_interpretation = self._get_regent_interpretation(query)
            if regent_interpretation:
                sections.append(regent_interpretation)
        elif query:
            # Para outras queries, não incluir o contexto diretamente
            pass

        if not sections:
            return []

        chunk = KnowledgeChunk("\n\n".join(sections))
        return [chunk.as_dict()]


