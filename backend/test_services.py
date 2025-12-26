#!/usr/bin/env python3
"""
Script para testar os serviços (Backend + RAG Service).
Executa testes de integração e verifica se os serviços estão funcionando.

Execute este script a partir do diretório backend:
    cd backend
    python3 test_services.py
"""
import sys
import subprocess
import os
import time
from pathlib import Path
from typing import Tuple, Optional

try:
    import requests
except ImportError:
    print("⚠️  requests não instalado. Instalando...")
    subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
    import requests

# Cores para output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Imprime cabeçalho formatado."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")


def print_success(text: str):
    """Imprime mensagem de sucesso."""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")


def print_error(text: str):
    """Imprime mensagem de erro."""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")


def print_warning(text: str):
    """Imprime mensagem de aviso."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")


def print_info(text: str):
    """Imprime mensagem informativa."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")


def check_service(url: str, name: str, timeout: int = 5) -> Tuple[bool, Optional[str]]:
    """
    Verifica se um serviço está respondendo.
    
    Returns:
        (is_running, message)
    """
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return True, f"{name} está respondendo (status: {response.status_code})"
        else:
            return False, f"{name} respondeu com status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, f"{name} não está acessível em {url}"
    except requests.exceptions.Timeout:
        return False, f"{name} não respondeu em {timeout}s"
    except Exception as e:
        return False, f"Erro ao verificar {name}: {str(e)}"


def test_rag_service() -> bool:
    """Testa o RAG Service."""
    print_header("Testando RAG Service")
    
    # Health check
    print_info("Verificando health check...")
    is_running, message = check_service("http://localhost:8001/health", "RAG Service")
    if is_running:
        print_success(message)
    else:
        print_error(message)
        print_info("💡 Dica: Inicie o RAG service com: docker-compose up rag-service")
        return False
    
    # Status endpoint
    print_info("Verificando endpoint de status...")
    try:
        response = requests.get("http://localhost:8001/api/rag/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {data.get('available', False)}")
            print_info(f"  - Has index: {data.get('has_index', False)}")
            print_info(f"  - Has Groq: {data.get('has_groq', False)}")
            print_info(f"  - Document count: {data.get('document_count', 0)}")
        else:
            print_warning(f"Status endpoint retornou {response.status_code}")
    except Exception as e:
        print_error(f"Erro ao verificar status: {e}")
        return False
    
    # Test search
    print_info("Testando busca de documentos...")
    try:
        response = requests.post(
            "http://localhost:8001/api/rag/search",
            json={"query": "Sol em Libra", "top_k": 3},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            count = data.get("count", 0)
            print_success(f"Busca funcionando: {count} resultados")
        else:
            print_warning(f"Busca retornou {response.status_code}")
    except Exception as e:
        print_error(f"Erro na busca: {e}")
        return False
    
    # Test interpretation
    print_info("Testando interpretação...")
    try:
        response = requests.post(
            "http://localhost:8001/api/rag/interpretation",
            json={"planet": "Sol", "sign": "Libra", "use_groq": False, "top_k": 3},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            interpretation = data.get("interpretation", "")
            if len(interpretation) > 0:
                print_success(f"Interpretação funcionando ({len(interpretation)} chars)")
            else:
                print_warning("Interpretação retornou vazia")
        else:
            print_warning(f"Interpretação retornou {response.status_code}")
    except Exception as e:
        print_error(f"Erro na interpretação: {e}")
        return False
    
    return True


def test_backend() -> bool:
    """Testa o Backend."""
    print_header("Testando Backend")
    
    # Root endpoint
    print_info("Verificando root endpoint...")
    is_running, message = check_service("http://localhost:8000/", "Backend")
    if is_running:
        print_success(message)
    else:
        print_error(message)
        print_info("💡 Dica: Inicie o backend com: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False
    
    # RAG status via backend
    print_info("Verificando status do RAG via backend...")
    try:
        response = requests.get("http://localhost:8000/api/interpretation/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status do RAG via backend: {data.get('available', False)}")
        else:
            print_warning(f"Status endpoint retornou {response.status_code}")
    except Exception as e:
        print_error(f"Erro ao verificar status: {e}")
    
    # Search via backend
    print_info("Testando busca via backend...")
    try:
        response = requests.get(
            "http://localhost:8000/api/interpretation/search",
            params={"query": "Sol em Libra", "top_k": 3},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            count = data.get("count", 0)
            print_success(f"Busca via backend funcionando: {count} resultados")
        else:
            print_warning(f"Busca retornou {response.status_code}")
    except Exception as e:
        print_error(f"Erro na busca: {e}")
    
    # Interpretation via backend
    print_info("Testando interpretação via backend...")
    try:
        response = requests.post(
            "http://localhost:8000/api/interpretation",
            json={"planet": "Sol", "sign": "Libra", "use_groq": False},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            interpretation = data.get("interpretation", "")
            if len(interpretation) > 0:
                print_success(f"Interpretação via backend funcionando ({len(interpretation)} chars)")
            else:
                print_warning("Interpretação retornou vazia")
        elif response.status_code == 503:
            print_warning("Backend retornou 503 - RAG service pode não estar disponível")
        else:
            print_warning(f"Interpretação retornou {response.status_code}")
    except Exception as e:
        print_error(f"Erro na interpretação: {e}")
    
    return True


def test_integration() -> bool:
    """Testa a integração entre backend e RAG service."""
    print_header("Testando Integração Backend ↔ RAG Service")
    
    # Verificar se ambos estão rodando
    rag_running, _ = check_service("http://localhost:8001/health", "RAG Service")
    backend_running, _ = check_service("http://localhost:8000/", "Backend")
    
    if not rag_running:
        print_error("RAG Service não está rodando. Não é possível testar integração.")
        return False
    
    if not backend_running:
        print_error("Backend não está rodando. Não é possível testar integração.")
        return False
    
    print_success("Ambos os serviços estão rodando")
    
    # Testar fluxo completo
    print_info("Testando fluxo completo: Backend → RAG Service → Resposta")
    try:
        # 1. Backend busca no RAG
        response = requests.post(
            "http://localhost:8000/api/interpretation",
            json={
                "planet": "Sol",
                "sign": "Libra",
                "use_groq": False,
                "top_k": 5
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("✅ Fluxo completo funcionando!")
            print_info(f"  - Interpretação: {len(data.get('interpretation', ''))} chars")
            print_info(f"  - Fontes: {len(data.get('sources', []))}")
            print_info(f"  - Gerado por: {data.get('generated_by', 'unknown')}")
            return True
        elif response.status_code == 503:
            print_error("Backend não conseguiu conectar ao RAG service")
            print_info("Verifique se RAG_SERVICE_URL está configurado corretamente")
            return False
        else:
            print_warning(f"Resposta inesperada: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro no fluxo completo: {e}")
        return False


def run_pytest_tests() -> bool:
    """Executa testes pytest de integração."""
    print_header("Executando Testes Pytest")
    
    # Estamos já dentro do backend, então verificar diretório atual
    current_dir = Path(".")
    if not (current_dir / "app").exists():
        print_error("Não estamos no diretório backend correto")
        return False
    
    # Verificar se pytest está instalado
    pytest_available = False
    try:
        result = subprocess.run(
            ["pytest", "--version"], 
            check=True, 
            capture_output=True,
            text=True,
            timeout=5
        )
        print_success(f"pytest encontrado: {result.stdout.strip()}")
        pytest_available = True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print_warning("pytest não encontrado. Tentando instalar...")
        
        # Tentar diferentes métodos de instalação
        install_commands = [
            [sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio", "httpx", "requests"],
            ["pip3", "install", "pytest", "pytest-asyncio", "httpx", "requests"],
            ["pip", "install", "pytest", "pytest-asyncio", "httpx", "requests"],
        ]
        
        installed = False
        for cmd in install_commands:
            try:
                print_info(f"Tentando instalar com: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                print_success(f"pytest instalado com sucesso usando: {cmd[0]}")
                installed = True
                pytest_available = True
                break
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
                continue
        
        if not installed:
            print_error("Não foi possível instalar pytest automaticamente")
            print_warning("Instale manualmente com um dos comandos:")
            print_warning("  python3 -m pip install pytest pytest-asyncio httpx requests")
            print_warning("  pip3 install pytest pytest-asyncio httpx requests")
            print_warning("  pip install pytest pytest-asyncio httpx requests")
            return False
    
    # Configurar variável de ambiente
    env = os.environ.copy()
    env["RAG_SERVICE_URL"] = "http://localhost:8001"
    
    # Verificar se pytest está disponível antes de continuar
    if not pytest_available:
        print_error("pytest não está disponível. Não é possível executar testes.")
        return False
    
    # Verificar se diretório de testes existe
    tests_dir = Path("tests/integration")
    if not tests_dir.exists():
        print_warning("Diretório de testes não encontrado: tests/integration")
        print_info("Os testes de integração ainda não foram criados.")
        print_info("Execute os testes básicos de serviços acima.")
        return False
    
    # Executar testes
    print_info("Executando testes de integração...")
    try:
        result = subprocess.run(
            ["pytest", "tests/integration/", "-v", "--tb=short"],
            cwd=".",
            env=env,
            timeout=300,
            capture_output=False  # Mostrar output em tempo real
        )
        if result.returncode == 0:
            print_success("Todos os testes passaram!")
            return True
        else:
            print_warning(f"Alguns testes falharam (código: {result.returncode})")
            return False
    except subprocess.TimeoutExpired:
        print_error("Testes excederam o tempo limite (5 minutos)")
        return False
    except FileNotFoundError:
        print_error("pytest não encontrado após instalação. Tente instalar manualmente.")
        return False
    except Exception as e:
        print_error(f"Erro ao executar testes: {e}")
        return False


def main():
    """Função principal."""
    import os
    
    print_header("Teste de Serviços - CosmoAstrologia")
    print_info("Verificando se os serviços estão rodando...")
    print()
    
    results = {
        "rag_service": False,
        "backend": False,
        "integration": False,
        "pytest": False
    }
    
    # Testar RAG Service
    results["rag_service"] = test_rag_service()
    
    # Testar Backend
    results["backend"] = test_backend()
    
    # Testar integração
    if results["rag_service"] and results["backend"]:
        results["integration"] = test_integration()
    else:
        print_warning("Pulando teste de integração (serviços não estão rodando)")
    
    # Executar testes pytest (opcional)
    print()
    if results["rag_service"] or results["backend"]:
        response = input("Deseja executar testes pytest de integração? (s/n): ").strip().lower()
        if response == 's':
            results["pytest"] = run_pytest_tests()
        else:
            print_info("Testes pytest pulados")
    else:
        print_warning("Pulando testes pytest (serviços não estão rodando)")
    
    # Resumo final
    print_header("Resumo dos Testes")
    
    for test_name, passed in results.items():
        if passed:
            print_success(f"{test_name.replace('_', ' ').title()}: PASSOU")
        else:
            print_error(f"{test_name.replace('_', ' ').title()}: FALHOU")
    
    # Contar sucessos
    passed_count = sum(results.values())
    total_count = len(results)
    
    print()
    if passed_count == total_count:
        print_success(f"Todos os testes passaram! ({passed_count}/{total_count})")
        return 0
    else:
        print_warning(f"Alguns testes falharam ({passed_count}/{total_count})")
        print_info("Verifique se os serviços estão rodando:")
        print_info("  - RAG Service: docker-compose up rag-service")
        print_info("  - Backend: docker-compose up backend")
        return 1


if __name__ == "__main__":
    import os
    sys.exit(main())

