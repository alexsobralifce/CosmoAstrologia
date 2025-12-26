#!/usr/bin/env python3
"""
Teste da estrutura do prompt melhorado de numerologia.
Verifica se as melhorias foram aplicadas corretamente.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import re
from datetime import datetime

# Ler o arquivo de interpretação para verificar o prompt
interpretation_file = os.path.join(os.path.dirname(__file__), '..', 'backend', 'app', 'api', 'interpretation.py')

print("=" * 80)
print("TESTE DA ESTRUTURA DO PROMPT NUMEROLÓGICO MELHORADO")
print("=" * 80)

with open(interpretation_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Verificações
checks = {
    "Prompt narrativo": False,
    "História de vida": False,
    "Mínimo 2000 palavras": False,
    "Modelo 70b": False,
    "Max tokens 8000": False,
    "Parágrafos mínimos": False,
    "Exemplos práticos": False,
    "Conectar números": False
}

# 1. Verificar se menciona narrativa/história
if "narrativa" in content.lower() or "história de vida" in content.lower() or "contar a história" in content.lower():
    checks["Prompt narrativo"] = True
    print("✓ Prompt menciona narrativa/história de vida")

# 2. Verificar se menciona contar história
if "contar a história" in content.lower() or "conte a história" in content.lower():
    checks["História de vida"] = True
    print("✓ Instruções para contar história de vida")

# 3. Verificar mínimo de palavras
if "2000 palavras" in content or "mínimo 2000" in content.lower():
    checks["Mínimo 2000 palavras"] = True
    print("✓ Mínimo de 2000 palavras especificado")

# 4. Verificar modelo
if "llama-3.1-70b-versatile" in content:
    checks["Modelo 70b"] = True
    print("✓ Modelo atualizado para llama-3.1-70b-versatile")

# 5. Verificar max_tokens
if "max_tokens=8000" in content or "max_tokens= 8000" in content:
    checks["Max tokens 8000"] = True
    print("✓ Max tokens aumentado para 8000")

# 6. Verificar parágrafos mínimos
if "MÍNIMO" in content and ("parágrafo" in content.lower() or "paragraph" in content.lower()):
    checks["Parágrafos mínimos"] = True
    print("✓ Parágrafos mínimos especificados para cada seção")

# 7. Verificar exemplos práticos
if "exemplos práticos" in content.lower() or "exemplos concretos" in content.lower() or "dê exemplos" in content.lower():
    checks["Exemplos práticos"] = True
    print("✓ Instruções para dar exemplos práticos")

# 8. Verificar conectar números
if "conecte" in content.lower() and "números" in content.lower() or "narrativa coesa" in content.lower():
    checks["Conectar números"] = True
    print("✓ Instruções para conectar números em narrativa")

# Verificar seções detalhadas
sections = [
    "PARTE 1: A ESSÊNCIA",
    "PARTE 2: VIRTUDES, DEFEITOS E PADRÕES",
    "PARTE 3: O MAPA DA JORNADA",
    "PARTE 4: PREVISÃO E MOMENTO ATUAL"
]

print("\n" + "=" * 80)
print("VERIFICAÇÃO DAS SEÇÕES DETALHADAS")
print("=" * 80)

for section in sections:
    if section in content:
        # Contar quantas subseções tem
        section_start = content.find(section)
        if section_start != -1:
            # Procurar próxima seção ou fim
            next_section = len(content)
            for other_section in sections:
                other_pos = content.find(other_section, section_start + 1)
                if other_pos != -1 and other_pos < next_section:
                    next_section = other_pos
            
            section_text = content[section_start:next_section]
            # Contar subseções numeradas
            subsections = len(re.findall(r'\d+\.\s+\*\*', section_text))
            print(f"✓ {section}: {subsections} subseções encontradas")
        else:
            print(f"✗ {section}: Não encontrada")
    else:
        print(f"✗ {section}: Não encontrada")

# Resumo final
print("\n" + "=" * 80)
print("RESUMO DAS VERIFICAÇÕES")
print("=" * 80)

total_checks = len(checks)
passed_checks = sum(checks.values())

for check, passed in checks.items():
    status = "✓" if passed else "✗"
    print(f"{status} {check}")

print(f"\nTotal: {passed_checks}/{total_checks} verificações passaram")

if passed_checks == total_checks:
    print("\n✅ TODAS AS MELHORIAS FORAM APLICADAS COM SUCESSO!")
else:
    print(f"\n⚠️ {total_checks - passed_checks} melhorias ainda precisam ser verificadas")

print("=" * 80)

