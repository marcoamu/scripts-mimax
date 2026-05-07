#!/usr/bin/env python3
"""
Science Papers Bot - Buscador de papers científicos
Usa Semantic Scholar API y OpenAlex API (gratuitas)
"""

import os
import time
import logging
import random
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    ContextTypes, filters, CallbackQueryHandler
)
import requests

# Configuración
BOT_TOKEN = "8616597549:AAFIDUKbD1pRb9JCjNVQB4ZDV8ZP-10lz30"
SEMANTIC_API = "https://api.semanticscholar.org/graph/v1"
OPENALEX_API = "https://api.openalex.org"
ARXIV_API = "http://export.arxiv.org/api/query"

# Rate limiting
last_request_time = 0
MIN_REQUEST_INTERVAL = 1.0

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_text(text, max_len=200):
    """Limpiar texto de caracteres problemáticos"""
    if not text:
        return "N/A"
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    if len(text) > max_len:
        text = text[:max_len] + "..."
    return text.strip()

def rate_limited_request(url, params=None, max_retries=3):
    """Hacer request con rate limiting y retry"""
    global last_request_time
    for attempt in range(max_retries):
        try:
            elapsed = time.time() - last_request_time
            if elapsed < MIN_REQUEST_INTERVAL:
                time.sleep(MIN_REQUEST_INTERVAL - elapsed)
            last_request_time = time.time()
            response = requests.get(url, params=params, timeout=20)
            if response.status_code == 429:
                wait_time = random.uniform(2, 5) * (attempt + 1)
                logger.info(f"Rate limited, waiting {wait_time:.1f}s")
                time.sleep(wait_time)
                continue
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
            continue
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Science Papers Bot\n\n"
        "Busca papers cientificos de forma gratuita.\n\n"
        "Usa /search <tema> para buscar papers\n"
        "Ejemplo: /search machine learning healthcare"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Comandos disponibles:\n\n"
        "/search <tema> - Buscar papers\n"
        "/help - Mostrar ayuda\n\n"
        "Los resultados incluyen link gratuito al paper"
    )

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Uso: /search <tema>\n"
            "Ejemplo: /search transformer models"
        )
        return
    
    query = " ".join(context.args)
    await update.message.reply_text(f"Buscando papers sobre: {query}...")
    
    try:
        url = f"{SEMANTIC_API}/paper/search"
        params = {
            "query": query,
            "limit": 10,
            "fields": "title,authors,year,abstract,citationCount,openAccessPdf"
        }
        
        response = rate_limited_request(url, params)
        
        if response and response.status_code == 200:
            data = response.json()
            papers = data.get("data", [])
            
            if papers:
                await send_papers_results(update, query, papers, context)
                return
        
        await search_openalex(update, query, context)
        
    except Exception as e:
        logger.error(f"Error searching: {e}")
        await update.message.reply_text(f"Error en la busqueda: {str(e)}")

def search_arxiv(query, max_results=8):
    """Buscar papers en arXiv"""
    try:
        import urllib.parse
        search_query = urllib.parse.quote(query)
        url = f"{ARXIV_API}?search_query=all:{search_query}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
        
        response = requests.get(url, timeout=20)
        if response.status_code != 200:
            return None
        
        # Parsear XML de arXiv
        content = response.text
        
        papers = []
        entries = content.split('<entry>')
        
        for entry in entries[1:max_results+1]:
            try:
                title_match = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
                author_matches = re.findall(r'<name>(.*?)</name>', entry)
                summary_match = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
                published_match = re.search(r'<published>(.*?)</published>', entry)
                pdf_match = re.search(r'<link href="(.*?)" title="pdf"', entry)
                arxiv_url_match = re.search(r'<id>(.*?)</id>', entry)
                
                if title_match:
                    title = clean_text(title_match.group(1).strip(), 80)
                    authors = ", ".join(author_matches[:3]) if author_matches else "Unknown"
                    if len(author_matches) > 3:
                        authors += f" +{len(author_matches)-3}"
                    
                    year = "N/A"
                    if published_match:
                        year = published_match.group(1)[:4]
                    
                    pdf_url = pdf_match.group(1) if pdf_match else None
                    article_url = arxiv_url_match.group(1) if arxiv_url_match else None
                    
                    papers.append({
                        "title": title,
                        "authors": authors,
                        "year": year,
                        "pdf_url": pdf_url,
                        "url": article_url,
                        "source": "arXiv"
                    })
            except:
                continue
        
        return papers if papers else None
        
    except Exception as e:
        logger.error(f"ArXiv search error: {e}")
        return None

async def search_arxiv_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, query):
    """Handler para buscar en arXiv"""
    try:
        await update.message.reply_text(f"Buscando en arXiv: {query}...")
        
        papers = search_arxiv(query)
        
        if not papers:
            await update.message.reply_text("No se encontraron papers en arXiv.")
            return
        
        message = f"Resultados de arXiv para: {query}\n\n"
        
        for i, paper in enumerate(papers[:8], 1):
            message += f"{i}. {paper['title']}...\n"
            message += f"   Autor: {paper['authors']} | Ano: {paper['year']}\n"
            if paper['pdf_url']:
                message += f"   PDF: {paper['pdf_url']}\n"
            message += "\n"
            
            context.user_data[f"paper_{i}"] = f"arxiv:{paper['url']}"
        
        keyboard = [
            [InlineKeyboardButton("Nueva busqueda", callback_data="new_search")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"ArXiv handler error: {e}")
        await update.message.reply_text("Error buscando en arXiv.")

async def search_openalex(update, query, context):
    try:
        await update.message.reply_text("Probando fuente alternativa...")
        
        url = f"{OPENALEX_API}/works"
        params = {
            "search": query,
            "per-page": 8,
            "select": "title,authorships,publication_year,open_access,doi"
        }
        
        response = rate_limited_request(url, params)
        
        if not response or response.status_code != 200:
            await update.message.reply_text("No se pudieron obtener resultados. Intenta de nuevo en unos minutos.")
            return
        
        data = response.json()
        works = data.get("results", [])
        
        if not works:
            await update.message.reply_text("No se encontraron papers. Prueba otro tema.")
            return
        
        message = f"Resultados para: {query}\n\n"
        
        for i, work in enumerate(works[:8], 1):
            title = clean_text(work.get("title", "Sin titulo"), 80)
            year = work.get("publication_year", "N/A")
            authors = work.get("authorships", [])
            author_str = authors[0].get("author", {}).get("display_name", "Unknown") if authors else "Unknown"
            if len(authors) > 1:
                author_str += f" +{len(authors)-1}"
            
            oa = work.get("open_access", {})
            pdf_url = oa.get("oa_url") if oa else None
            
            message += f"{i}. {title}...\n"
            message += f"   Autor: {author_str} | Ano: {year}\n"
            if pdf_url:
                message += f"   PDF: {pdf_url}\n"
            message += "\n"
            
            context.user_data[f"paper_{i}"] = f"openalex:{work.get('doi', '')}"
        
        keyboard = [
            [InlineKeyboardButton("Nueva busqueda", callback_data="new_search")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"OpenAlex search error: {e}")
        await update.message.reply_text("Error al buscar. Intenta de nuevo mas tarde.")

async def send_papers_results(update, query, papers, context):
    message = f"Resultados para: {query}\n\n"
    
    for i, paper in enumerate(papers[:8], 1):
        title = clean_text(paper.get("title", "Sin titulo"), 80)
        year = paper.get("year", "N/A")
        citations = paper.get("citationCount", 0)
        authors = paper.get("authors", [])
        author_str = authors[0].get("name", "Unknown") if authors else "Unknown"
        if len(authors) > 1:
            author_str += f" +{len(authors)-1}"
        
        pdf_url = paper.get("openAccessPdf", {})
        pdf_link = pdf_url.get("url") if pdf_url else None
        
        message += f"{i}. {title}...\n"
        message += f"   Autor: {author_str} | Ano: {year} | Citas: {citations}\n"
        
        if pdf_link and pdf_link.strip():
            message += f"   PDF: {pdf_link}\n"
        
        paper_id = paper.get("paperId", "")
        context.user_data[f"paper_{i}"] = paper_id
        message += "\n"
    
    keyboard = [
        [InlineKeyboardButton("Mas resultados", callback_data=f"more_{query}")],
        [InlineKeyboardButton("Nueva busqueda", callback_data="new_search")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "new_search":
        await query.edit_message_text("Escribe /search <tema> para una nueva busqueda")
    elif query.data.startswith("more_"):
        topic = query.data[5:]
        context.args = topic.split()
        await search(update, context)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if any(word in text for word in ["buscar", "search", "paper"]):
        await update.message.reply_text(
            "Usa /search <tema> para buscar papers\n"
            "Ejemplo: /search neural networks"
        )
    else:
        await update.message.reply_text(
            "Science Papers Bot\n"
            "Usa /search <tema> para buscar papers"
        )

async def arxiv_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando especifico para buscar en arXiv"""
    if not context.args:
        await update.message.reply_text(
            "Uso: /arxiv <tema>\n"
            "Busca especificamente en arXiv (papers de fisica, CS, matematicas)\n"
            "Ejemplo: /arxiv machine learning"
        )
        return
    
    query = " ".join(context.args)
    await search_arxiv_handler(update, context, query)

def main():
    logger.info("Starting Science Papers Bot...")
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("arxiv", arxiv_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    logger.info("Bot is running!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()