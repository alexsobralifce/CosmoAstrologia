#!/usr/bin/env python3
"""
Script para testar as melhorias na interpretação numerológica.
Verifica se a interpretação está mais detalhada, com pontos positivos/negativos
e linguagem inspiradora.
"""

import requests
import json
import sys
from datetime import datetime
import re

# Configuração
API_BASE_URL = "http://localhost:8000"

def test_numerology_interpretation():
    """Testa o endpoint de interpretação numerológica"""
    
    print("=" * 80)
    print("🧪 TESTE DAS MELHORIAS NA INTERPRETAÇÃO NUMEROLÓGICA")
    print("=" * 80)
    print(f"API URL: {API_BASE_URL}")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Primeiro, precisamos autenticar ou usar um token existente
    # Para teste, vamos assumir que você tem um token válido
    # Ou podemos criar um usuário de teste
    
    print("📋 NOTA: Este teste requer autenticação.")
    print("   Você pode fornecer um token JWT ou usar um usuário de teste existente.")
    print()
    
    # Verificar se backend está rodando
    try:
        health_check = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health_check.status_code != 200:
            print(f"⚠️  Backend pode não estar rodando corretamente")
    except:
        print(f"❌ ERRO: Backend não está acessível em {API_BASE_URL}")
        print(f"   Certifique-se de que o backend está rodando antes de executar o teste.")
        return 1
    
    # Tentar usar token fornecido ou criar usuário de teste
    token = None
    
    # Opção 1: Verificar se há token fornecido como argumento
    if len(sys.argv) > 1:
        token = sys.argv[1]
        print(f"✅ Usando token fornecido: {token[:20]}...")
    else:
        # Opção 2: Tentar criar usuário de teste
        test_email = f"test_numerology_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com"
        test_password = "Test123!@#"
        test_name = "Teste Numerologia"
        
        print(f"📝 Tentando criar usuário de teste...")
        print(f"   Email: {test_email}")
        print(f"   Nome: {test_name}")
        print()
        
        try:
            # Registrar usuário de teste
            register_response = requests.post(
                f"{API_BASE_URL}/api/auth/register",
                json={
                    "email": test_email,
                    "password": test_password,
                    "name": test_name,
                    "birth_data": {
                        "name": test_name,
                        "birth_date": "1985-05-15",
                        "birth_time": "14:30",
                        "birth_place": "São Paulo, SP, Brasil",
                        "latitude": -23.5505,
                        "longitude": -46.6333
                    }
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if register_response.status_code in [200, 201]:
                auth_data = register_response.json()
                token = auth_data.get("access_token")
                if token:
                    print(f"✅ Usuário criado e token obtido: {token[:20]}...")
                else:
                    print(f"⚠️  Resposta inesperada do registro")
                    print(f"   Status: {register_response.status_code}")
                    print(f"   Resposta: {register_response.text[:200]}")
                    print()
                    print(f"💡 DICA: Você pode fornecer um token JWT como argumento:")
                    print(f"   python3 test_numerologia_melhorias.py SEU_TOKEN_AQUI")
                    return 1
            else:
                print(f"⚠️  Não foi possível criar usuário (status {register_response.status_code})")
                print(f"   Resposta: {register_response.text[:200]}")
                print()
                print(f"💡 DICA: Use um token JWT existente:")
                print(f"   python3 test_numerologia_melhorias.py SEU_TOKEN_AQUI")
                return 1
        except Exception as e:
            print(f"❌ Erro ao criar usuário: {e}")
            print()
            print(f"💡 DICA: Use um token JWT existente:")
            print(f"   python3 test_numerologia_melhorias.py SEU_TOKEN_AQUI")
            return 1
    
    if not token:
        print(f"❌ Não foi possível obter token de autenticação")
        return 1
    
    print()
    
    # 2. Testar endpoint de interpretação numerológica
    try:
        print(f"🔗 Testando endpoint: /api/numerology/interpretation")
        print(f"📤 Enviando requisição...")
        
        interpretation_response = requests.post(
            f"{API_BASE_URL}/api/numerology/interpretation",
            json={"language": "pt"},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            timeout=120  # Timeout maior para interpretação completa
        )
        
        print(f"📥 Status Code: {interpretation_response.status_code}")
        print()
        
        if interpretation_response.status_code == 200:
            data = interpretation_response.json()
            interpretation = data.get("interpretation", "")
            
            print(f"✅ SUCESSO! Interpretação recebida")
            print()
            
            # Análise da interpretação
            print(f"📊 ANÁLISE DA INTERPRETAÇÃO:")
            print("-" * 80)
            
            # 1. Tamanho
            char_count = len(interpretation)
            word_count = len(interpretation.split())
            print(f"   📏 Tamanho: {char_count:,} caracteres, {word_count:,} palavras")
            
            # Verificar se está maior que antes (antes era ~1000-2000 caracteres)
            if char_count > 2000:
                print(f"   ✅ Tamanho adequado (esperado > 2000 caracteres)")
            else:
                print(f"   ⚠️  Tamanho menor que o esperado (esperado > 2000 caracteres)")
            
            print()
            
            # 2. Estrutura - Verificar seções
            print(f"   📑 ESTRUTURA:")
            sections_found = []
            
            # Verificar seções esperadas
            section_keywords = {
                "Introdução": ["bem-vindo", "bem vindo", "boas-vindas", "ferramentas de autoconhecimento"],
                "Caminho de Vida": ["caminho de vida", "caminho de vida", "missão de vida"],
                "Número do Destino": ["número do destino", "destino", "expressão", "talentos naturais"],
                "Número da Alma": ["número da alma", "alma", "desejo do coração", "motivações"],
                "Número da Personalidade": ["número da personalidade", "personalidade", "apresenta ao mundo"],
                "Número do Aniversário": ["número do aniversário", "aniversário", "talentos especiais"],
                "Número da Maturidade": ["número da maturidade", "maturidade", "segunda metade da vida"],
                "Síntese": ["síntese", "visão unificada", "orientação final", "abraçar seu caminho"]
            }
            
            for section, keywords in section_keywords.items():
                found = any(keyword.lower() in interpretation.lower() for keyword in keywords)
                if found:
                    sections_found.append(section)
                    print(f"      ✅ {section}")
                else:
                    print(f"      ❌ {section} (não encontrado)")
            
            print()
            
            # 3. Pontos Positivos
            print(f"   ✨ PONTOS POSITIVOS:")
            positive_patterns = [
                r"pontos?\s+positivos?",
                r"forças?",
                r"talentos?",
                r"características?\s+positivas?",
                r"pontos?\s+fortes?",
                r"qualidades?"
            ]
            
            positive_found = any(re.search(pattern, interpretation, re.IGNORECASE) for pattern in positive_patterns)
            if positive_found:
                print(f"      ✅ Menção a pontos positivos encontrada")
            else:
                print(f"      ❌ Nenhuma menção a pontos positivos")
            
            # Contar listas de pontos positivos
            positive_lists = len(re.findall(r"(pontos?\s+positivos?|forças?|talentos?)[:•]\s*\n", interpretation, re.IGNORECASE))
            if positive_lists > 0:
                print(f"      ✅ {positive_lists} lista(s) de pontos positivos encontrada(s)")
            
            print()
            
            # 4. Desafios/Áreas de Atenção
            print(f"   ⚠️  DESAFIOS/ÁREAS DE ATENÇÃO:")
            challenge_patterns = [
                r"desafios?",
                r"áreas?\s+de\s+atenção",
                r"pontos?\s+de\s+atenção",
                r"fraquezas?",
                r"dificuldades?"
            ]
            
            challenge_found = any(re.search(pattern, interpretation, re.IGNORECASE) for pattern in challenge_patterns)
            if challenge_found:
                print(f"      ✅ Menção a desafios/áreas de atenção encontrada")
            else:
                print(f"      ❌ Nenhuma menção a desafios/áreas de atenção")
            
            print()
            
            # 5. Orientações Práticas
            print(f"   💡 ORIENTAÇÕES PRÁTICAS:")
            guidance_patterns = [
                r"orientações?",
                r"dicas?",
                r"sugestões?",
                r"como\s+usar",
                r"como\s+desenvolver",
                r"práticas?",
                r"recomendações?"
            ]
            
            guidance_found = any(re.search(pattern, interpretation, re.IGNORECASE) for pattern in guidance_patterns)
            if guidance_found:
                print(f"      ✅ Menção a orientações práticas encontrada")
            else:
                print(f"      ❌ Nenhuma menção a orientações práticas")
            
            print()
            
            # 6. Linguagem Inspiradora
            print(f"   🌟 LINGUAGEM INSPIRADORA:")
            inspiring_words = [
                "crescimento", "evolução", "potencial", "realização",
                "desenvolver", "abraçar", "transformar", "oportunidades",
                "possibilidades", "inspirador", "encorajador", "empoderador"
            ]
            
            inspiring_count = sum(1 for word in inspiring_words if word.lower() in interpretation.lower())
            if inspiring_count >= 5:
                print(f"      ✅ Linguagem inspiradora presente ({inspiring_count} palavras inspiradoras encontradas)")
            else:
                print(f"      ⚠️  Pouca linguagem inspiradora ({inspiring_count} palavras encontradas)")
            
            print()
            
            # 7. Resumo
            print(f"📋 RESUMO:")
            print("-" * 80)
            
            score = 0
            total_checks = 7
            
            if char_count > 2000:
                score += 1
            if len(sections_found) >= 6:
                score += 1
            if positive_found:
                score += 1
            if challenge_found:
                score += 1
            if guidance_found:
                score += 1
            if inspiring_count >= 5:
                score += 1
            if positive_lists > 0:
                score += 1
            
            print(f"   Pontuação: {score}/{total_checks}")
            
            if score >= 6:
                print(f"   ✅ EXCELENTE! A interpretação está completa e melhorada!")
            elif score >= 4:
                print(f"   ⚠️  BOM, mas pode melhorar. Alguns elementos estão faltando.")
            else:
                print(f"   ❌ A interpretação não está com as melhorias esperadas.")
            
            print()
            
            # 8. Preview da interpretação
            print(f"📄 PREVIEW DA INTERPRETAÇÃO (primeiros 500 caracteres):")
            print("-" * 80)
            print(interpretation[:500])
            print("...")
            print()
            
            # 9. Informações adicionais
            print(f"📊 INFORMAÇÕES ADICIONAIS:")
            print(f"   - Gerado por: {data.get('generated_by', 'N/A')}")
            print(f"   - Query usado: {data.get('query_used', 'N/A')}")
            print(f"   - Fontes: {len(data.get('sources', []))} fonte(s)")
            
            return 0 if score >= 6 else 1
            
        else:
            print(f"❌ ERRO!")
            print(f"   Status: {interpretation_response.status_code}")
            print(f"   Resposta: {interpretation_response.text[:500]}")
            return 1
    
    except requests.exceptions.ConnectionError:
        print(f"❌ ERRO: Não foi possível conectar ao servidor")
        print(f"   Verifique se o backend está rodando em {API_BASE_URL}")
        return 1
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    try:
        exit_code = test_numerology_interpretation()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

