#!/usr/bin/env python3
"""
Script para testar o fluxo completo de atualização de dados do usuário.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_update_flow():
    print("=" * 60)
    print("TESTE DE FLUXO DE ATUALIZAÇÃO")
    print("=" * 60)
    
    # 1. Login
    print("\n1. Fazendo login...")
    login_data = {
        "email": "alexandre@bol.com",
        "password": "123456"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"✗ Erro no login: {response.status_code}")
        print(response.text)
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ Login realizado com sucesso")
    
    # 2. Buscar dados atuais
    print("\n2. Buscando dados atuais do usuário...")
    response = requests.get(f"{BASE_URL}/api/auth/birth-chart", headers=headers)
    if response.status_code != 200:
        print(f"✗ Erro ao buscar dados: {response.status_code}")
        print(response.text)
        return
    
    current_data = response.json()
    print(f"✓ Dados atuais:")
    print(f"  Nome: {current_data['name']}")
    print(f"  Data: {current_data['birth_date']}")
    print(f"  Hora: {current_data['birth_time']}")
    print(f"  Local: {current_data['birth_place']}")
    print(f"  Sol: {current_data['sun_sign']} {current_data.get('sun_degree', 0):.2f}°")
    print(f"  Lua: {current_data['moon_sign']} {current_data.get('moon_degree', 0):.2f}°")
    print(f"  Ascendente: {current_data['ascendant_sign']} {current_data.get('ascendant_degree', 0):.2f}°")
    
    # 3. Atualizar dados (alterar hora para testar recálculo)
    print("\n3. Atualizando dados (alterando hora de nascimento)...")
    
    # Alterar hora para uma que resulte em Ascendente em Aquário
    new_time = "09:30"  # Hora que resulta em Aquário para a data 20/10/1981
    
    update_data = {
        "name": current_data["name"],
        "birth_data": {
            "name": current_data["name"],
            "birth_date": current_data["birth_date"],
            "birth_time": new_time,  # Nova hora
            "birth_place": current_data["birth_place"],
            "latitude": current_data["latitude"],
            "longitude": current_data["longitude"],
        }
    }
    
    response = requests.put(f"{BASE_URL}/api/auth/me", headers=headers, json=update_data)
    if response.status_code != 200:
        print(f"✗ Erro ao atualizar: {response.status_code}")
        print(response.text)
        return
    
    print(f"✓ Dados atualizados (hora alterada para {new_time})")
    
    # 4. Buscar dados atualizados
    print("\n4. Buscando dados atualizados...")
    response = requests.get(f"{BASE_URL}/api/auth/birth-chart", headers=headers)
    if response.status_code != 200:
        print(f"✗ Erro ao buscar dados atualizados: {response.status_code}")
        print(response.text)
        return
    
    updated_data = response.json()
    print(f"✓ Dados atualizados:")
    print(f"  Nome: {updated_data['name']}")
    print(f"  Data: {updated_data['birth_date']}")
    print(f"  Hora: {updated_data['birth_time']}")
    print(f"  Local: {updated_data['birth_place']}")
    print(f"  Sol: {updated_data['sun_sign']} {updated_data.get('sun_degree', 0):.2f}°")
    print(f"  Lua: {updated_data['moon_sign']} {updated_data.get('moon_degree', 0):.2f}°")
    print(f"  Ascendente: {updated_data['ascendant_sign']} {updated_data.get('ascendant_degree', 0):.2f}°")
    
    # 5. Verificar se os signos mudaram
    print("\n5. Verificando mudanças...")
    print("-" * 60)
    
    if current_data['birth_time'] != updated_data['birth_time']:
        print(f"✓ Hora atualizada: {current_data['birth_time']} → {updated_data['birth_time']}")
    else:
        print(f"✗ Hora não foi atualizada")
    
    if current_data['ascendant_sign'] != updated_data['ascendant_sign']:
        print(f"✓ Ascendente mudou: {current_data['ascendant_sign']} → {updated_data['ascendant_sign']}")
    else:
        print(f"✗ Ascendente não mudou: {current_data['ascendant_sign']}")
        print(f"  (Esperado que mude ao alterar a hora)")
    
    if current_data['sun_sign'] != updated_data['sun_sign']:
        print(f"⚠ Sol mudou: {current_data['sun_sign']} → {updated_data['sun_sign']}")
    else:
        print(f"✓ Sol permaneceu: {current_data['sun_sign']}")
    
    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_update_flow()
    except requests.exceptions.ConnectionError:
        print("✗ Erro: Não foi possível conectar ao backend.")
        print("  Certifique-se de que o backend está rodando em http://localhost:8000")
    except Exception as e:
        print(f"✗ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

