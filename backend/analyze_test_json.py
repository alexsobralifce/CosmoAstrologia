#!/usr/bin/env python3
"""
Script para analisar o JSON gerado e verificar consistência das informações.
"""

import json
import re
from collections import defaultdict

def extract_temperament_from_text(text):
    """Extrai valores de temperamento do texto."""
    patterns = [
        r'Fogo[:\s]+(\d+)\s*ponto',
        r'Fire[:\s]+(\d+)\s*point',
        r'Terra[:\s]+(\d+)\s*ponto',
        r'Earth[:\s]+(\d+)\s*point',
        r'Ar[:\s]+(\d+)\s*ponto',
        r'Air[:\s]+(\d+)\s*point',
        r'Água[:\s]+(\d+)\s*ponto',
        r'Water[:\s]+(\d+)\s*point',
    ]
    
    result = {}
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            element = pattern.split('[')[0]
            result[element] = int(matches[0])
    
    return result

def extract_dignities_from_text(text):
    """Extrai dignidades mencionadas no texto."""
    dignities = {}
    
    # Padrão: "Planeta em Signo: DIGNIDADE" ou "Planeta em Signo está em DIGNIDADE"
    pattern = r'(\w+)\s+em\s+(\w+).*?(?:PEREGRINO|DOMICÍLIO|EXALTAÇÃO|QUEDA|DETRIMENTO|peregrino|domicílio|exaltação|queda|detrimento)'
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    for match in matches:
        planet = match[0]
        sign = match[1]
        # Procurar a dignidade
        dignity_pattern = r'(?:PEREGRINO|DOMICÍLIO|EXALTAÇÃO|QUEDA|DETRIMENTO|peregrino|domicílio|exaltação|queda|detrimento)'
        dignity_match = re.search(dignity_pattern, text[text.find(match[0]):text.find(match[0])+200], re.IGNORECASE)
        if dignity_match:
            dignities[f"{planet} em {sign}"] = dignity_match.group(0).upper()
    
    return dignities

def find_precomputed_block(text):
    """Encontra o bloco pré-calculado no texto."""
    start = text.find("🔒 DADOS PRÉ-CALCULADOS")
    if start == -1:
        start = text.find("PRE-COMPUTED DATA")
    
    if start == -1:
        return None
    
    # Pegar próximo bloco de 2000 caracteres
    block = text[start:start+2000]
    return block

def extract_precomputed_temperament(block):
    """Extrai temperamento do bloco pré-calculado."""
    if not block:
        return None
    
    result = {}
    
    # Procurar padrões
    patterns = {
        'Fogo': r'Fogo[:\s]+(\d+)\s*ponto',
        'Terra': r'Terra[:\s]+(\d+)\s*ponto',
        'Ar': r'Ar[:\s]+(\d+)\s*ponto',
        'Água': r'Água[:\s]+(\d+)\s*ponto',
    }
    
    for element, pattern in patterns.items():
        match = re.search(pattern, block, re.IGNORECASE)
        if match:
            result[element] = int(match.group(1))
    
    # Procurar elemento dominante
    dominant_match = re.search(r'ELEMENTO DOMINANTE[:\s]+(\w+)', block, re.IGNORECASE)
    if dominant_match:
        result['dominant'] = dominant_match.group(1)
    
    return result

def extract_precomputed_dignities(block):
    """Extrai dignidades do bloco pré-calculado."""
    if not block:
        return {}
    
    dignities = {}
    
    # Padrão: "• Planeta em Signo: DIGNIDADE"
    pattern = r'•\s*(\w+)\s+em\s+(\w+)[:\s]+(PEREGRINO|DOMICÍLIO|EXALTAÇÃO|QUEDA|DETRIMENTO)'
    matches = re.findall(pattern, block, re.IGNORECASE)
    
    for match in matches:
        planet = match[0]
        sign = match[1]
        dignity = match[2].upper()
        key = f"{planet} em {sign}"
        dignities[key] = dignity
    
    return dignities

def analyze_json(file_path):
    """Analisa o JSON e verifica consistência."""
    print("=" * 80)
    print("🔍 ANÁLISE DO JSON GERADO")
    print("=" * 80)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    sections = data.get('sections', [])
    
    print(f"\n📋 Total de seções: {len(sections)}")
    print(f"📅 Gerado em: {data.get('generated_at', 'N/A')}")
    
    # 1. Verificar temperamento em cada seção
    print("\n" + "=" * 80)
    print("1️⃣ VERIFICAÇÃO DE TEMPERAMENTO")
    print("=" * 80)
    
    temperament_by_section = {}
    precomputed_temperament = None
    
    for section in sections:
        section_name = section.get('section', 'unknown')
        content = section.get('content', '')
        
        # Encontrar bloco pré-calculado
        block = find_precomputed_block(content)
        if block and not precomputed_temperament:
            precomputed_temperament = extract_precomputed_temperament(block)
            print(f"\n📊 Temperamento do bloco pré-calculado:")
            if precomputed_temperament:
                for element, points in precomputed_temperament.items():
                    if element != 'dominant':
                        print(f"  • {element}: {points} pontos")
                if 'dominant' in precomputed_temperament:
                    print(f"  • ELEMENTO DOMINANTE: {precomputed_temperament['dominant']}")
        
        # Extrair temperamento do texto
        text_temperament = extract_temperament_from_text(content)
        if text_temperament:
            temperament_by_section[section_name] = text_temperament
            print(f"\n📝 Seção '{section_name}':")
            for element, points in text_temperament.items():
                print(f"  • {element}: {points} pontos")
    
    # Verificar consistência
    if len(temperament_by_section) > 1:
        print("\n🔍 Verificando consistência...")
        first = list(temperament_by_section.values())[0]
        all_consistent = all(
            temp == first 
            for temp in temperament_by_section.values()
        )
        
        if all_consistent:
            print("✅ Temperamento CONSISTENTE entre todas as seções!")
        else:
            print("❌ Temperamento INCONSISTENTE entre seções!")
            print("\nDiferenças encontradas:")
            for section_name, temp in temperament_by_section.items():
                if temp != first:
                    print(f"  • {section_name}: {temp} (diferente do primeiro)")
    
    # Comparar com bloco pré-calculado
    if precomputed_temperament:
        print("\n🔍 Comparando com bloco pré-calculado...")
        precomputed_points = {k: v for k, v in precomputed_temperament.items() if k != 'dominant'}
        
        for section_name, text_temp in temperament_by_section.items():
            if text_temp != precomputed_points:
                print(f"❌ Seção '{section_name}' NÃO corresponde ao bloco pré-calculado!")
                print(f"   Bloco: {precomputed_points}")
                print(f"   Texto: {text_temp}")
            else:
                print(f"✅ Seção '{section_name}' corresponde ao bloco pré-calculado")
    
    # 2. Verificar dignidades
    print("\n" + "=" * 80)
    print("2️⃣ VERIFICAÇÃO DE DIGNIDADES")
    print("=" * 80)
    
    precomputed_dignities = {}
    dignities_by_section = {}
    
    for section in sections:
        section_name = section.get('section', 'unknown')
        content = section.get('content', '')
        
        # Encontrar bloco pré-calculado
        block = find_precomputed_block(content)
        if block and not precomputed_dignities:
            precomputed_dignities = extract_precomputed_dignities(block)
            print(f"\n📊 Dignidades do bloco pré-calculado:")
            for key, dignity in list(precomputed_dignities.items())[:5]:
                print(f"  • {key}: {dignity}")
            if len(precomputed_dignities) > 5:
                print(f"  ... e mais {len(precomputed_dignities) - 5}")
        
        # Extrair dignidades do texto
        text_dignities = extract_dignities_from_text(content)
        if text_dignities:
            dignities_by_section[section_name] = text_dignities
    
    # Comparar com bloco pré-calculado
    if precomputed_dignities:
        print("\n🔍 Verificando dignidades mencionadas no texto...")
        for section_name, text_digs in dignities_by_section.items():
            print(f"\n📝 Seção '{section_name}':")
            for key, dignity in text_digs.items():
                if key in precomputed_dignities:
                    if dignity == precomputed_dignities[key]:
                        print(f"  ✅ {key}: {dignity} (correto)")
                    else:
                        print(f"  ❌ {key}: {dignity} (esperado: {precomputed_dignities[key]})")
                else:
                    print(f"  ⚠️  {key}: {dignity} (não encontrado no bloco)")
    
    # 3. Verificar erros conhecidos
    print("\n" + "=" * 80)
    print("3️⃣ VERIFICAÇÃO DE ERROS CONHECIDOS")
    print("=" * 80)
    
    errors_found = []
    
    for section in sections:
        section_name = section.get('section', 'unknown')
        content = section.get('content', '')
        
        # Erro 1: Sol em Virgem em Domicílio
        if re.search(r'Sol.*Virgem.*(?:DOMICÍLIO|Domicílio|domicílio)', content, re.IGNORECASE):
            errors_found.append(f"❌ {section_name}: Menciona 'Sol em Virgem em Domicílio' (deveria ser PEREGRINO)")
        
        # Erro 2: Temperamento inconsistente (já verificado acima)
        # Erro 3: Dignidades inventadas (já verificado acima)
    
    if errors_found:
        print("\n❌ Erros encontrados:")
        for error in errors_found:
            print(f"  {error}")
    else:
        print("\n✅ Nenhum erro conhecido encontrado!")
    
    # Resumo
    print("\n" + "=" * 80)
    print("📊 RESUMO")
    print("=" * 80)
    print(f"Total de seções: {len(sections)}")
    print(f"Seções com temperamento: {len(temperament_by_section)}")
    print(f"Seções com dignidades: {len(dignities_by_section)}")
    print(f"Temperamento pré-calculado encontrado: {'Sim' if precomputed_temperament else 'Não'}")
    print(f"Dignidades pré-calculadas encontradas: {'Sim' if precomputed_dignities else 'Não'}")
    print(f"Erros encontrados: {len(errors_found)}")
    
    return {
        'sections_count': len(sections),
        'temperament_consistent': all_consistent if len(temperament_by_section) > 1 else None,
        'errors_count': len(errors_found),
        'precomputed_found': bool(precomputed_temperament and precomputed_dignities)
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Procurar arquivo mais recente
        import glob
        files = glob.glob("test_birth_chart_*.json")
        if files:
            file_path = max(files, key=lambda f: os.path.getmtime(f))
        else:
            print("❌ Nenhum arquivo JSON encontrado!")
            sys.exit(1)
    
    import os
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        sys.exit(1)
    
    result = analyze_json(file_path)
    
    if result['errors_count'] == 0 and result['temperament_consistent']:
        print("\n✅ ANÁLISE CONCLUÍDA - TUDO CORRETO!")
    else:
        print("\n⚠️  ANÁLISE CONCLUÍDA - PROBLEMAS ENCONTRADOS!")

