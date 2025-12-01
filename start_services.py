#!/usr/bin/env python3
"""
Script Python para iniciar todos os serviços (Backend, RAG Service, Frontend).
"""
import sys
import subprocess
import os
import time
import signal
import requests
from pathlib import Path
from typing import List, Optional, Dict

# Cores
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


def check_port(port: int) -> bool:
    """Verifica se uma porta está em uso."""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0


def check_service_health(url: str, timeout: int = 5) -> bool:
    """Verifica se um serviço está respondendo."""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False


def check_docker_compose() -> bool:
    """Verifica se docker-compose está disponível."""
    try:
        subprocess.run(["docker", "compose", "version"], 
                      capture_output=True, check=True)
        return True
    except:
        try:
            subprocess.run(["docker-compose", "--version"], 
                          capture_output=True, check=True)
            return True
        except:
            return False


def start_with_docker() -> bool:
    """Inicia serviços com Docker Compose."""
    print_header("Iniciando Serviços com Docker Compose")
    
    if not Path("docker-compose.yml").exists():
        print_error("docker-compose.yml não encontrado")
        return False
    
    print_info("Iniciando serviços...")
    
    try:
        # Tentar docker compose primeiro
        try:
            subprocess.run(["docker", "compose", "up", "-d"], 
                          check=True, capture_output=True)
        except:
            subprocess.run(["docker-compose", "up", "-d"], 
                          check=True, capture_output=True)
        
        print_success("Serviços iniciados com Docker Compose")
        
        # Aguardar serviços iniciarem
        print_info("Aguardando serviços iniciarem...")
        time.sleep(5)
        
        check_services_status()
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Erro ao iniciar serviços: {e}")
        return False


def start_manually() -> Dict[str, Optional[subprocess.Popen]]:
    """Inicia serviços manualmente."""
    print_header("Iniciando Serviços Manualmente")
    
    processes = {}
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # RAG Service
    if check_port(8001):
        print_warning("RAG Service já está rodando na porta 8001")
        processes["rag"] = None
    else:
        print_info("Iniciando RAG Service na porta 8001...")
        try:
            os.chdir("rag-service")
            log_file = open("../logs/rag-service.log", "w")
            process = subprocess.Popen(
                ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                cwd=os.getcwd()
            )
            os.chdir("..")
            processes["rag"] = process
            print_success(f"RAG Service iniciado (PID: {process.pid})")
        except Exception as e:
            print_error(f"Erro ao iniciar RAG Service: {e}")
            processes["rag"] = None
    
    # Backend
    if check_port(8000):
        print_warning("Backend já está rodando na porta 8000")
        processes["backend"] = None
    else:
        print_info("Iniciando Backend na porta 8000...")
        try:
            os.chdir("backend")
            log_file = open("../logs/backend.log", "w")
            process = subprocess.Popen(
                ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                cwd=os.getcwd()
            )
            os.chdir("..")
            processes["backend"] = process
            print_success(f"Backend iniciado (PID: {process.pid})")
        except Exception as e:
            print_error(f"Erro ao iniciar Backend: {e}")
            processes["backend"] = None
    
    # Frontend
    if check_port(5173):
        print_warning("Frontend já está rodando na porta 5173")
        processes["frontend"] = None
    else:
        print_info("Iniciando Frontend na porta 5173...")
        if Path("package.json").exists():
            try:
                log_file = open("logs/frontend.log", "w")
                process = subprocess.Popen(
                    ["npm", "run", "dev"],
                    stdout=log_file,
                    stderr=subprocess.STDOUT
                )
                processes["frontend"] = process
                print_success(f"Frontend iniciado (PID: {process.pid})")
            except Exception as e:
                print_error(f"Erro ao iniciar Frontend: {e}")
                processes["frontend"] = None
        else:
            print_warning("Frontend não encontrado (package.json não existe)")
            processes["frontend"] = None
    
    # Aguardar serviços iniciarem
    print_info("Aguardando serviços iniciarem...")
    time.sleep(3)
    
    check_services_status()
    return processes


def check_services_status():
    """Verifica status dos serviços."""
    print_header("Status dos Serviços")
    
    # RAG Service
    if check_port(8001):
        if check_service_health("http://localhost:8001/health"):
            print_success("RAG Service: Rodando em http://localhost:8001")
        else:
            print_warning("RAG Service: Porta 8001 em uso mas não responde")
    else:
        print_error("RAG Service: Não está rodando")
    
    # Backend
    if check_port(8000):
        if check_service_health("http://localhost:8000/"):
            print_success("Backend: Rodando em http://localhost:8000")
        else:
            print_warning("Backend: Porta 8000 em uso mas não responde")
    else:
        print_error("Backend: Não está rodando")
    
    # Frontend
    if check_port(5173):
        print_success("Frontend: Rodando em http://localhost:5173")
    else:
        print_warning("Frontend: Não está rodando")


def stop_services(processes: Optional[Dict] = None):
    """Para os serviços."""
    print_header("Parando Serviços")
    
    # Tentar parar com Docker Compose primeiro
    if Path("docker-compose.yml").exists() and check_docker_compose():
        print_info("Parando serviços com Docker Compose...")
        try:
            subprocess.run(["docker", "compose", "down"], 
                          capture_output=True, check=True)
        except:
            subprocess.run(["docker-compose", "down"], 
                          capture_output=True, check=True)
        print_success("Serviços parados")
        return
    
    # Parar processos manualmente
    if processes:
        for name, process in processes.items():
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    print_success(f"{name.title()} parado (PID: {process.pid})")
                except:
                    process.kill()
                    print_warning(f"{name.title()} forçado a parar (PID: {process.pid})")
    
    # Parar processos nas portas
    import socket
    for port in [8001, 8000, 5173]:
        if check_port(port):
            print_warning(f"Porta {port} ainda em uso. Você pode precisar parar manualmente.")


def show_logs(service: str):
    """Mostra logs de um serviço."""
    if not service:
        print_error("Especifique o serviço: rag-service, backend ou frontend")
        return
    
    log_file = Path(f"logs/{service}.log")
    
    if Path("docker-compose.yml").exists() and check_docker_compose():
        print_info(f"Mostrando logs do {service} (Docker Compose)...")
        try:
            subprocess.run(["docker", "compose", "logs", "-f", service])
        except:
            subprocess.run(["docker-compose", "logs", "-f", service])
    elif log_file.exists():
        print_info(f"Mostrando logs do {service}...")
        try:
            subprocess.run(["tail", "-f", str(log_file)])
        except KeyboardInterrupt:
            pass
    else:
        print_error(f"Logs não encontrados para {service}")


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gerenciar serviços do CosmoAstrologia")
    parser.add_argument("command", nargs="?", default="start",
                       choices=["start", "stop", "restart", "status", "logs"],
                       help="Comando a executar")
    parser.add_argument("--service", help="Serviço para logs (rag-service, backend, frontend)")
    parser.add_argument("--no-docker", action="store_true", 
                       help="Não usar Docker Compose mesmo se disponível")
    
    args = parser.parse_args()
    
    processes = {}
    
    if args.command == "start":
        print_header("Iniciando Serviços - CosmoAstrologia")
        
        use_docker = not args.no_docker and check_docker_compose() and Path("docker-compose.yml").exists()
        
        if use_docker:
            response = input("Usar Docker Compose? (s/n) [s]: ").strip().lower()
            use_docker = response != "n"
        
        if use_docker:
            start_with_docker()
        else:
            processes = start_manually()
        
        print()
        print_success("Serviços iniciados!")
        print_info("URLs:")
        print_info("  - RAG Service: http://localhost:8001")
        print_info("  - Backend: http://localhost:8000")
        print_info("  - Frontend: http://localhost:5173")
        
        # Salvar PIDs para poder parar depois
        if processes:
            import json
            pids = {k: v.pid for k, v in processes.items() if v}
            Path("logs/pids.json").write_text(json.dumps(pids))
    
    elif args.command == "stop":
        # Carregar PIDs se existirem
        pids_file = Path("logs/pids.json")
        if pids_file.exists():
            import json
            pids = json.loads(pids_file.read_text())
            processes = {k: subprocess.Popen([], pid=v) for k, v in pids.items()}
        stop_services(processes)
    
    elif args.command == "restart":
        stop_services(processes)
        time.sleep(2)
        main()
    
    elif args.command == "status":
        check_services_status()
    
    elif args.command == "logs":
        show_logs(args.service or "")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário")
        sys.exit(0)

