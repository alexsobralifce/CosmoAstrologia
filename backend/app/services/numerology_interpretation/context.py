"""Recuperação de contexto no RAG e nota de números mestres."""

from typing import Any, Dict, List, Tuple


def retrieve_context(rag_service, queries: List[str]) -> Tuple[str, List[Dict[str, Any]]]:
    """Busca cada consulta no RAG, remove repetidos e devolve (texto de contexto, documentos únicos)."""
    context_documents = []
    if rag_service:
        for query in queries:
            try:
                results = rag_service.search(query, top_k=5, expand_query=True, category='numerology')
                context_documents.extend(results)
            except Exception as e:
                print(f"[WARNING] Erro ao buscar query '{query}': {e}")
    
    # Remover duplicatas e ordenar por relevância (aumentado limite para mais contexto de tarot)
    seen_texts = set()
    unique_docs = []
    for doc in sorted(context_documents, key=lambda x: x.get('score', 0), reverse=True):
        doc_text = doc.get('text', '').strip()
        if doc_text and doc_text not in seen_texts and len(doc_text) > 50:
            seen_texts.add(doc_text)
            unique_docs.append(doc)
            if len(unique_docs) >= 30:  # Aumentado de 20 para 30 para incluir mais contexto de tarot
                break
    
    context_text = "\n\n".join([
        f"[Fonte: {doc.get('source', 'unknown')} - Página {doc.get('page', 1)}]\n{doc.get('text', '')}"
        for doc in unique_docs[:20]  # Aumentado de 15 para 20 para incluir mais contexto de tarot
        if doc.get('text')
    ])
    return context_text, unique_docs


def describe_master_numbers(numerology_map: Dict[str, Any]) -> str:
    """Texto que informa à LLM quais números do mapa são mestres."""
    master_info = []
    if numerology_map['life_path']['is_master']:
        master_info.append(f"Caminho de Vida {numerology_map['life_path']['number']} é um Número Mestre")
    if numerology_map['destiny']['is_master']:
        master_info.append(f"Destino {numerology_map['destiny']['number']} é um Número Mestre")
    if numerology_map['soul']['is_master']:
        master_info.append(f"Alma {numerology_map['soul']['number']} é um Número Mestre")
    
    master_note = "\n".join(master_info) if master_info else "Nenhum número mestre presente."
    return master_note
