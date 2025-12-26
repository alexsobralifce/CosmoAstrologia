#!/usr/bin/env python3
"""Script para validar o sitemap.xml"""
import xml.etree.ElementTree as ET
import sys
from pathlib import Path

# Caminho do sitemap
sitemap_path = Path(__file__).parent.parent / 'public' / 'sitemap.xml'

if not sitemap_path.exists():
    print(f"❌ ERRO: Arquivo não encontrado: {sitemap_path}")
    sys.exit(1)

try:
    # Parse do XML
    tree = ET.parse(sitemap_path)
    root = tree.getroot()
    
    # Verificar namespace
    namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    
    print("✅ XML bem formado")
    print(f"✅ Namespace correto: {root.tag}")
    
    # Encontrar todas as URLs
    urls = root.findall('.//sitemap:url', namespace)
    print(f"✅ {len(urls)} URLs encontradas\n")
    
    # Validar cada URL
    errors = []
    warnings = []
    
    for i, url in enumerate(urls, 1):
        loc = url.find('sitemap:loc', namespace)
        lastmod = url.find('sitemap:lastmod', namespace)
        changefreq = url.find('sitemap:changefreq', namespace)
        priority = url.find('sitemap:priority', namespace)
        
        print(f"URL {i}:")
        if loc is not None:
            url_text = loc.text
            print(f"  ✅ Loc: {url_text}")
            
            # Validar URL
            if not url_text.startswith('https://'):
                error = f"  ❌ ERRO: URL não começa com https://"
                print(error)
                errors.append(error)
            if 'cosmoastral.com.br' not in url_text:
                warning = f"  ⚠️  AVISO: URL não contém domínio correto"
                print(warning)
                warnings.append(warning)
        else:
            error = f"  ❌ ERRO: Tag <loc> não encontrada"
            print(error)
            errors.append(error)
        
        if lastmod is not None:
            print(f"  ✅ Lastmod: {lastmod.text}")
            # Validar formato de data (ISO 8601)
            try:
                # Tenta parse direto
                datetime.fromisoformat(lastmod.text.replace('Z', '+00:00'))
            except:
                try:
                    # Tenta sem timezone
                    datetime.fromisoformat(lastmod.text.split('+')[0].split('T')[0])
                except:
                    # Formato inválido
                    warning = f"  ⚠️  AVISO: Formato de data pode estar incorreto: {lastmod.text}"
                    print(warning)
                    warnings.append(warning)
        else:
            print(f"  ⚠️  AVISO: Tag <lastmod> não encontrada (opcional)")
        
        if changefreq is not None:
            valid_freqs = ['always', 'hourly', 'daily', 'weekly', 'monthly', 'yearly', 'never']
            if changefreq.text.lower() in valid_freqs:
                print(f"  ✅ Changefreq: {changefreq.text}")
            else:
                error = f"  ❌ ERRO: Changefreq inválido: {changefreq.text}"
                print(error)
                errors.append(error)
        else:
            print(f"  ⚠️  AVISO: Tag <changefreq> não encontrada (opcional)")
        
        if priority is not None:
            try:
                priority_val = float(priority.text)
                if 0.0 <= priority_val <= 1.0:
                    print(f"  ✅ Priority: {priority.text}")
                else:
                    error = f"  ❌ ERRO: Priority fora do range (0.0-1.0): {priority.text}"
                    print(error)
                    errors.append(error)
            except ValueError:
                error = f"  ❌ ERRO: Priority não é um número: {priority.text}"
                print(error)
                errors.append(error)
        else:
            print(f"  ⚠️  AVISO: Tag <priority> não encontrada (opcional)")
        
        print()
    
    # Resumo
    print("=" * 50)
    if errors:
        print(f"❌ {len(errors)} ERRO(S) encontrado(s)")
        sys.exit(1)
    elif warnings:
        print(f"⚠️  {len(warnings)} AVISO(S) encontrado(s) (não críticos)")
    else:
        print("✅ Validação concluída sem erros!")
    
except ET.ParseError as e:
    print(f"❌ ERRO: XML mal formado: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
