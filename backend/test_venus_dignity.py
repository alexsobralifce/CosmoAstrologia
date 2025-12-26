#!/usr/bin/env python3
"""
Script para testar se a correção do prompt está funcionando.
Testa especificamente se Vênus em Sagitário é mencionado como PEREGRINO (correto)
e não como QUEDA (incorreto).
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_venus_dignity():
    """Testa se a IA menciona corretamente Vênus em Sagitário como PEREGRINO"""
    
    print("=" * 60)
    print("TESTE DE CORREÇÃO - DIGNIDADE DE VÊNUS")
    print("=" * 60)
    
    # Dados do PDF que tinha o problema
    test_data = {
        "name": "Alexandre Rocha",
        "birthDate": "20/10/1981",
        "birthTime": "13:30",
        "birthPlace": "Sobral, Ceará, Brasil",
        "sunSign": "Libra",
        "moonSign": "Leão",
        "ascendant": "Aquário",
        "sunHouse": 1,
        "moonHouse": 1,
        "ascendantHouse": 1,
        "mercurySign": "Libra",
        "venusSign": "Sagitário",
        "marsSign": "Leão",
        "jupiterSign": "Libra",
        "saturnSign": "Libra",
        "uranusSign": "Escorpião",
        "neptuneSign": "Sagitário",
        "plutoSign": "Libra",
        "northNodeSign": "Leão",
        "southNodeSign": "Aquário",
        "section": "personal",  # Seção que analisa Vênus
        "language": "pt"
    }
    
    print("\n1. Fazendo requisição para gerar seção 'personal'...")
    print(f"   URL: {BASE_URL}/api/interpretation/full-birth-chart/section")
    print(f"   Dados: {test_data['name']}, {test_data['birthDate']} {test_data['birthTime']}")
    print(f"   Vênus: {test_data['venusSign']} (deve ser PEREGRINO, não QUEDA)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/interpretation/full-birth-chart/section",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"\n❌ Erro na requisição: {response.status_code}")
            print(f"   Resposta: {response.text[:500]}")
            return False
        
        result = response.json()
        interpretation = result.get('interpretation', '')
        
        print(f"\n2. Analisando resposta...")
        print(f"   Tamanho da interpretação: {len(interpretation)} caracteres")
        
        # Verificar se menciona Vênus
        if 'Vênus' not in interpretation:
            print("   ⚠️  Interpretação não menciona Vênus")
            return False
        
        # Verificar se menciona PEREGRINO (correto)
        venus_peregrine = 'Vênus' in interpretation and 'PEREGRINO' in interpretation
        venus_peregrine_lower = 'Vênus' in interpretation and 'peregrino' in interpretation.lower()
        
        # Verificar se menciona QUEDA (incorreto)
        venus_fall = 'Vênus' in interpretation and 'Queda' in interpretation
        venus_fall_lower = 'Vênus' in interpretation and 'queda' in interpretation.lower()
        
        print("\n3. Verificando dignidade mencionada:")
        
        if venus_peregrine or venus_peregrine_lower:
            print("   ✅ Vênus mencionado como PEREGRINO (CORRETO)")
        else:
            print("   ⚠️  Vênus não mencionado como PEREGRINO explicitamente")
        
        if venus_fall or venus_fall_lower:
            print("   ❌ PROBLEMA: Vênus mencionado como QUEDA (INCORRETO)")
            # Procurar contexto
            lines = interpretation.split('\n')
            for i, line in enumerate(lines):
                if 'Vênus' in line and ('Queda' in line or 'queda' in line.lower()):
                    print(f"   Contexto: {line.strip()}")
                    if i > 0:
                        print(f"   Linha anterior: {lines[i-1].strip()}")
                    if i < len(lines) - 1:
                        print(f"   Linha seguinte: {lines[i+1].strip()}")
            return False
        else:
            print("   ✅ Vênus NÃO mencionado como QUEDA (correto)")
        
        # Mostrar trecho sobre Vênus
        print("\n4. Trecho sobre Vênus na interpretação:")
        lines = interpretation.split('\n')
        venus_context = []
        for i, line in enumerate(lines):
            if 'Vênus' in line:
                # Pegar contexto (2 linhas antes e depois)
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                venus_context = lines[start:end]
                break
        
        if venus_context:
            for line in venus_context:
                print(f"   {line}")
        else:
            print("   (Trecho não encontrado)")
        
        print("\n" + "=" * 60)
        if not (venus_fall or venus_fall_lower):
            print("✅ TESTE PASSOU - Vênus mencionado corretamente!")
            return True
        else:
            print("❌ TESTE FALHOU - Vênus mencionado incorretamente como QUEDA")
            return False
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Erro: Não foi possível conectar ao servidor")
        print("   Certifique-se de que o servidor está rodando em http://localhost:8000")
        return False
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_venus_dignity()
    exit(0 if success else 1)

