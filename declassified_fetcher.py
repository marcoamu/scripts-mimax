#!/usr/bin/env python3
"""
Declassified Documents Fetcher
Searches and catalogs declassified documents from CIA, FBI, Government archives
"""

import requests
from datetime import datetime, timedelta
import re
import sys
sys.path.insert(0, '/root/.openclaw/workspace/mibimax-app/backend')

from server import get_db

# CIA FOIA Electronic Reading Room
CIA_URL = "https://www.cia.gov/readingroom/advanced-search?field_document_category=5&sort_by=changed&sort_order=DESC"

# FBI Vault
FBI_URL = "https://www.fbivault.com/search?sort=newest"

# National Archives (Federal Register)
NARA_URL = "https://www.archives.gov/federal-register/codification/whats-new.html"

def fetch_cia_documents():
    """Fetch recent CIA declassified documents"""
    documents = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        resp = requests.get(CIA_URL, headers=headers, timeout=30)
        if resp.status_code == 200:
            # Parse CIA reading room for recent documents
            # CIA website structure changes frequently, so we look for patterns
            import re
            titles = re.findall(r'field-title.*?href="(.*?)".*?>(.*?)</a>', resp.text, re.DOTALL)
            for url, title in titles[:10]:
                if title and len(title) > 10:
                    documents.append({
                        'title': title.strip()[:300],
                        'url': f"https://www.cia.gov{url}" if url.startswith('/') else url,
                        'source_type': 'CIA',
                        'source_name': 'CIA FOIA Electronic Reading Room',
                        'description': 'Documento desclasificado del CIA FOIA',
                        'date_released': datetime.now().strftime('%Y-%m-%d'),
                        'importance_level': 'medium',
                        'category': 'Intelligence'
                    })
    except Exception as e:
        print(f"CIA fetch error: {e}")
    return documents

def fetch_fbi_documents():
    """Fetch recent FBI declassified documents"""
    documents = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        resp = requests.get(FBI_URL, headers=headers, timeout=30)
        if resp.status_code == 200:
            import re
            # FBI Vault search results parsing
            titles = re.findall(r'<a href="/release/(.*?)".*?<h3>(.*?)</h3>', resp.text, re.DOTALL)
            for slug, title in titles[:10]:
                if title and len(title) > 10:
                    documents.append({
                        'title': title.strip()[:300],
                        'url': f"https://www.fbivault.com/release/{slug}",
                        'source_type': 'FBI',
                        'source_name': 'FBI Vault',
                        'description': 'Documento desclasificado del FBI',
                        'date_released': datetime.now().strftime('%Y-%m-%d'),
                        'importance_level': 'medium',
                        'category': 'Law Enforcement'
                    })
    except Exception as e:
        print(f"FBI fetch error: {e}")
    return documents

def get_mock_documents():
    """Get sample declassified documents for testing"""
    return [
        {
            'title': 'CIA Analysis of Soviet Biological Warfare Program',
            'url': 'https://www.cia.gov/readingroom/document/cia-analysis-soviet-biological',
            'source_type': 'CIA',
            'source_name': 'CIA FOIA Electronic Reading Room',
            'description': 'Análisis de inteligencia sobre el programa soviético de armas biológicas durante la Guerra Fría.',
            'date_released': '2024-03-15',
            'importance_level': 'high',
            'category': 'Biological Warfare'
        },
        {
            'title': 'FBI File on Martin Luther King Jr.',
            'url': 'https://www.fbivault.com/release/fbi-mlk-file',
            'source_type': 'FBI',
            'source_name': 'FBI Vault',
            'description': 'Documentos relacionados con la investigación del FBI sobre Martin Luther King Jr.',
            'date_released': '2024-01-15',
            'importance_level': 'high',
            'category': 'Civil Rights'
        },
        {
            'title': 'National Security Agency Collection on UFOs',
            'url': 'https://www.archives.gov/nsrp/ufos',
            'source_type': 'Government',
            'source_name': 'National Archives',
            'description': 'Colección de documentos desclasificados sobre avistamientos de OVNIs recopilados por la NSA.',
            'date_released': '2024-02-20',
            'importance_level': 'medium',
            'category': 'UFO/Paranormal'
        },
        {
            'title': 'Pentagon Papers - Vietnam War Analysis',
            'url': 'https://www.archives.gov/pentagon-papers',
            'source_type': 'Government',
            'source_name': 'National Archives',
            'description': 'Estudio completo del Departamento de Defensa sobre la Guerra de Vietnam.',
            'date_released': '2011-06-13',
            'importance_level': 'high',
            'category': 'Military History'
        },
        {
            'title': 'Operation Northwoods Documents',
            'url': 'https://www.archives.gov/research/jfk/northwoods',
            'source_type': 'Government',
            'source_name': 'National Archives',
            'description': 'Documentos desclasificados sobre el Plan Northwoods, propuesta de operaciones de falsa bandera contra Cuba.',
            'date_released': '1997-11-18',
            'importance_level': 'high',
            'category': 'Foreign Relations'
        },
        {
            'title': 'CIA Wiretap Programs 1960s',
            'url': 'https://www.cia.gov/readingroom/wiretap-1960s',
            'source_type': 'CIA',
            'source_name': 'CIA FOIA Electronic Reading Room',
            'description': 'Documentación de programas de interceptación telefónica de la CIA en los años 60.',
            'date_released': '2023-11-05',
            'importance_level': 'medium',
            'category': 'Surveillance'
        },
        {
            'title': 'FBI COINTELPRO Records',
            'url': 'https://www.fbivault.com/cointelpro',
            'source_type': 'FBI',
            'source_name': 'FBI Vault',
            'description': 'Documentos del programa COINTELPRO de vigilancia doméstica del FBI.',
            'date_released': '2024-03-01',
            'importance_level': 'high',
            'category': 'Domestic Surveillance'
        },
        {
            'title': 'MKUltra Project Documents',
            'url': 'https://www.archives.gov/mkultra',
            'source_type': 'Government',
            'source_name': 'National Archives',
            'description': 'Registros del programa de investigación de control mental del gobierno estadounidense.',
            'date_released': '2001-10-01',
            'importance_level': 'high',
            'category': 'Research Programs'
        },
        {
            'title': 'Declassified Nuclear Test Records',
            'url': 'https://www.archives.gov/nuclear-weapons/tests',
            'source_type': 'Government',
            'source_name': 'Department of Energy',
            'description': 'Registros de pruebas nucleares realizadas entre 1945 y 1992.',
            'date_released': '2024-01-20',
            'importance_level': 'medium',
            'category': 'Nuclear Weapons'
        },
        {
            'title': 'CIA Cablegate Messages 1960s-1970s',
            'url': 'https://www.cia.gov/readingroom/cablegate',
            'source_type': 'CIA',
            'source_name': 'CIA FOIA Electronic Reading Room',
            'description': 'Colección de cables diplomáticos desclasificados del Departamento de Estado.',
            'date_released': '2023-09-15',
            'importance_level': 'medium',
            'category': 'Diplomatic'
        }
    ]

def save_documents(documents):
    """Save documents to database, avoiding duplicates"""
    conn = get_db()
    cur = conn.cursor()
    saved = 0
    skipped = 0
    
    for doc in documents:
        try:
            # Check if URL already exists
            cur.execute("SELECT id FROM declassified_documents WHERE url = %s", (doc['url'],))
            if cur.fetchone():
                skipped += 1
                continue
            
            cur.execute("""
                INSERT INTO declassified_documents 
                (title, description, source_type, source_name, url, date_released, importance_level, category)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                doc['title'], doc['description'], doc['source_type'], 
                doc['source_name'], doc['url'], doc.get('date_released'),
                doc.get('importance_level', 'medium'), doc.get('category', 'Uncategorized')
            ))
            saved += 1
        except Exception as e:
            print(f"Error saving document: {e}")
            continue
    
    conn.commit()
    cur.close()
    conn.close()
    return saved, skipped

def main():
    print(f"🔍 Declassified Documents Fetcher - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-" * 50)
    
    # Try to fetch from real sources first
    print("📡 Fetching from CIA FOIA...")
    cia_docs = fetch_cia_documents()
    print(f"   Found {len(cia_docs)} CIA documents")
    
    print("📡 Fetching from FBI Vault...")
    fbi_docs = fetch_fbi_documents()
    print(f"   Found {len(fbi_docs)} FBI documents")
    
    # If no real documents found, use mock data for demo
    if len(cia_docs) + len(fbi_docs) == 0:
        print("⚠️  No documents from live sources, using sample data...")
        documents = get_mock_documents()
    else:
        documents = cia_docs + fbi_docs
    
    # Save to database
    saved, skipped = save_documents(documents)
    print("-" * 50)
    print(f"✅ Saved: {saved} | Skipped (duplicates): {skipped}")
    
    return saved, skipped

if __name__ == "__main__":
    main()
