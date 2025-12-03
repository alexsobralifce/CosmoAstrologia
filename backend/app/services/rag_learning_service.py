"""
Serviço de Aprendizado Contínuo para RAG.
Permite que o RAG aprenda e expanda seus conhecimentos a partir das interpretações geradas.
"""

import json
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict


class RAGLearningService:
    """Gerencia o aprendizado contínuo do RAG a partir de interpretações geradas."""
    
    def __init__(self, learning_path: str = "rag_learning"):
        """
        Inicializa o serviço de aprendizado.
        
        Args:
            learning_path: Caminho para armazenar dados de aprendizado
        """
        self.learning_path = Path(learning_path)
        self.learning_path.mkdir(parents=True, exist_ok=True)
        
        self.learned_file = self.learning_path / "learned_interpretations.json"
        self.metadata_file = self.learning_path / "learning_metadata.json"
        
        # Carregar dados existentes
        self.learned_interpretations: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {
            "total_learned": 0,
            "total_validated": 0,
            "total_rejected": 0,
            "by_category": defaultdict(int),
            "last_updated": None
        }
        
        self._load_data()
    
    def _load_data(self):
        """Carrega dados de aprendizado do disco."""
        # Carregar interpretações aprendidas
        if self.learned_file.exists():
            try:
                with open(self.learned_file, 'r', encoding='utf-8') as f:
                    self.learned_interpretations = json.load(f)
            except Exception as e:
                print(f"[RAG-Learning] Erro ao carregar interpretações: {e}")
                self.learned_interpretations = []
        
        # Carregar metadados
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                    # Converter defaultdict de volta
                    if "by_category" in self.metadata:
                        self.metadata["by_category"] = defaultdict(int, self.metadata["by_category"])
            except Exception as e:
                print(f"[RAG-Learning] Erro ao carregar metadados: {e}")
    
    def _save_data(self):
        """Salva dados de aprendizado no disco."""
        try:
            # Salvar interpretações
            with open(self.learned_file, 'w', encoding='utf-8') as f:
                json.dump(self.learned_interpretations, f, ensure_ascii=False, indent=2)
            
            # Salvar metadados (converter defaultdict para dict)
            metadata_to_save = self.metadata.copy()
            metadata_to_save["by_category"] = dict(self.metadata["by_category"])
            metadata_to_save["last_updated"] = datetime.now().isoformat()
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[RAG-Learning] Erro ao salvar dados: {e}")
    
    def _generate_hash(self, text: str) -> str:
        """Gera hash único para um texto (para detectar duplicatas)."""
        # Normalizar texto (remover espaços extras, converter para minúsculas)
        normalized = re.sub(r'\s+', ' ', text.strip().lower())
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def validate_interpretation(self, interpretation: str, metadata: Dict[str, Any]) -> tuple[bool, str]:
        """
        Valida se uma interpretação deve ser aprendida.
        
        Args:
            interpretation: Texto da interpretação
            metadata: Metadados (query, planeta, signo, casa, categoria)
        
        Returns:
            Tupla (deve_aprender, motivo)
        """
        # Validação 1: Comprimento mínimo
        if len(interpretation.strip()) < 200:
            return False, "Interpretação muito curta (mínimo 200 caracteres)"
        
        # Validação 2: Verificar se não é apenas texto genérico
        generic_phrases = [
            "não foi possível",
            "erro ao",
            "não encontrado",
            "não disponível",
            "por favor",
            "tente novamente"
        ]
        interpretation_lower = interpretation.lower()
        if any(phrase in interpretation_lower for phrase in generic_phrases):
            return False, "Contém frases genéricas de erro"
        
        # Validação 3: Verificar se contém informações específicas
        # Se tem planeta/casa, verificar se menciona
        if metadata.get("planet"):
            planet_lower = metadata["planet"].lower()
            if planet_lower not in interpretation_lower:
                return False, f"Não menciona o planeta {metadata['planet']}"
        
        if metadata.get("house"):
            house_mentions = [
                f"casa {metadata['house']}",
                f"{metadata['house']}ª casa",
                f"casa {metadata['house']}ª"
            ]
            if not any(mention in interpretation_lower for mention in house_mentions):
                # Não é crítico, mas preferível
                pass
        
        # Validação 4: Verificar duplicatas
        text_hash = self._generate_hash(interpretation)
        for learned in self.learned_interpretations:
            if learned.get("hash") == text_hash:
                return False, "Interpretação duplicada"
        
        # Validação 5: Verificar similaridade muito alta (80%+)
        for learned in self.learned_interpretations:
            learned_text = learned.get("text", "")
            if len(learned_text) > 0:
                similarity = self._calculate_similarity(interpretation, learned_text)
                if similarity > 0.8:
                    return False, f"Interpretação muito similar (similaridade: {similarity:.2f})"
        
        return True, "Válida"
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade simples entre dois textos (0-1)."""
        # Normalizar textos
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def should_learn(self, interpretation: str, metadata: Dict[str, Any]) -> bool:
        """
        Decide se uma interpretação deve ser aprendida.
        
        Args:
            interpretation: Texto da interpretação
            metadata: Metadados da interpretação
        
        Returns:
            True se deve aprender, False caso contrário
        """
        is_valid, reason = self.validate_interpretation(interpretation, metadata)
        
        if not is_valid:
            print(f"[RAG-Learning] Interpretação rejeitada: {reason}")
            self.metadata["total_rejected"] += 1
            return False
        
        return True
    
    def save_interpretation(
        self,
        interpretation: str,
        query: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Salva uma interpretação para aprendizado.
        
        Args:
            interpretation: Texto da interpretação gerada
            query: Query original usada
            metadata: Metadados adicionais (planeta, signo, casa, categoria)
        
        Returns:
            True se foi salva, False caso contrário
        """
        if not metadata:
            metadata = {}
        
        # Verificar se deve aprender
        if not self.should_learn(interpretation, metadata):
            return False
        
        # Criar entrada de aprendizado
        learned_entry = {
            "text": interpretation.strip(),
            "hash": self._generate_hash(interpretation),
            "query": query,
            "metadata": metadata,
            "category": metadata.get("category", "astrology"),
            "learned_at": datetime.now().isoformat(),
            "source": "groq_generated"
        }
        
        # Adicionar à lista
        self.learned_interpretations.append(learned_entry)
        
        # Atualizar estatísticas
        self.metadata["total_learned"] += 1
        self.metadata["total_validated"] += 1
        category = metadata.get("category", "astrology")
        self.metadata["by_category"][category] += 1
        
        # Salvar no disco
        self._save_data()
        
        print(f"[RAG-Learning] ✅ Interpretação aprendida (total: {self.metadata['total_learned']})")
        return True
    
    def get_learned_interpretations(
        self,
        category: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retorna interpretações aprendidas.
        
        Args:
            category: Filtrar por categoria ('astrology' ou 'numerology')
            limit: Limitar número de resultados
        
        Returns:
            Lista de interpretações aprendidas
        """
        results = self.learned_interpretations
        
        if category:
            results = [r for r in results if r.get("category") == category]
        
        if limit:
            results = results[:limit]
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do aprendizado."""
        return {
            "total_learned": self.metadata["total_learned"],
            "total_validated": self.metadata["total_validated"],
            "total_rejected": self.metadata["total_rejected"],
            "by_category": dict(self.metadata["by_category"]),
            "last_updated": self.metadata.get("last_updated")
        }
    
    def clear_learned_data(self):
        """Limpa todos os dados aprendidos (útil para testes)."""
        self.learned_interpretations = []
        self.metadata = {
            "total_learned": 0,
            "total_validated": 0,
            "total_rejected": 0,
            "by_category": defaultdict(int),
            "last_updated": None
        }
        self._save_data()
        print("[RAG-Learning] Dados de aprendizado limpos")


# Instância global
_learning_service_instance: Optional[RAGLearningService] = None


def get_learning_service() -> RAGLearningService:
    """Obtém instância singleton do serviço de aprendizado."""
    global _learning_service_instance
    
    if _learning_service_instance is None:
        service_path = Path(__file__).parent.parent.parent
        learning_path = service_path / "rag_learning"
        _learning_service_instance = RAGLearningService(str(learning_path))
    
    return _learning_service_instance

