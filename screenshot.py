#!/usr/bin/env python3
"""
📸 Screenshot Utility con Playwright
Capturas de páginas web
"""
import argparse
import sys
from playwright.sync_api import sync_playwright

def screenshot(url, output="screenshot.png", full=True, delay=0):
    """Toma screenshot de una URL"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        print(f"📸 Navegando a {url}...")
        page.goto(url, wait_until="load", timeout=30000)
        
        if delay > 0:
            page.wait_for_timeout(delay * 1000)
        
        page.screenshot(path=output, full_page=full)
        browser.close()
        print(f"✅ Guardado: {output}")

def main():
    parser = argparse.ArgumentParser(description="📸 Screenshot con Playwright")
    parser.add_argument("url", help="URL para capturar")
    parser.add_argument("-o", "--output", default="screenshot.png", help="Archivo de salida")
    parser.add_argument("-f", "--full", action="store_true", default=True, help="Pagina completa")
    parser.add_argument("-d", "--delay", type=int, default=0, help="Delay segundos antes de capturar")
    
    args = parser.parse_args()
    screenshot(args.url, args.output, args.full, args.delay)

if __name__ == "__main__":
    main()
