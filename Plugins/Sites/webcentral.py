# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat

import logging
import asyncio
import aiohttp
import re
import io
from PIL import Image
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import hashlib

logger = logging.getLogger(__name__)

class WebCentralAPI:
    def __init__(self, Config):
        self.Config = Config
        self.base_url = "https://weebcentral.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://weebcentral.com/",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def get_latest_chapters(self, limit: int = 50) -> List[Dict]:
        """Scrape latest updates from WebCentral Homepage"""
        chapters = []
        urls = [self.base_url]
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for url in urls:
                try:
                    logger.info(f"Fetching WebCentral: {url}")
                    async with session.get(url, timeout=30) as resp:
                        if resp.status != 200:
                            logger.error(f"WebCentral returned status {resp.status}")
                            continue
                        html = await resp.text()
                        soup = BeautifulSoup(html, "html.parser")
                        
                        # Try multiple selectors to find chapter links
                        # Look for any link containing chapter/episode keywords
                        links = soup.find_all("a", href=True)
                        logger.info(f"Found {len(links)} total links on page")
                        
                        seen_ids = set()
                        potential_chapters = []
                        
                        for a in links:
                            href = a.get("href", "")
                            
                            # Filter for chapter-like URLs
                            if not any(keyword in href.lower() for keyword in ['/chapter', '/episode', '/read']):
                                continue
                            
                            full_url = urljoin(self.base_url, href)
                            text_content = a.get_text(separator=" ", strip=True)
                            
                            if not text_content or len(text_content) < 3:
                                continue
                            
                            # Try multiple regex patterns
                            manga_title = None
                            chap_num = None
                            
                            # Pattern 1: "Title Chapter 123"
                            m = re.search(r"(.+?)\s+(?:Episode|Chapter|Ch\.?|Ep\.?)\s+(\d+(?:\.\d+)?)", text_content, re.I)
                            if m:
                                manga_title = m.group(1).strip()
                                chap_num = m.group(2)
                            
                            # Pattern 2: "Chapter 123 - Title" or just "Chapter 123"
                            if not manga_title:
                                m = re.search(r"(?:Chapter|Episode|Ch\.?|Ep\.?)\s+(\d+(?:\.\d+)?)\s*[-:]?\s*(.*)", text_content, re.I)
                                if m:
                                    chap_num = m.group(1)
                                    manga_title = m.group(2).strip() if m.group(2) else "Unknown"
                            
                            # Pattern 3: Extract from URL if text parsing fails
                            if not manga_title or not chap_num:
                                url_match = re.search(r'/([^/]+)/(?:chapter|episode|ch|ep)[-_]?(\d+(?:\.\d+)?)', href, re.I)
                                if url_match:
                                    manga_title = url_match.group(1).replace('-', ' ').replace('_', ' ').title()
                                    chap_num = url_match.group(2)
                            
                            # Fallback
                            if not manga_title:
                                manga_title = text_content[:50]
                            if not chap_num:
                                chap_num = "0"
                            
                            full_title = f"{manga_title} - Chapter {chap_num}"
                            chap_id_hash = hashlib.md5(full_url.encode()).hexdigest()
                            
                            if chap_id_hash not in seen_ids:
                                seen_ids.add(chap_id_hash)
                                potential_chapters.append({
                                    'id': chap_id_hash,
                                    'manga_id': chap_id_hash,
                                    'manga_title': manga_title,
                                    'chapter': chap_num,
                                    'title': full_title,
                                    'group': "WebCentral",
                                    'url': full_url
                                })
                        
                        logger.info(f"Found {len(potential_chapters)} potential chapters after filtering")
                        
                        # Add to main list
                        for chap in potential_chapters:
                            if len(chapters) >= limit:
                                break
                            chapters.append(chap)
                            logger.debug(f"Added: {chap['title']} - {chap['url']}")
                                
                except Exception as e:
                    logger.error(f"WebCentral check failed: {e}", exc_info=True)
                    
        logger.info(f"Total chapters found: {len(chapters)}")
        return chapters

    async def get_manga_info(self, manga_id: str) -> Optional[Dict]:
        """Fetch manga info. Note: manga_id might be a chapter URL if scraped from latest."""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(manga_id, timeout=30) as resp:
                    if resp.status != 200: 
                        return {'id': manga_id, 'title': 'Unknown', 'cover_url': None}
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    series_link = soup.find("a", href=re.compile(r"/series/"))
                    title = "Unknown"
                    if series_link:
                        title = series_link.get_text(strip=True)
                    
                    cover_url = None
                    og_img = soup.find("meta", property="og:image")
                    if og_img:
                        cover_url = og_img.get("content")
                    
                    return {'id': manga_id, 'title': title, 'cover_url': cover_url}
        except Exception as e:
            logger.error(f"WebCentral get_manga_info failed: {e}")
            return None

    async def get_chapter_images(self, chapter_url: str) -> Optional[List[str]]:
        """Scrape images from a chapter URL using internal API"""
        images = []
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(chapter_url, timeout=30) as resp:
                    if resp.status != 200: return None
                    await resp.text()

                base_chap_url = chapter_url.rstrip('/')
                api_url = f"{base_chap_url}/images?is_prev=False&current_page=1&reading_style=long_strip"
                
                api_headers = self.headers.copy()
                api_headers.update({
                    "HX-Request": "True",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": chapter_url
                })
                
                async with session.get(api_url, headers=api_headers, timeout=30) as resp:
                    if resp.status != 200: 
                        logger.error(f"WebCentral API failed: {resp.status}")
                        return None
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    imgs = soup.find_all("img")
                    for img in imgs:
                        src = img.get("src") or img.get("data-src")
                        if not src: continue
                        
                        if any(x in src.lower() for x in ["logo", "avatar", "icon", "banner", "loader", "broken_image"]):
                            continue
                            
                        full_src = urljoin(self.base_url, src)
                        if full_src not in images:
                            images.append(full_src)
                            
            except Exception as e:
                logger.error(f"WebCentral DL failed: {e}")
                return None
        return images
    
    async def search_manga(self, query: str, limit: int = 10) -> List[Dict]:
        return []
        
    async def get_manga_chapters(self, manga_id: str, limit: int = 20, offset: int = 0, languages: list = ['en']) -> List[Dict]:
        return []

    async def get_chapter_info(self, chapter_id: str) -> Optional[Dict]:
        """Fetch chapter info from WebCentral page"""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(chapter_id, timeout=30) as resp:
                    if resp.status != 200: 
                        return {'id': chapter_id, 'chapter': '0', 'title': 'Unknown', 'manga_title': 'WebCentral', 'manga_id': chapter_id}
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    manga_title = "Unknown"
                    series_link = soup.find("a", href=re.compile(r"/series/"))
                    if series_link:
                        manga_title = series_link.get_text(strip=True)
                    
                    chapter_num = "0"
                    selected_option = soup.find("option", selected=True)
                    if selected_option:
                        txt = selected_option.get_text(strip=True)
                        match = re.search(r"Chapter\s+(\d+(?:\.\d+)?)", txt, re.I)
                        if match: chapter_num = match.group(1)
                    
                    if chapter_num == "0":
                        page_title = soup.title.string if soup.title else ""
                        match = re.search(r"Chapter\s+(\d+(?:\.\d+)?)", page_title, re.I)
                        if match: chapter_num = match.group(1)

                    return {
                        'id': hashlib.md5(chapter_id.encode()).hexdigest(),
                        'chapter': chapter_num,
                        'title': '',
                        'manga_title': manga_title,
                        'manga_id': series_link['href'] if series_link else chapter_id
                    }
        except Exception as e:
            logger.error(f"WebCentral get_chapter_info failed: {e}")
            return None


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat
