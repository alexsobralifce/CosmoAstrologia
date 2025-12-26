"""
Script para extrair informações específicas dos livros de referência:
1. Sakoian & Acker - The Astrologer's Handbook (Aspectos e geometria angular)
2. Stephen Arroyo - Normas Práticas (Casas e Elementos)
3. Kris Brandt Riske - Llewellyn's Complete Book (Regras de segurança)

Este script filtra informações minuciosamente e cria documentos estruturados
para ampliar o RAG, garantindo que os cálculos usem a biblioteca local.
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    print("[WARNING] PyPDF2 não instalado. Tentando pdfplumber...")

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    print("[WARNING] pdfplumber não instalado. Instale com: pip install pdfplumber")

# Caminhos dos PDFs
ASTROLOGIA_DIR = Path(__file__).parent.parent / "astrologia"

PDFS = {
    'sakoian_acker': ASTROLOGIA_DIR / "pdfcoffee.com_sakoian-amp-acker-the-astrologers-handbook-pdf-free.pdf",
    'arroyo': ASTROLOGIA_DIR / "pdfcoffee.com_normas-praticas-para-a-interpretaao-do-mapa-astral-stephen-arroyo-pdf-free.pdf",
    'riske': ASTROLOGIA_DIR / "O Livro Completo Da Astrologia PDF.pdf"
}

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "reference_books"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def extract_text_from_pdf(pdf_path: Path) -> Dict[int, str]:
    """Extrai texto de um PDF, retornando um dicionário {página: texto}."""
    if not pdf_path.exists():
        print(f"[WARNING] PDF não encontrado: {pdf_path}")
        return {}
    
    text_by_page = {}
    
    # Tentar primeiro com pdfplumber (melhor para PDFs escaneados)
    if HAS_PDFPLUMBER:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                print(f"[INFO] Processando {pdf_path.name} com pdfplumber ({total_pages} páginas)...")
                
                for page_num in range(total_pages):
                    try:
                        page = pdf.pages[page_num]
                        text = page.extract_text()
                        if text and text.strip():
                            text_by_page[page_num + 1] = text
                    except Exception as e:
                        print(f"[WARNING] Erro ao extrair página {page_num + 1} com pdfplumber: {e}")
                        continue
                
                if text_by_page:
                    print(f"[INFO] Extraídas {len(text_by_page)} páginas com texto (pdfplumber)")
                    return text_by_page
        except Exception as e:
            print(f"[WARNING] Erro ao processar com pdfplumber: {e}")
            print(f"         Tentando PyPDF2...")
    
    # Fallback para PyPDF2
    if HAS_PYPDF2:
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                print(f"[INFO] Processando {pdf_path.name} com PyPDF2 ({total_pages} páginas)...")
                
                for page_num in range(total_pages):
                    try:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        if text.strip():
                            text_by_page[page_num + 1] = text
                    except Exception as e:
                        print(f"[WARNING] Erro ao extrair página {page_num + 1}: {e}")
                        continue
                
                print(f"[INFO] Extraídas {len(text_by_page)} páginas com texto (PyPDF2)")
        except Exception as e:
            print(f"[ERROR] Erro ao processar PDF {pdf_path}: {e}")
    else:
        print(f"[ERROR] Nenhuma biblioteca de PDF disponível. Instale PyPDF2 ou pdfplumber.")
    
    return text_by_page


def filter_sakoian_acker_content(text_by_page: Dict[int, str]) -> str:
    """
    Filtra informações sobre aspectos e geometria angular do livro de Sakoian & Acker.
    Busca por: aspectos, trígono, quadratura, orbe, geometria angular, aspectos maiores/menores
    """
    relevant_content = []
    
    # Palavras-chave para buscar
    keywords = [
        r'aspect',
        r'trígono|trine',
        r'quadratura|square',
        r'sextil|sextile',
        r'conjunção|conjunction',
        r'oposição|opposition',
        r'orbe|orb',
        r'geometr[íi]a angular',
        r'angular.*relationship',
        r'aspect.*calculation',
        r'aspect.*definition',
        r'aspect.*meaning',
        r'aspect.*interpretation'
    ]
    
    for page_num, text in text_by_page.items():
        # Normalizar texto
        text_lower = text.lower()
        
        # Verificar se a página contém palavras-chave relevantes
        matches = sum(1 for keyword in keywords if re.search(keyword, text_lower, re.IGNORECASE))
        
        if matches >= 2:  # Pelo menos 2 palavras-chave
            # Extrair parágrafos relevantes
            paragraphs = text.split('\n\n')
            relevant_paragraphs = []
            
            for para in paragraphs:
                para_lower = para.lower()
                if any(re.search(kw, para_lower, re.IGNORECASE) for kw in keywords):
                    relevant_paragraphs.append(para.strip())
            
            if relevant_paragraphs:
                relevant_content.append(f"\n--- Página {page_num} ---\n")
                relevant_content.append("\n\n".join(relevant_paragraphs))
    
    return "\n\n".join(relevant_content)


def filter_arroyo_content(text_by_page: Dict[int, str]) -> str:
    """
    Filtra informações sobre Casas e Elementos do livro de Stephen Arroyo.
    Busca por: casas, triplicidade, riqueza, vida, elementos, fire, earth, air, water
    """
    relevant_content = []
    
    # Palavras-chave para buscar
    keywords = [
        r'casa|house',
        r'triplicidade|triplicity',
        r'riqueza|wealth',
        r'elemento|element',
        r'fogo|fire',
        r'terra|earth',
        r'ar|air',
        r'água|water',
        r'casa.*2|second.*house',
        r'casa.*5|fifth.*house',
        r'casa.*8|eighth.*house',
        r'casa.*11|eleventh.*house',
        r'interpretação.*casa',
        r'meaning.*house',
        r'house.*signification'
    ]
    
    for page_num, text in text_by_page.items():
        text_lower = text.lower()
        matches = sum(1 for keyword in keywords if re.search(keyword, text_lower, re.IGNORECASE))
        
        if matches >= 2:
            paragraphs = text.split('\n\n')
            relevant_paragraphs = []
            
            for para in paragraphs:
                para_lower = para.lower()
                if any(re.search(kw, para_lower, re.IGNORECASE) for kw in keywords):
                    relevant_paragraphs.append(para.strip())
            
            if relevant_paragraphs:
                relevant_content.append(f"\n--- Página {page_num} ---\n")
                relevant_content.append("\n\n".join(relevant_paragraphs))
    
    return "\n\n".join(relevant_content)


def filter_riske_content(text_by_page: Dict[int, str]) -> str:
    """
    Filtra informações sobre regras de segurança do livro de Kris Brandt Riske.
    Busca por: mercúrio retrógrado, lua fora de curso, void of course, retrógrado, não agir
    """
    relevant_content = []
    
    # Palavras-chave para buscar
    keywords = [
        r'mercúrio.*retrógrado|mercury.*retrograde',
        r'lua.*fora.*curso|moon.*void.*course',
        r'void.*course',
        r'retrógrado|retrograde',
        r'não.*agir|do.*not.*act',
        r'evitar|avoid',
        r'segurança|safety',
        r'regra.*timing|timing.*rule',
        r'elecção|election',
        r'horária|horary'
    ]
    
    for page_num, text in text_by_page.items():
        text_lower = text.lower()
        matches = sum(1 for keyword in keywords if re.search(keyword, text_lower, re.IGNORECASE))
        
        if matches >= 1:  # Apenas 1 palavra-chave já é relevante para regras de segurança
            paragraphs = text.split('\n\n')
            relevant_paragraphs = []
            
            for para in paragraphs:
                para_lower = para.lower()
                if any(re.search(kw, para_lower, re.IGNORECASE) for kw in keywords):
                    relevant_paragraphs.append(para.strip())
            
            if relevant_paragraphs:
                relevant_content.append(f"\n--- Página {page_num} ---\n")
                relevant_content.append("\n\n".join(relevant_paragraphs))
    
    return "\n\n".join(relevant_content)


def create_structured_document(title: str, content: str, source: str, category: str) -> str:
    """Cria um documento estruturado para o RAG."""
    header = f"""# {title}

**Fonte:** {source}
**Categoria:** {category}
**Uso na estratégia:** {{
    'sakoian_acker': 'Definições precisas de aspectos (trígonos, quadraturas) e geometria angular para calcular momentos de sorte ou tensão',
    'arroyo': 'Definições das Casas e dos Elementos (Triplicidade da Riqueza, Triplicidade da Vida) para estruturar negócios e carreira',
    'riske': 'Regras de segurança como Mercúrio Retrógrado e Lua Fora de Curso, usados como filtros de "não agir"'
}}[category]

**IMPORTANTE:** Todos os cálculos astrológicos devem ser feitos usando a biblioteca local (Swiss Ephemeris via kerykeion). 
Nunca invente ou estime cálculos. Use apenas dados calculados e validados pela biblioteca padrão.

---

"""
    return header + content


def main():
    """Função principal para extrair e processar os PDFs."""
    print("="*80)
    print("EXTRAÇÃO DE INFORMAÇÕES DOS LIVROS DE REFERÊNCIA")
    print("="*80)
    print()
    
    # Processar cada PDF
    results = {}
    
    # 1. Sakoian & Acker - Aspectos
    print("\n[1/3] Processando Sakoian & Acker (Aspectos e Geometria Angular)...")
    if PDFS['sakoian_acker'].exists():
        text_by_page = extract_text_from_pdf(PDFS['sakoian_acker'])
        filtered_content = filter_sakoian_acker_content(text_by_page)
        results['sakoian_acker'] = filtered_content
        
        # Salvar documento estruturado
        doc = create_structured_document(
            "Aspectos e Geometria Angular - Sakoian & Acker",
            filtered_content,
            "Sakoian, Frances & Acker, Louis S. - The Astrologer's Handbook",
            "sakoian_acker"
        )
        
        output_file = OUTPUT_DIR / "sakoian_acker_aspectos.md"
        output_file.write_text(doc, encoding='utf-8')
        print(f"[SUCCESS] Documento salvo: {output_file}")
        print(f"         Tamanho: {len(filtered_content)} caracteres")
    else:
        print(f"[WARNING] PDF não encontrado: {PDFS['sakoian_acker']}")
    
    # 2. Stephen Arroyo - Casas e Elementos
    print("\n[2/3] Processando Stephen Arroyo (Casas e Elementos)...")
    if PDFS['arroyo'].exists():
        text_by_page = extract_text_from_pdf(PDFS['arroyo'])
        filtered_content = filter_arroyo_content(text_by_page)
        results['arroyo'] = filtered_content
        
        # Salvar documento estruturado
        doc = create_structured_document(
            "Casas e Elementos - Stephen Arroyo",
            filtered_content,
            "Arroyo, Stephen - Normas Práticas para a Interpretação do Mapa Astral",
            "arroyo"
        )
        
        output_file = OUTPUT_DIR / "arroyo_casas_elementos.md"
        output_file.write_text(doc, encoding='utf-8')
        print(f"[SUCCESS] Documento salvo: {output_file}")
        print(f"         Tamanho: {len(filtered_content)} caracteres")
    else:
        print(f"[WARNING] PDF não encontrado: {PDFS['arroyo']}")
    
    # 3. Kris Brandt Riske - Regras de Segurança
    print("\n[3/3] Processando Kris Brandt Riske (Regras de Segurança)...")
    if PDFS['riske'].exists():
        text_by_page = extract_text_from_pdf(PDFS['riske'])
        filtered_content = filter_riske_content(text_by_page)
        results['riske'] = filtered_content
        
        # Salvar documento estruturado
        doc = create_structured_document(
            "Regras de Segurança - Kris Brandt Riske",
            filtered_content,
            "Riske, Kris Brandt - Llewellyn's Complete Book of Astrology",
            "riske"
        )
        
        output_file = OUTPUT_DIR / "riske_regras_seguranca.md"
        output_file.write_text(doc, encoding='utf-8')
        print(f"[SUCCESS] Documento salvo: {output_file}")
        print(f"         Tamanho: {len(filtered_content)} caracteres")
    else:
        print(f"[WARNING] PDF não encontrado: {PDFS['riske']}")
    
    # Resumo
    print("\n" + "="*80)
    print("RESUMO")
    print("="*80)
    total_chars = sum(len(content) for content in results.values())
    print(f"Total de caracteres extraídos: {total_chars:,}")
    print(f"Documentos criados: {len(results)}")
    print(f"\nPróximo passo: Reconstruir o índice RAG com:")
    print(f"  python scripts/build_rag_index_fastembed.py")
    print("="*80)


if __name__ == "__main__":
    main()

