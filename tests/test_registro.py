#!/usr/bin/env python3
"""
Script para testar o registro de usuário e verificar se email e senha estão sendo salvos
"""
import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000/api/auth/register"

def test_registro():
    """Testa o registro de um novo usuário"""
    test_email = f"teste_{datetime.now().strftime('%Y%m%d_%H%M%S')}@teste.com"
    test_password = "123456"
    test_name = "Usuário Teste"
    
    data = {
        "email": test_email,
        "password": test_password,
        "name": test_name,
        "birth_data": {
            "name": test_name,
            "birth_date": "1990-01-01T12:00:00",
            "birth_time": "12:00",
            "birth_place": "São Paulo, SP",
            "latitude": -23.5505,
            "longitude": -46.6333
        }
    }
    
    print(f"🧪 Testando registro de: {test_email}")
    print(f"📧 Email: {test_email}")
    print(f"🔑 Senha: {test_password}")
    print(f"👤 Nome: {test_name}")
    print()
    
    try:
        response = requests.post(API_URL, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Registro bem-sucedido!")
            print(f"🎫 Token recebido: {result.get('access_token', 'N/A')[:50]}...")
            
            # Verificar no banco
            from app.models.database import User
            from app.core.database import SessionLocal
            from app.services.astrology_calculator import verify_password
            
            db = SessionLocal()
            user = db.query(User).filter(User.email == test_email).first()
            
            if user:
                print(f"\n📊 Verificação no banco:")
                print(f"   ✅ Email salvo: {user.email}")
                print(f"   {'✅' if user.password_hash else '❌'} Senha salva: {'Sim' if user.password_hash else 'Não'}")
                print(f"   ✅ Nome salvo: {user.name}")
                
                if user.password_hash:
                    # Verificar se a senha está correta
                    import bcrypt
                    is_valid = bcrypt.checkpw(test_password.encode('utf-8'), user.password_hash.encode('utf-8'))
                    print(f"   {'✅' if is_valid else '❌'} Senha válida: {'Sim' if is_valid else 'Não'}")
                else:
                    print("   ⚠️  Senha não foi salva!")
            else:
                print("❌ Usuário não encontrado no banco!")
            
            db.close()
            return True
        else:
            print(f"❌ Erro no registro: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE REGISTRO - Email e Senha")
    print("=" * 60)
    print()
    
    # Verificar se o backend está rodando
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Backend está rodando")
            print()
            test_registro()
        else:
            print("❌ Backend não está respondendo corretamente")
    except Exception as e:
        print(f"❌ Não foi possível conectar ao backend: {str(e)}")
        print("   Certifique-se de que o backend está rodando em http://localhost:8000")

