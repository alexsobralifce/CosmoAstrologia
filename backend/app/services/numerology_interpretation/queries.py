"""Consultas ao RAG para a interpretação numerológica (uma lista por mapa)."""

from typing import Any, Dict, List


def build_rag_queries(numerology_map: Dict[str, Any]) -> List[str]:
    """Monta as consultas sobre cada número do mapa, números mestres e correspondência com o Tarot."""
    queries = [
        # Caminho de Vida (mais importante)
        f"life path number {numerology_map['life_path']['number']} numerologia pitagórica significado missão pontos positivos negativos",
        f"caminho de vida {numerology_map['life_path']['number']} numerologia características forças fraquezas",
        f"number {numerology_map['life_path']['number']} numerology positive negative traits strengths weaknesses",
        
        # Número do Destino/Expressão
        f"expression destiny number {numerology_map['destiny']['number']} numerologia talentos habilidades",
        f"número expressão destino {numerology_map['destiny']['number']} numerologia pontos fortes desafios",
        f"destiny number {numerology_map['destiny']['number']} numerology talents abilities",
        
        # Número da Alma/Desejo do Coração
        f"soul desire heart number {numerology_map['soul']['number']} numerologia motivação desejos internos",
        f"número alma desejo coração {numerology_map['soul']['number']} numerologia motivações",
        f"soul number {numerology_map['soul']['number']} numerology inner desires motivations",
        
        # Número da Personalidade
        f"personality number {numerology_map['personality']['number']} numerologia como se apresenta mundo",
        f"número personalidade {numerology_map['personality']['number']} numerologia aparência externa",
        
        # Número do Aniversário
        f"birthday number {numerology_map['birthday']['number']} numerologia talentos especiais habilidades",
        f"número aniversário {numerology_map['birthday']['number']} numerologia dons naturais",
        
        # Número da Maturidade
        f"maturity number {numerology_map['maturity']['number']} numerologia segunda metade vida potencial",
        f"número maturidade {numerology_map['maturity']['number']} numerologia evolução futuro",
    ]
    
    # Adicionar queries para números mestres se aplicável
    if numerology_map['life_path']['is_master']:
        queries.append(f"master number {numerology_map['life_path']['number']} numerologia significado especial")
    if numerology_map['destiny']['is_master']:
        queries.append(f"master number {numerology_map['destiny']['number']} expression destiny")
    if numerology_map['soul']['is_master']:
        queries.append(f"master number {numerology_map['soul']['number']} soul heart desire")
    
    # Adicionar queries expandidas sobre tarot e numerologia para CADA número (forte ligação)
    # Caminho de Vida - Tarot
    queries.extend([
        f"tarot numerologia número {numerology_map['life_path']['number']} arcano correspondente significado",
        f"arcano maior número {numerology_map['life_path']['number']} tarot numerologia",
        f"carta tarot número {numerology_map['life_path']['number']} numerologia pitagórica",
        f"tarot arcano {numerology_map['life_path']['number']} caminho de vida numerologia",
        f"numerologia tarot conexão número {numerology_map['life_path']['number']} interpretação",
        f"arcanos maiores tarot numerologia número {numerology_map['life_path']['number']} significado completo",
    ])
    
    # Número do Destino - Tarot
    queries.extend([
        f"tarot numerologia número {numerology_map['destiny']['number']} arcano destino expressão",
        f"arcano maior número {numerology_map['destiny']['number']} tarot numerologia destino",
        f"carta tarot número {numerology_map['destiny']['number']} numerologia expressão",
        f"tarot arcano {numerology_map['destiny']['number']} destino numerologia",
        f"numerologia tarot conexão número {numerology_map['destiny']['number']} talentos",
    ])
    
    # Número da Alma - Tarot
    queries.extend([
        f"tarot numerologia número {numerology_map['soul']['number']} arcano alma desejo coração",
        f"arcano maior número {numerology_map['soul']['number']} tarot numerologia alma",
        f"carta tarot número {numerology_map['soul']['number']} numerologia desejo coração",
        f"tarot arcano {numerology_map['soul']['number']} alma numerologia motivações",
        f"numerologia tarot conexão número {numerology_map['soul']['number']} desejos internos",
    ])
    
    # Número da Personalidade - Tarot
    queries.extend([
        f"tarot numerologia número {numerology_map['personality']['number']} arcano personalidade",
        f"arcano maior número {numerology_map['personality']['number']} tarot numerologia personalidade",
        f"carta tarot número {numerology_map['personality']['number']} numerologia aparência",
        f"tarot arcano {numerology_map['personality']['number']} personalidade numerologia",
    ])
    
    # Número do Aniversário - Tarot
    queries.extend([
        f"tarot numerologia número {numerology_map['birthday']['number']} arcano aniversário",
        f"arcano maior número {numerology_map['birthday']['number']} tarot numerologia aniversário",
        f"carta tarot número {numerology_map['birthday']['number']} numerologia dia nascimento",
        f"tarot arcano {numerology_map['birthday']['number']} aniversário numerologia talentos",
    ])
    
    # Número da Maturidade - Tarot
    queries.extend([
        f"tarot numerologia número {numerology_map['maturity']['number']} arcano maturidade",
        f"arcano maior número {numerology_map['maturity']['number']} tarot numerologia maturidade",
        f"carta tarot número {numerology_map['maturity']['number']} numerologia segunda metade vida",
        f"tarot arcano {numerology_map['maturity']['number']} maturidade numerologia futuro",
    ])
    return queries
