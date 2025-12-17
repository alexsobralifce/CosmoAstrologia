#!/usr/bin/env python3
"""Script para validar o sitemap.xml"""
import xml.etree.ElementTree as ET
from datetime import datetime

try:
    # Parse do XML
    tree = ET.parse('public/sitemap.xml')
    root = tree.getroot()
    
    # Verificar namespace
    namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    
    print("✅ XML bem formado")
    print(f"✅ Namespace correto: {root.tag}")
    
    # Encontrar todas as URLs
    urls = root.findall('.//sitemap:url', namespace)
    print(f"✅ {len(urls)} URLs encontradas\n")
    
    # Validar cada URL
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
                print(f"  ⚠️  AVISO: URL não começa com https://")
            if 'cosmoastral.com.br' not in url_text:
                print(f"  ⚠️  AVISO: URL não contém domínio correto")
        else:
            print(f"  ❌ ERRO: Tag <loc> não encontrada")
        
        if lastmod is not None:
            print(f"  ✅ Lastmod: {lastmod.text}")
            # Validar formato de data
            try:
                datetime.fromisoformat(lastmod.text.replace('+00:00', ''))
            except:
                print(f"  ⚠️  AVISO: Formato de data pode estar incorreto")
        else:
            print(f"  ⚠️  AVISO: Tag <lastmod> não encontrada (opcional)")
        
        if changefreq is not None:
            valid_freqs = ['always', 'hourly', 'daily', 'weekly', 'monthly', 'yearly', 'never']
            if changefreq.text.lower() in valid_freqs:
                print(f"  ✅ Changefreq: {changefreq.text}")
            else:
                print(f"  ⚠️  AVISO: Changefreq inválido: {changefreq.text}")
        else:
            print(f"  ⚠️  AVISO: Tag <changefreq> não encontrada (opcional)")
        
        if priority is not None:
            try:
                priority_val = float(priority.text)
                if 0.0 <= priority_val <= 1.0:
                    print(f"  ✅ Priority: {priority.text}")
                else:
                    print(f"  ❌ ERRO: Priority fora do range (0.0-1.0): {priority.text}")
            except ValueError:
                print(f"  ❌ ERRO: Priority não é um número: {priority.text}")
        else:
            print(f"  ⚠️  AVISO: Tag <priority> não encontrada (opcional)")
        
        print()
    
    print("✅ Validação concluída!")
    
except ET.ParseError as e:
    print(f"❌ ERRO: XML mal formado: {e}")
    exit(1)
except Exception as e:
    print(f"❌ ERRO: {e}")
    exit(1)
