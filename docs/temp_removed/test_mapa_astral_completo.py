#!/usr/bin/env python3
"""
Script para testar o endpoint /api/full-birth-chart/section com dados fictícios
e analisar os resultados em detalhes.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any

# Configuração
API_BASE_URL = "http://localhost:8000"

def test_full_birth_chart_section_detailed():
    """Testa a geração de uma seção do mapa astral completo com análise detalhada"""
    
    print("=" * 80)
    print("🧪 TESTE COMPLETO DO MAPA ASTRAL COM DADOS FICTÍCIOS")
    print("=" * 80)
    print(f"API URL: {API_BASE_URL}")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Dados fictícios de teste (exemplo realista)
    test_data = {
        "name": "Maria Silva Santos",
        "birthDate": "15/07/1990",
        "birthTime": "14:30",
        "birthPlace": "São Paulo, SP, Brasil",
        "sunSign": "Câncer",
        "moonSign": "Escorpião",
        "ascendant": "Leão",
        "sunHouse": 1,
        "moonHouse": 5,
        "section": "power",  # Começar com power
        "language": "pt",
        # Planetas pessoais
        "mercurySign": "Câncer",
        "mercuryHouse": 1,
        "venusSign": "Leão",
        "venusHouse": 2,
        "marsSign": "Virgem",
        "marsHouse": 3,
        # Planetas sociais
        "jupiterSign": "Câncer",
        "jupiterHouse": 1,
        "saturnSign": "Capricórnio",
        "saturnHouse": 7,
        # Planetas geracionais
        "uranusSign": "Capricórnio",
        "uranusHouse": 7,
        "neptuneSign": "Capricórnio",
        "neptuneHouse": 7,
        "plutoSign": "Escorpião",
        "plutoHouse": 5,
        # Nodos
        "northNodeSign": "Áries",
        "northNodeHouse": 10,
        "southNodeSign": "Libra",
        "southNodeHouse": 4,
        # Quíron
        "chironSign": "Câncer",
        "chironHouse": 1,
        # Meio do Céu
        "midheavenSign": "Touro",
        "icSign": "Escorpião",
        # Coordenadas (São Paulo)
        "latitude": -23.5505,
        "longitude": -46.6333
    }
    
    # Testar todas as seções
    sections = ["power", "triad", "personal", "houses", "karma", "synthesis"]
    
    results = {}
    analysis = {
        "total_requests": 0,
        "successful": 0,
        "failed": 0,
        "total_content_length": 0,
        "average_content_length": 0,
        "sections_analysis": {}
    }
    
    print("📋 DADOS DE TESTE:")
    print(f"   Nome: {test_data['name']}")
    print(f"   Data: {test_data['birthDate']} às {test_data['birthTime']}")
    print(f"   Local: {test_data['birthPlace']}")
    print(f"   Coordenadas: ({test_data['latitude']}, {test_data['longitude']})")
    print(f"   Tríade: Sol {test_data['sunSign']}, Lua {test_data['moonSign']}, Asc {test_data['ascendant']}")
    print()
    
    for section in sections:
        print(f"\n{'='*80}")
        print(f"📋 Testando seção: {section.upper()}")
        print("="*80)
        
        test_data["section"] = section
        endpoint = f"{API_BASE_URL}/api/full-birth-chart/section"
        
        analysis["total_requests"] += 1
        
        try:
            print(f"🔗 Endpoint: {endpoint}")
            print(f"📤 Enviando requisição...")
            
            start_time = datetime.now()
            
            response = requests.post(
                endpoint,
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=120  # 2 minutos para geração com IA
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"📥 Status Code: {response.status_code}")
            print(f"⏱️  Tempo de resposta: {duration:.2f}s")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCESSO!")
                print(f"   Seção: {result.get('section', 'N/A')}")
                print(f"   Título: {result.get('title', 'N/A')}")
                print(f"   Gerado por: {result.get('generated_by', 'N/A')}")
                
                content = result.get('content', '')
                content_length = len(content)
                analysis["total_content_length"] += content_length
                analysis["successful"] += 1
                
                print(f"   Tamanho do conteúdo: {content_length:,} caracteres")
                print(f"   Número de palavras: ~{len(content.split())} palavras")
                
                # Análise do conteúdo
                has_temperament = 'temperamento' in content.lower() or 'elemento' in content.lower()
                has_dignities = 'domicílio' in content.lower() or 'exaltação' in content.lower() or 'peregrino' in content.lower()
                has_planets = any(planet in content.lower() for planet in ['sol', 'lua', 'mercúrio', 'vênus', 'marte'])
                has_practical = any(word in content.lower() for word in ['prático', 'vida', 'comportamento', 'desafio', 'oportunidade'])
                
                print(f"   📊 Análise do conteúdo:")
                print(f"      ✓ Menciona temperamento/elementos: {'Sim' if has_temperament else 'Não'}")
                print(f"      ✓ Menciona dignidades: {'Sim' if has_dignities else 'Não'}")
                print(f"      ✓ Menciona planetas: {'Sim' if has_planets else 'Não'}")
                print(f"      ✓ Tem orientação prática: {'Sim' if has_practical else 'Não'}")
                
                # Mostrar preview do conteúdo
                if content:
                    preview = content[:300] + "..." if len(content) > 300 else content
                    print(f"\n   📄 Preview do conteúdo:")
                    print(f"   {preview}")
                
                results[section] = {
                    "status": "success",
                    "title": result.get('title'),
                    "content_length": content_length,
                    "word_count": len(content.split()),
                    "generated_by": result.get('generated_by'),
                    "duration": duration,
                    "has_temperament": has_temperament,
                    "has_dignities": has_dignities,
                    "has_planets": has_planets,
                    "has_practical": has_practical,
                    "content_preview": preview[:200] if content else ""
                }
                
                analysis["sections_analysis"][section] = {
                    "success": True,
                    "content_length": content_length,
                    "duration": duration,
                    "quality_indicators": {
                        "temperament": has_temperament,
                        "dignities": has_dignities,
                        "planets": has_planets,
                        "practical": has_practical
                    }
                }
            else:
                print(f"❌ ERRO!")
                print(f"   Status: {response.status_code}")
                error_text = response.text[:500]
                print(f"   Resposta: {error_text}")
                
                analysis["failed"] += 1
                results[section] = {
                    "status": "error",
                    "status_code": response.status_code,
                    "error": error_text
                }
                analysis["sections_analysis"][section] = {
                    "success": False,
                    "error": error_text
                }
                
        except requests.exceptions.ConnectionError:
            print(f"❌ ERRO: Não foi possível conectar ao servidor")
            print(f"   Verifique se o backend está rodando em {API_BASE_URL}")
            analysis["failed"] += 1
            results[section] = {
                "status": "connection_error",
                "error": "Servidor não disponível"
            }
            analysis["sections_analysis"][section] = {
                "success": False,
                "error": "Servidor não disponível"
            }
        except requests.exceptions.Timeout:
            print(f"❌ ERRO: Timeout - requisição demorou mais de 2 minutos")
            analysis["failed"] += 1
            results[section] = {
                "status": "timeout",
                "error": "Requisição expirou"
            }
            analysis["sections_analysis"][section] = {
                "success": False,
                "error": "Timeout"
            }
        except Exception as e:
            print(f"❌ ERRO: {str(e)}")
            analysis["failed"] += 1
            results[section] = {
                "status": "exception",
                "error": str(e)
            }
            analysis["sections_analysis"][section] = {
                "success": False,
                "error": str(e)
            }
    
    # Calcular média
    if analysis["successful"] > 0:
        analysis["average_content_length"] = analysis["total_content_length"] // analysis["successful"]
    
    # Resumo final
    print("\n" + "=" * 80)
    print("📊 ANÁLISE COMPLETA DOS RESULTADOS")
    print("=" * 80)
    
    print(f"\n📈 ESTATÍSTICAS GERAIS:")
    print(f"   Total de requisições: {analysis['total_requests']}")
    print(f"   ✅ Sucessos: {analysis['successful']}")
    print(f"   ❌ Falhas: {analysis['failed']}")
    print(f"   Taxa de sucesso: {(analysis['successful']/analysis['total_requests']*100):.1f}%")
    print(f"   Total de caracteres gerados: {analysis['total_content_length']:,}")
    if analysis['successful'] > 0:
        print(f"   Média de caracteres por seção: {analysis['average_content_length']:,}")
    
    print(f"\n📋 ANÁLISE POR SEÇÃO:")
    for section, result in results.items():
        status_icon = "✅" if result.get("status") == "success" else "❌"
        print(f"\n   {status_icon} {section.upper()}:")
        if result.get("status") == "success":
            print(f"      Título: {result.get('title', 'N/A')}")
            print(f"      Tamanho: {result.get('content_length', 0):,} caracteres")
            print(f"      Palavras: ~{result.get('word_count', 0)}")
            print(f"      Tempo: {result.get('duration', 0):.2f}s")
            print(f"      Gerado por: {result.get('generated_by', 'N/A')}")
            print(f"      Indicadores de qualidade:")
            print(f"         • Temperamento: {'✓' if result.get('has_temperament') else '✗'}")
            print(f"         • Dignidades: {'✓' if result.get('has_dignities') else '✗'}")
            print(f"         • Planetas: {'✓' if result.get('has_planets') else '✗'}")
            print(f"         • Prático: {'✓' if result.get('has_practical') else '✗'}")
        else:
            print(f"      Erro: {result.get('error', 'Erro desconhecido')[:100]}")
    
    # Análise de qualidade
    print(f"\n🎯 ANÁLISE DE QUALIDADE:")
    quality_scores = {}
    for section, data in analysis["sections_analysis"].items():
        if data.get("success"):
            indicators = data.get("quality_indicators", {})
            score = sum(1 for v in indicators.values() if v)
            quality_scores[section] = score
            print(f"   {section.upper()}: {score}/4 indicadores de qualidade")
    
    # Verificar se os cálculos estão sendo feitos pela biblioteca
    print(f"\n🔬 VERIFICAÇÃO DE CÁLCULOS:")
    print(f"   ⚠️  IMPORTANTE: Verifique os logs do backend para confirmar que:")
    print(f"      • O mapa astral foi calculado usando Swiss Ephemeris (kerykeion)")
    print(f"      • Os dados foram validados antes de enviar à IA")
    print(f"      • O bloco pré-calculado foi criado corretamente")
    
    # Recomendações
    print(f"\n💡 RECOMENDAÇÕES:")
    if analysis["failed"] > 0:
        print(f"   ⚠️  {analysis['failed']} seção(ões) falharam - verifique os erros acima")
    if analysis["successful"] == analysis["total_requests"]:
        print(f"   ✅ Todas as seções foram geradas com sucesso!")
    
    # Verificar qualidade do conteúdo
    low_quality = [s for s, score in quality_scores.items() if score < 3]
    if low_quality:
        print(f"   ⚠️  Seções com qualidade abaixo do esperado: {', '.join(low_quality)}")
    else:
        print(f"   ✅ Todas as seções têm boa qualidade de conteúdo")
    
    print()
    print("=" * 80)
    
    if analysis["successful"] == analysis["total_requests"]:
        print("🎉 TODOS OS TESTES PASSARAM!")
        return 0
    else:
        print(f"⚠️  {analysis['failed']} TESTE(S) FALHARAM")
        return 1

if __name__ == "__main__":
    try:
        exit_code = test_full_birth_chart_section_detailed()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

