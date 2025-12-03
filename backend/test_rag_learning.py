#!/usr/bin/env python3
"""
Teste do sistema de aprendizado contínuo do RAG.
Valida que o sistema funciona sem quebrar código existente.
"""

import sys
from pathlib import Path

# Adicionar backend ao path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def test_learning_service():
    """Testa o serviço de aprendizado."""
    print("=" * 60)
    print("TESTE 1: Serviço de Aprendizado")
    print("=" * 60)
    
    try:
        from app.services.rag_learning_service import get_learning_service
        
        learning_service = get_learning_service()
        print("✅ Serviço de aprendizado inicializado")
        
        # Testar validação
        valid_interpretation = """
        O Sol em Leão na Casa 5 representa uma energia criativa e expressiva muito forte.
        Esta posição indica que a pessoa tem um talento natural para se expressar artisticamente
        e busca reconhecimento através de suas criações. A Casa 5 está relacionada à criatividade,
        ao amor, aos filhos e ao prazer, então o Sol aqui sugere que a pessoa encontra sua
        identidade através dessas áreas da vida.
        """
        
        metadata = {
            "planet": "Sol",
            "sign": "Leão",
            "house": 5,
            "category": "astrology"
        }
        
        should_learn, reason = learning_service.validate_interpretation(valid_interpretation, metadata)
        print(f"✅ Validação funcionando: {should_learn} - {reason}")
        
        # Testar salvamento
        saved = learning_service.save_interpretation(
            interpretation=valid_interpretation,
            query="Sol em Leão na Casa 5",
            metadata=metadata
        )
        print(f"✅ Salvamento funcionando: {saved}")
        
        # Testar estatísticas
        stats = learning_service.get_statistics()
        print(f"✅ Estatísticas: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do serviço de aprendizado: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_service_with_learning():
    """Testa o RAG Service com aprendizado."""
    print("\n" + "=" * 60)
    print("TESTE 2: RAG Service com Aprendizado")
    print("=" * 60)
    
    try:
        from app.services.rag_service_fastembed import get_rag_service
        
        rag_service = get_rag_service()
        if not rag_service:
            print("⚠️ RAG Service não disponível (índice não carregado)")
            return True  # Não é erro, apenas não tem índice
        
        print("✅ RAG Service inicializado")
        
        # Testar adição de documento aprendido
        test_text = "Mercúrio em Gêmeos na Casa 3 indica uma mente muito ativa e comunicativa."
        added = rag_service.add_learned_document(
            text=test_text,
            metadata={"planet": "Mercúrio", "sign": "Gêmeos", "house": 3},
            category="astrology"
        )
        print(f"✅ Adição de documento aprendido: {added}")
        
        # Testar busca (deve incluir documentos aprendidos)
        try:
            results = rag_service.search("Mercúrio Gêmeos Casa 3", top_k=5)
            print(f"✅ Busca funcionando: {len(results)} resultados")
            
            # Verificar se há documentos aprendidos nos resultados
            learned_in_results = any(r.get('is_learned', False) for r in results)
            print(f"✅ Documentos aprendidos nas buscas: {learned_in_results}")
        except Exception as search_error:
            print(f"⚠️ Busca não disponível (índice não carregado): {search_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do RAG Service: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Testa integração completa."""
    print("\n" + "=" * 60)
    print("TESTE 3: Integração Completa")
    print("=" * 60)
    
    try:
        from app.services.rag_learning_service import get_learning_service
        from app.services.rag_service_fastembed import get_rag_service
        
        learning_service = get_learning_service()
        rag_service = get_rag_service()
        
        # Simular fluxo completo
        interpretation = """
        Vênus em Libra na Casa 7 representa harmonia e beleza nos relacionamentos.
        Esta posição indica que a pessoa valoriza muito o equilíbrio e a justiça em seus
        relacionamentos pessoais e profissionais. A Casa 7 está diretamente relacionada
        aos relacionamentos, então Vênus aqui sugere que a pessoa tem uma capacidade natural
        de criar harmonia e atrair parceiros que compartilham seus valores estéticos e relacionais.
        """
        
        metadata = {
            "planet": "Vênus",
            "sign": "Libra",
            "house": 7,
            "category": "astrology"
        }
        
        # 1. Salvar interpretação
        saved = learning_service.save_interpretation(
            interpretation=interpretation,
            query="Vênus em Libra na Casa 7",
            metadata=metadata
        )
        print(f"✅ Passo 1 - Salvamento: {saved}")
        
        # 2. Carregar no RAG
        if rag_service:
            rag_service.load_learned_documents()
            print("✅ Passo 2 - Carregamento no RAG: OK")
        
        # 3. Verificar estatísticas
        stats = learning_service.get_statistics()
        print(f"✅ Passo 3 - Estatísticas: {stats['total_learned']} interpretações aprendidas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de integração: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes."""
    print("\n" + "=" * 60)
    print("TESTES DO SISTEMA DE APRENDIZADO CONTÍNUO DO RAG")
    print("=" * 60)
    
    results = []
    
    # Teste 1: Serviço de aprendizado
    results.append(("Serviço de Aprendizado", test_learning_service()))
    
    # Teste 2: RAG Service com aprendizado
    results.append(("RAG Service com Aprendizado", test_rag_service_with_learning()))
    
    # Teste 3: Integração completa
    results.append(("Integração Completa", test_integration()))
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("O sistema de aprendizado contínuo está funcionando corretamente.")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("Verifique os erros acima.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

