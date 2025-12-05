#!/usr/bin/env python3
"""
Script para testar o novo prompt com dados fictícios.
Verifica se o prompt está seguindo as regras de não fazer cálculos.
"""

import json
import requests
from datetime import datetime

# Dados fictícios de uma pessoa
test_data = {
    "name": "Maria Silva",
    "birthDate": "15/08/1990",
    "birthTime": "14:30",
    "birthPlace": "São Paulo, Brasil",
    
    # Dados principais
    "sunSign": "Leão",
    "moonSign": "Câncer",
    "ascendant": "Áries",
    "sunHouse": 10,
    "moonHouse": 4,
    
    # Planetas pessoais
    "mercurySign": "Leão",
    "mercuryHouse": 10,
    "venusSign": "Virgem",
    "venusHouse": 11,
    "marsSign": "Escorpião",
    "marsHouse": 1,
    
    # Planetas sociais
    "jupiterSign": "Câncer",
    "jupiterHouse": 4,
    "saturnSign": "Capricórnio",
    "saturnHouse": 6,
    
    # Planetas geracionais
    "uranusSign": "Capricórnio",
    "uranusHouse": 6,
    "neptuneSign": "Capricórnio",
    "neptuneHouse": 6,
    "plutoSign": "Escorpião",
    "plutoHouse": 1,
    
    # Nodos Lunares
    "northNodeSign": "Áries",
    "northNodeHouse": 1,
    "southNodeSign": "Libra",
    "southNodeHouse": 7,
    
    # Quíron
    "chironSign": "Câncer",
    "chironHouse": 4,
    
    # Meio do Céu
    "midheavenSign": "Capricórnio",
    "icSign": "Câncer",
    
    "language": "pt"
}

# URL da API (assumindo que está rodando localmente)
API_URL = "http://localhost:8000/api/full-birth-chart/section"

def test_prompt():
    """Testa o prompt com dados fictícios."""
    print("=" * 80)
    print("TESTE DO PROMPT - VERIFICAÇÃO DE PRECISÃO")
    print("=" * 80)
    print(f"\n📋 Dados da pessoa fictícia:")
    print(f"   Nome: {test_data['name']}")
    print(f"   Data: {test_data['birthDate']} às {test_data['birthTime']}")
    print(f"   Local: {test_data['birthPlace']}")
    print(f"   Sol: {test_data['sunSign']} (Casa {test_data['sunHouse']})")
    print(f"   Lua: {test_data['moonSign']} (Casa {test_data['moonHouse']})")
    print(f"   Ascendente: {test_data['ascendant']}")
    print("\n" + "=" * 80)
    
    # Testar apenas uma seção primeiro (power - Estrutura de Poder)
    test_data["section"] = "power"
    
    print(f"\n🧪 Testando seção: {test_data['section']}")
    print(f"   Endpoint: {API_URL}")
    print("\n" + "-" * 80)
    
    try:
        response = requests.post(
            API_URL,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minutos de timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ RESPOSTA RECEBIDA COM SUCESSO!")
            print("\n" + "=" * 80)
            print("📊 ANÁLISE DA RESPOSTA:")
            print("=" * 80)
            
            # Verificar se a resposta contém o conteúdo
            if "content" in result:
                content = result["content"]
                print(f"\n📝 Tamanho da resposta: {len(content)} caracteres")
                print(f"📝 Título: {result.get('title', 'N/A')}")
                print(f"📝 Seção: {result.get('section', 'N/A')}")
                print(f"📝 Gerado por: {result.get('generated_by', 'N/A')}")
                
                # Verificar se há menções a cálculos (indicadores de erro)
                print("\n" + "-" * 80)
                print("🔍 VERIFICAÇÃO DE CONFORMIDADE COM O PROMPT:")
                print("-" * 80)
                
                # Palavras-chave que indicam que o modelo pode estar calculando
                forbidden_keywords = [
                    "calculei",
                    "calcule",
                    "calculando",
                    "vou calcular",
                    "preciso calcular",
                    "devo calcular",
                    "vou verificar a distância",
                    "vou medir",
                    "vou determinar",
                    "vou descobrir",
                    "vou encontrar",
                ]
                
                # Palavras-chave que indicam uso correto dos dados pré-calculados
                correct_keywords = [
                    "Kerykeion",
                    "Swiss Ephemeris",
                    "dados pré-calculados",
                    "bloco pré-calculado",
                    "já foram calculados",
                    "fornecido",
                    "dados fornecidos",
                ]
                
                content_lower = content.lower()
                
                # Verificar palavras proibidas
                found_forbidden = []
                for keyword in forbidden_keywords:
                    if keyword.lower() in content_lower:
                        found_forbidden.append(keyword)
                
                # Verificar palavras corretas
                found_correct = []
                for keyword in correct_keywords:
                    if keyword.lower() in content_lower:
                        found_correct.append(keyword)
                
                # Resultado da verificação
                print(f"\n❌ Palavras proibidas encontradas: {len(found_forbidden)}")
                if found_forbidden:
                    print("   ⚠️  ATENÇÃO: Possíveis tentativas de cálculo detectadas!")
                    for word in found_forbidden:
                        print(f"      - '{word}'")
                else:
                    print("   ✅ Nenhuma palavra proibida encontrada!")
                
                print(f"\n✅ Palavras corretas encontradas: {len(found_correct)}")
                if found_correct:
                    print("   ✅ Boa referência aos dados pré-calculados!")
                    for word in found_correct:
                        print(f"      - '{word}'")
                
                # Verificar se menciona dados específicos do mapa
                print("\n" + "-" * 80)
                print("📋 VERIFICAÇÃO DE USO DOS DADOS DO MAPA:")
                print("-" * 80)
                
                expected_data = [
                    ("Sol", "Leão"),
                    ("Lua", "Câncer"),
                    ("Ascendente", "Áries"),
                    ("Sol", "Casa 10"),
                    ("Lua", "Casa 4"),
                ]
                
                found_data = []
                for planet, sign in expected_data:
                    if planet in content and sign in content:
                        found_data.append(f"{planet} em {sign}")
                
                print(f"\n✅ Dados do mapa mencionados corretamente: {len(found_data)}/{len(expected_data)}")
                for data in found_data:
                    print(f"   ✅ {data}")
                
                # Mostrar preview da resposta
                print("\n" + "=" * 80)
                print("📄 PREVIEW DA RESPOSTA (primeiros 500 caracteres):")
                print("=" * 80)
                print(content[:500] + "..." if len(content) > 500 else content)
                
                # Salvar resposta completa em arquivo
                output_file = f"test_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"\n💾 Resposta completa salva em: {output_file}")
                
            else:
                print("\n❌ Resposta não contém 'content'")
                print(f"Resposta completa: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
        else:
            print(f"\n❌ ERRO: Status code {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar à API.")
        print("   Certifique-se de que o servidor está rodando em http://localhost:8000")
        print("\n   Para iniciar o servidor, execute:")
        print("   cd backend && uvicorn app.main:app --reload")
    except requests.exceptions.Timeout:
        print("\n❌ ERRO: Timeout - a requisição demorou mais de 2 minutos")
    except Exception as e:
        print(f"\n❌ ERRO: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_prompt()

