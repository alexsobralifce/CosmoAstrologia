#!/usr/bin/env python3
"""
Script para testar a atualização de usuário
"""
import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000/api/auth"
TEST_EMAIL = "alexandre@bol.com"
TEST_PASSWORD = "123456"

def test_update():
    """Testa a atualização de dados do usuário"""
    print("=" * 60)
    print("TESTE DE ATUALIZAÇÃO DE USUÁRIO")
    print("=" * 60)
    print()
    
    # 1. Fazer login
    print("1️⃣ Fazendo login...")
    login_response = requests.post(
        f"{API_URL}/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Erro no login: {login_response.status_code}")
        print(f"   {login_response.text}")
        return False
    
    token = login_response.json()["access_token"]
    print(f"✅ Login bem-sucedido! Token: {token[:50]}...")
    print()
    
    # 2. Buscar dados atuais
    print("2️⃣ Buscando dados atuais...")
    headers = {"Authorization": f"Bearer {token}"}
    current_user = requests.get(f"{API_URL}/me", headers=headers)
    current_chart = requests.get(f"{API_URL}/birth-chart", headers=headers)
    
    if current_user.status_code == 200:
        user_data = current_user.json()
        print(f"   Email: {user_data.get('email')}")
        print(f"   Nome: {user_data.get('name')}")
    
    if current_chart.status_code == 200:
        chart_data = current_chart.json()
        print(f"   Data: {chart_data.get('birth_date')}")
        print(f"   Hora: {chart_data.get('birth_time')}")
        print(f"   Local: {chart_data.get('birth_place')}")
    print()
    
    # 3. Atualizar dados
    print("3️⃣ Atualizando dados...")
    update_data = {
        "name": "FRANCISCO ALEXANDRE ARAUJO ROCHA",
        "email": TEST_EMAIL,
        "birth_data": {
            "name": "FRANCISCO ALEXANDRE ARAUJO ROCHA",
            "birth_date": "1990-01-15T00:00:00",
            "birth_time": "14:30",
            "birth_place": "Sobral, CE, Brasil",
            "latitude": -3.6879,
            "longitude": -40.3456
        }
    }
    
    update_response = requests.put(
        f"{API_URL}/me",
        headers=headers,
        json=update_data
    )
    
    if update_response.status_code == 200:
        print("✅ Atualização bem-sucedida!")
        print(f"   Resposta: {update_response.json()}")
    else:
        print(f"❌ Erro na atualização: {update_response.status_code}")
        print(f"   {update_response.text}")
        return False
    print()
    
    # 4. Verificar dados atualizados
    print("4️⃣ Verificando dados atualizados...")
    updated_user = requests.get(f"{API_URL}/me", headers=headers)
    updated_chart = requests.get(f"{API_URL}/birth-chart", headers=headers)
    
    if updated_user.status_code == 200:
        user_data = updated_user.json()
        print(f"   Email: {user_data.get('email')}")
        print(f"   Nome: {user_data.get('name')}")
    
    if updated_chart.status_code == 200:
        chart_data = updated_chart.json()
        print(f"   Data: {chart_data.get('birth_date')}")
        print(f"   Hora: {chart_data.get('birth_time')}")
        print(f"   Local: {chart_data.get('birth_place')}")
        print(f"   Signos: Sol={chart_data.get('sun_sign')}, Lua={chart_data.get('moon_sign')}, Asc={chart_data.get('ascendant_sign')}")
    
    print()
    print("✅ Teste concluído!")
    return True

if __name__ == "__main__":
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            test_update()
        else:
            print("❌ Backend não está respondendo corretamente")
    except Exception as e:
        print(f"❌ Não foi possível conectar ao backend: {str(e)}")
        print("   Certifique-se de que o backend está rodando em http://localhost:8000")

