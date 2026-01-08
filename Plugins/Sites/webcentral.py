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
        # Enhanced headers to bypass 403 blocking
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "DNT": "1",
            "Referer": "https://weebcentral.com/"
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def get_latest_chapters(self, limit: int = 50) -> List[Dict]:
        """Scrape latest updates from WebCentral Homepage"""
        chapters = []
        urls = [self.base_url]
        
        # Create session with SSL verification disabled and cookies enabled
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=60, connect=30)
        
        async with aiohttp.ClientSession(
            headers=self.headers, 
            connector=connector,
            timeout=timeout,
            cookie_jar=aiohttp.CookieJar()
        ) as session:
            for url in urls:
                try:
                    logger.info(f"Fetching WebCentral: {url}")
                    
                    # Add a small delay to appear more human-like
                    await asyncio.sleep(1)
                    
                    async with session.get(url, allow_redirects=True) as resp:
                        logger.info(f"Response status: {resp.status}")
                        
                        if resp.status == 403:
                            logger.error("403 Forbidden - Website is blocking requests. Trying alternative method...")
                            # Try with different user agent
                            alt_headers = self.headers.copy()
                            alt_headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
                            
                            await asyncio.sleep(2)
                            async with session.get(url, headers=alt_headers, allow_redirects=True) as resp2:
                                if resp2.status != 200:
                                    logger.error(f"Alternative method also failed: {resp2.status}")
                                    continue
                                resp = resp2
                        
                        if resp.status != 200:
                            logger.error(f"WebCentral returned status {resp.status}")
                            continue
                            
                        html = await resp.text()
                        
                        # Debug: Check if we got actual HTML
                        if len(html) < 1000:
                            logger.warning(f"Response seems too short ({len(html)} bytes), might be blocked")
                        
                        soup = BeautifulSoup(html, "html.parser")
                        
                        # Try multiple selectors to find chapter links
                        logger.info("Parsing page for chapter links...")
                        
                        # Method 1: Look for latest updates section
                        latest_section = soup.find(['div', 'section'], class_=re.compile(r'latest|update|recent', re.I))
                        if latest_section:
                            logger.info("Found latest updates section")
                            links = latest_section.find_all("a", href=True)
                        else:
                            # Method 2: Search all links
                            links = soup.find_all("a", href=True)
                        
                        logger.info(f"Found {len(links)} total links on page")
                        
                        seen_ids = set()
                        potential_chapters = []
                        
                        for a in links:
                            href = a.get("href", "")
                            
                            # Filter for chapter-like URLs (broader patterns)
                            if not any(keyword in href.lower() for keyword in ['/chapter', '/episode', '/read', '/manga', '/series']):
                                continue
                            
                            # Skip if it's just a series link without chapter
                            if '/series/' in href.lower() and '/chapter' not in href.lower():
                                continue
                            
                            full_url = urljoin(self.base_url, href)
                            text_content = a.get_text(separator=" ", strip=True)
                            
                            if not text_content or len(text_content) < 3:
                                continue
                            
                            # Try multiple regex patterns
                            manga_title = None
                            chap_num = None
                            
                            # Pattern 1: "Title Chapter 123" or "Title Episode 123"
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
                                
                except asyncio.TimeoutError:
                    logger.error("Request timed out")
                except aiohttp.ClientError as e:
                    logger.error(f"Client error: {e}")
                except Exception as e:
                    logger.error(f"WebCentral check failed: {e}", exc_info=True)
                    
        logger.info(f"Total chapters found: {len(chapters)}")
        return chapters

    async def get_manga_info(self, manga_id: str) -> Optional[Dict]:
        """Fetch manga info. Note: manga_id might be a chapter URL if scraped from latest."""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=60)
        
        try:
            async with aiohttp.ClientSession(
                headers=self.headers, 
                connector=connector,
                timeout=timeout
            ) as session:
                await asyncio.sleep(1)  # Rate limiting
                async with session.get(manga_id, allow_redirects=True) as resp:
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
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=60)
        
        async with aiohttp.ClientSession(
            headers=self.headers, 
            connector=connector,
            timeout=timeout,
            cookie_jar=aiohttp.CookieJar()
        ) as session:
            try:
                await asyncio.sleep(1)  # Rate limiting
                async with session.get(chapter_url, allow_redirects=True) as resp:
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
                
                await asyncio.sleep(0.5)
                async with session.get(api_url, headers=api_headers, allow_redirects=True) as resp:
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
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=60)
        
        try:
            async with aiohttp.ClientSession(
                headers=self.headers, 
                connector=connector,
                timeout=timeout
            ) as session:
                await asyncio.sleep(1)  # Rate limiting
                async with session.get(chapter_id, allow_redirects=True) as resp:
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
