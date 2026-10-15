"""Limpeza de textos gerados pela LLM."""

import re


def deduplicate_text(text: str) -> str:
    """
    Remove duplicações de texto nas interpretações geradas.
    Remove parágrafos duplicados, frases repetidas e padrões comuns.
    """
    if not text or len(text.strip()) < 50:
        return text
    
    # Remover duplicações de parágrafos inteiros
    paragraphs = text.split('\n\n')
    seen_paragraphs = set()
    unique_paragraphs = []
    
    for para in paragraphs:
        para_clean = para.strip()
        if not para_clean:
            unique_paragraphs.append(para)
            continue
        
        # Normalizar para comparação (remover espaços extras, case insensitive, remover pontuação final)
        para_key = re.sub(r'\s+', ' ', para_clean.lower())
        para_key = re.sub(r'[.,;:!?]+$', '', para_key).strip()
        
        # Ignorar parágrafos muito curtos (provavelmente títulos ou separadores)
        if len(para_key) > 50:
            if para_key not in seen_paragraphs:
                seen_paragraphs.add(para_key)
                unique_paragraphs.append(para)
        else:
            # Manter parágrafos curtos (títulos, etc) mas verificar duplicação
            if para_key not in seen_paragraphs or len(para_key) < 20:
                seen_paragraphs.add(para_key)
                unique_paragraphs.append(para)
    
    text = '\n\n'.join(unique_paragraphs)
    
    # Remover frases duplicadas dentro do mesmo parágrafo
    lines = text.split('\n')
    cleaned_lines = []
    seen_sentences = set()
    
    for line in lines:
        if not line.strip():
            cleaned_lines.append(line)
            continue
        
        # Dividir por pontos finais para detectar frases repetidas
        sentences = re.split(r'[.!?]+\s+', line)
        unique_sentences = []
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            sentence_clean = re.sub(r'\s+', ' ', sentence.strip().lower())
            sentence_clean = re.sub(r'[.,;:!?]+$', '', sentence_clean).strip()
            
            # Ignorar frases muito curtas (provavelmente parte de listas)
            if len(sentence_clean) > 30:
                if sentence_clean not in seen_sentences:
                    seen_sentences.add(sentence_clean)
                    unique_sentences.append(sentence.strip())
            else:
                unique_sentences.append(sentence.strip())
        
        if unique_sentences:
            cleaned_lines.append('. '.join(unique_sentences))
        else:
            cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    
    # Remover padrões comuns de repetição
    patterns_to_deduplicate = [
        r'A pessoa pode esperar:.*?(?=\n\n|\*\*|$)',
        r'The person can expect:.*?(?=\n\n|\*\*|$)',
        r'Oportunidades de crescimento e expansão.*?(?=\n\n|\*\*|$)',
        r'Opportunities for growth and expansion.*?(?=\n\n|\*\*|$)',
        r'Liderança e autoconfiança.*?(?=\n\n|\*\*|$)',
        r'Desenvolver habilidades de comunicação.*?(?=\n\n|\*\*|$)',
        r'Buscar apoio emocional.*?(?=\n\n|\*\*|$)',
    ]
    
    for pattern in patterns_to_deduplicate:
        matches = list(re.finditer(pattern, text, re.IGNORECASE | re.DOTALL))
        if len(matches) > 1:
            # Manter apenas a primeira ocorrência, remover as demais
            for match in matches[1:]:
                text = text[:match.start()] + text[match.end():]
    
    # Limpar espaços extras e quebras de linha múltiplas
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    return text.strip()
