#!/usr/bin/env python3
"""
Script para testar o funcionamento do endpoint /api/full-birth-chart/section
"""

import requests
import json
import sys
from datetime import datetime

# Configuração
API_BASE_URL = "http://localhost:8000"
# Para produção, usar: API_BASE_URL = "https://seu-backend.railway.app"

def test_full_birth_chart_section():
    """Testa a geração de uma seção do mapa astral completo"""
    
    print("=" * 80)
    print("🧪 TESTE DO MAPA ASTRAL COMPLETO")
    print("=" * 80)
    print(f"API URL: {API_BASE_URL}")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Dados de teste (exemplo de mapa astral)
    test_data = {
        "name": "Teste Usuário",
        "birthDate": "20/10/1981",
        "birthTime": "13:30",
        "birthPlace": "Sobral, Ceará, Brasil",
        "sunSign": "Libra",
        "moonSign": "Leão",
        "ascendant": "Aquário",
        "sunHouse": 8,
        "moonHouse": 6,
        "section": "karma",  # Testando a seção que estava dando erro
        "language": "pt",
        # Planetas pessoais
        "mercurySign": "Libra",
        "mercuryHouse": 8,
        "venusSign": "Sagitário",
        "venusHouse": 10,
        "marsSign": "Leão",
        "marsHouse": 7,
        # Planetas sociais
        "jupiterSign": "Libra",
        "jupiterHouse": 8,
        "saturnSign": "Libra",
        "saturnHouse": 8,
        # Planetas geracionais
        "uranusSign": "Escorpião",
        "uranusHouse": 9,
        "neptuneSign": "Sagitário",
        "neptuneHouse": 10,
        "plutoSign": "Libra",
        "plutoHouse": 8,
        # Nodos
        "northNodeSign": "Câncer",
        "northNodeHouse": 6,
        "southNodeSign": "Capricórnio",
        "southNodeHouse": 12,
        # Quíron
        "chironSign": "Touro",
        "chironHouse": 3,
        # Meio do Céu
        "midheavenSign": "Escorpião",
        "icSign": "Touro"
    }
    
    # Testar todas as seções
    sections = ["power", "triad", "personal", "houses", "karma", "synthesis"]
    
    results = {}
    
    for section in sections:
        print(f"\n📋 Testando seção: {section.upper()}")
        print("-" * 80)
        
        test_data["section"] = section
        endpoint = f"{API_BASE_URL}/api/full-birth-chart/section"
        
        try:
            print(f"🔗 Endpoint: {endpoint}")
            print(f"📤 Enviando requisição...")
            
            response = requests.post(
                endpoint,
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=120  # 2 minutos para geração com IA
            )
            
            print(f"📥 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCESSO!")
                print(f"   Seção: {result.get('section', 'N/A')}")
                print(f"   Título: {result.get('title', 'N/A')}")
                print(f"   Gerado por: {result.get('generated_by', 'N/A')}")
                print(f"   Tamanho do conteúdo: {len(result.get('content', ''))} caracteres")
                
                # Mostrar preview do conteúdo
                content = result.get('content', '')
                if content:
                    preview = content[:200] + "..." if len(content) > 200 else content
                    print(f"   Preview: {preview}")
                
                results[section] = {
                    "status": "success",
                    "title": result.get('title'),
                    "content_length": len(result.get('content', '')),
                    "generated_by": result.get('generated_by')
                }
            else:
                print(f"❌ ERRO!")
                print(f"   Status: {response.status_code}")
                print(f"   Resposta: {response.text[:500]}")
                results[section] = {
                    "status": "error",
                    "status_code": response.status_code,
                    "error": response.text[:200]
                }
                
        except requests.exceptions.ConnectionError:
            print(f"❌ ERRO: Não foi possível conectar ao servidor")
            print(f"   Verifique se o backend está rodando em {API_BASE_URL}")
            results[section] = {
                "status": "connection_error",
                "error": "Servidor não disponível"
            }
        except requests.exceptions.Timeout:
            print(f"❌ ERRO: Timeout - requisição demorou mais de 2 minutos")
            results[section] = {
                "status": "timeout",
                "error": "Requisição expirou"
            }
        except Exception as e:
            print(f"❌ ERRO: {str(e)}")
            results[section] = {
                "status": "exception",
                "error": str(e)
            }
    
    # Resumo final
    print("\n" + "=" * 80)
    print("📊 RESUMO DOS TESTES")
    print("=" * 80)
    
    success_count = sum(1 for r in results.values() if r.get("status") == "success")
    total_count = len(results)
    
    for section, result in results.items():
        status = result.get("status", "unknown")
        if status == "success":
            print(f"✅ {section.upper()}: OK ({result.get('content_length', 0)} chars)")
        else:
            print(f"❌ {section.upper()}: FALHOU - {result.get('error', 'Erro desconhecido')}")
    
    print()
    print(f"✅ Sucessos: {success_count}/{total_count}")
    print(f"❌ Falhas: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        return 0
    else:
        print(f"\n⚠️  {total_count - success_count} TESTE(S) FALHARAM")
        return 1

if __name__ == "__main__":
    try:
        exit_code = test_full_birth_chart_section()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

