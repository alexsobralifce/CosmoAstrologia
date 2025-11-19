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
    1: {"focus": "identidade, estilo pessoal e iniciativa", "question": "Como eu me apresento e inicio novos ciclos?"},
    2: {"focus": "valores, finanças e autoestima", "question": "Do que preciso para sentir segurança material?"},
    3: {"focus": "comunicação, estudos e laços fraternos", "question": "Como troco ideias e circulo pelas minhas redes próximas?"},
    4: {"focus": "família, raízes e intimidade emocional", "question": "Onde ancoro minha vida interior?"},
    5: {"focus": "criatividade, romance e expressão lúdica", "question": "De que modo celebro meus talentos e prazeres?"},
    6: {"focus": "rotina, saúde e serviço", "question": "Como organizo o cotidiano e cuido do meu corpo?"},
    7: {"focus": "parcerias, contratos e espelhamentos", "question": "Quais qualidades busco nos relacionamentos?"},
    8: {"focus": "transformação, recursos compartilhados e intimidade profunda", "question": "Como lido com entregas e renascimentos?"},
    9: {"focus": "propósito, estudos superiores e viagens", "question": "Que crenças expandem minha visão de mundo?"},
    10: {"focus": "carreira, vocação e reputação", "question": "Como quero ser reconhecido no mundo?"},
    11: {"focus": "amizades, coletivos e futuro", "question": "Quais causas desejo apoiar com minha rede?"},
    12: {"focus": "inconsciente, espiritualidade e retiros", "question": "Do que preciso para recarregar e escutar minha intuição?"},
}


ASPECT_MEANINGS: Dict[str, str] = {
    "conjunção": "Integra energias semelhantes; pode intensificar tanto talentos quanto desafios por falta de distância crítica.",
    "oposição": "Pede conciliação entre polos; projeta qualidades no outro para que ocorra equilíbrio consciente.",
    "quadratura": "Gera tensão criativa; obriga a agir e reorganizar prioridades para evitar estagnação.",
    "trígono": "Facilita o fluxo; talentos naturais podem ser potencializados com consciência e gratidão.",
    "sextil": "Oferta oportunidades sutis; exige movimento intencional para aproveitar as portas abertas.",
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
        return (
            f"{prefix} {data['focus']}. Pergunta-chave: {data['question']} "
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
        return f"O aspecto de {aspect.lower()} envolvendo {subject} lembra que {meaning}"

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

        if query:
            sections.append(f"Contexto da consulta: {query}")

        if not sections:
            return []

        chunk = KnowledgeChunk("\n\n".join(sections))
        return [chunk.as_dict()]


