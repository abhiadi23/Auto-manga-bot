import logging
import aiohttp
import re
import asyncio
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MangakakalotAPI:
    def __init__(self, Config=None):
        self.Config = Config
        self.base_url = "https://mangakakalot.gg"
        self.latest_url = "https://mangakakalot.gg/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Referer': 'https://mangakakalot.gg/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

    def convert_webp_to_jpeg(self, url: str) -> str:
        """Convert .webp URLs to .jpeg"""
        if url.lower().endswith('.webp'):
            return url[:-5] + '.jpeg'
        return url

    def parse_upload_hours_ago(self, time_text: str) -> Optional[float]:
        if not time_text:
            return None
        
        time_text = time_text.strip().lower().replace(' ago', '')

        if 'current' in time_text or 'just now' in time_text:
            return 0.0

        minute_match = re.search(r'(\d+)\s*minute?', time_text)
        if minute_match:
            return int(minute_match.group(1)) / 60.0

        hour_match = re.search(r'(\d+)\s*hour?', time_text)
        if hour_match:
            return float(hour_match.group(1))

        day_match = re.search(r'(\d+)\s*day?', time_text)
        if day_match:
            return float(day_match.group(1)) * 24

        if re.search(r'\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2}', time_text):
            return None

        return None

    async def get_latest_chapters_method1(self, limit: int = 50) -> List[Dict]:
        """Original method - parse markdown-like text sections"""
        chapters = []
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(self.latest_url, timeout=60) as resp:
                    if resp.status != 200:
                        logger.error(f"Failed to fetch homepage: {resp.status}")
                        return []
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')

                latest_heading = soup.find(string=re.compile(r'##\s*LATEST\s+MANGA\s+RELEASES', re.I))
                if not latest_heading:
                    logger.warning("Method 1: LATEST MANGA RELEASES heading not found")
                    return []

                logger.info("Method 1: Found LATEST MANGA RELEASES section")

                text_block = ''
                current = latest_heading.next_element
                while current:
                    if isinstance(current, str) and re.match(r'^\s*##\s+', current.strip(), re.I):
                        break
                    if hasattr(current, 'name') and current.name in ['h1', 'h2', 'h3']:
                        break

                    if isinstance(current, str):
                        text_block += current
                    else:
                        text_block += current.get_text(separator='\n')

                    current = current.next_element

                lines = [line.strip() for line in text_block.split('\n') if line.strip()]
                logger.debug(f"Method 1: Extracted {len(lines)} lines from latest section")

                manga_pattern = re.compile(r'^\[(.+?)\]\((https?://[^)]+)\)$')
                chapter_pattern = re.compile(r'^\*\s*\[(.+?)\]\((https?://[^)]+)\)\s*\*(.+?)\*$')

                current_manga_title = None
                current_manga_url = None

                for line in lines:
                    if len(chapters) >= limit * 3:
                        break

                    manga_match = manga_pattern.match(line)
                    if manga_match:
                        current_manga_title = manga_match.group(1).strip()
                        current_manga_url = manga_match.group(2).strip()
                        current_manga_url = current_manga_url.replace('https://www.mangakakalot.gg', 'https://mangakakalot.gg')
                        logger.debug(f"Method 1: Found manga: {current_manga_title}")
                        continue

                    if not current_manga_title or not current_manga_url:
                        continue

                    chapter_match = chapter_pattern.match(line)
                    if chapter_match:
                        chapter_title = chapter_match.group(1).strip()
                        chapter_url = chapter_match.group(2).strip()
                        time_text = chapter_match.group(3).strip()

                        hours_ago = self.parse_upload_hours_ago(time_text)

                        if hours_ago is not None and hours_ago <= 24:
                            num_match = re.search(r'Chapter\s*([\d\.]+)', chapter_title, re.I)
                            chapter_num_str = num_match.group(1) if num_match else "0"

                            chapters.append({
                                'id': chapter_url,
                                'manga_id': current_manga_url,
                                'manga_title': current_manga_title,
                                'chapter': chapter_num_str,
                                'title': chapter_title,
                                'group': 'Mangakakalot',
                                'url': chapter_url,
                                'hours_ago': round(hours_ago, 2)
                            })

                            logger.info(f"Method 1: New chapter → {current_manga_title} - {chapter_title}")

                chapters.sort(key=lambda x: x['hours_ago'])
                logger.info(f"Method 1: Detected {len(chapters)} new chapters within the last 24 hours")

            except Exception as e:
                logger.error(f"Method 1 error: {e}", exc_info=True)

        return chapters[:limit]

    async def get_latest_chapters_method2(self, limit: int = 50) -> List[Dict]:
        """Method 2 - Parse HTML structure directly"""
        chapters = []
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(self.latest_url, timeout=60) as resp:
                    if resp.status != 200:
                        logger.error(f"Method 2: Failed to fetch homepage: {resp.status}")
                        return []
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')

                logger.info("Method 2: Parsing HTML structure for latest updates")

                possible_containers = soup.find_all(['div', 'section'], 
                    class_=re.compile(r'(latest|update|new|recent|item)', re.I))

                logger.debug(f"Method 2: Found {len(possible_containers)} possible containers")

                for container in possible_containers:
                    links = container.find_all('a', href=re.compile(r'/chapter[-_]|/read/'))
                    
                    for link in links:
                        try:
                            chapter_url = link.get('href', '')
                            if not chapter_url:
                                continue
                            
                            if not chapter_url.startswith('http'):
                                chapter_url = urljoin(self.base_url, chapter_url)
                            
                            chapter_title = link.get('title') or link.get_text(strip=True)
                            if not chapter_title:
                                continue
                            
                            time_elem = None
                            parent = link.parent
                            for _ in range(3):
                                if parent:
                                    time_elem = parent.find(['span', 'i', 'time'], 
                                        class_=re.compile(r'(time|date|ago)', re.I))
                                    if not time_elem:
                                        time_elem = parent.find(string=re.compile(r'\d+\s*(hour|minute|day)', re.I))
                                    if time_elem:
                                        break
                                    parent = parent.parent
                            
                            time_text = ''
                            if time_elem:
                                time_text = time_elem.get_text(strip=True) if hasattr(time_elem, 'get_text') else str(time_elem).strip()
                            
                            hours_ago = self.parse_upload_hours_ago(time_text) if time_text else 1.0
                            
                            if hours_ago is None or hours_ago > 24:
                                continue
                            
                            manga_title = 'Unknown'
                            manga_url = chapter_url
                            
                            manga_link = None
                            parent = link.parent
                            for _ in range(5):
                                if parent:
                                    all_links = parent.find_all('a', href=re.compile(r'/manga/|/read/'))
                                    for potential_manga_link in all_links:
                                        href_val = potential_manga_link.get('href', '')
                                        if href_val and '/chapter' not in href_val.lower():
                                            manga_link = potential_manga_link
                                            break
                                    if manga_link:
                                        break
                                    parent = parent.parent
                            
                            if manga_link:
                                manga_title = manga_link.get('title') or manga_link.get_text(strip=True)
                                manga_url = manga_link.get('href', '')
                                if manga_url and not manga_url.startswith('http'):
                                    manga_url = urljoin(self.base_url, manga_url)
                            else:
                                manga_url_match = re.search(r'(https?://[^/]+/[^/]+/[^/]+?)(?:/chapter|/read)', chapter_url, re.I)
                                if manga_url_match:
                                    manga_url = manga_url_match.group(1)
                            
                            num_match = re.search(r'Chapter\s*([\d\.]+)', chapter_title, re.I)
                            chapter_num_str = num_match.group(1) if num_match else "0"
                            
                            chapter_data = {
                                'id': chapter_url,
                                'manga_id': manga_url,
                                'manga_title': manga_title,
                                'chapter': chapter_num_str,
                                'title': chapter_title,
                                'group': 'Mangakakalot',
                                'url': chapter_url,
                                'hours_ago': round(hours_ago, 2)
                            }
                            
                            if not any(c['id'] == chapter_url for c in chapters):
                                chapters.append(chapter_data)
                                logger.info(f"Method 2: New chapter → {manga_title} - {chapter_title}")
                            
                            if len(chapters) >= limit * 2:
                                break
                        
                        except Exception as e:
                            logger.debug(f"Method 2: Error parsing link: {e}")
                            continue
                    
                    if len(chapters) >= limit * 2:
                        break

                chapters.sort(key=lambda x: x['hours_ago'])
                logger.info(f"Method 2: Detected {len(chapters)} chapters")

            except Exception as e:
                logger.error(f"Method 2 error: {e}", exc_info=True)

        return chapters[:limit]

    async def get_latest_chapters_method3(self, limit: int = 50) -> List[Dict]:
        """Method 3 - Use RSS feed or API endpoint if available"""
        return []

    async def get_latest_chapters(self, limit: int = 50) -> List[Dict]:
        """Main method that tries all scraping approaches"""
        logger.info("Starting chapter detection with multiple methods...")
        
        chapters = await self.get_latest_chapters_method1(limit)
        if chapters:
            logger.info(f"✅ Method 1 successful: {len(chapters)} chapters found")
            return chapters
        
        logger.info("Method 1 failed, trying Method 2...")
        chapters = await self.get_latest_chapters_method2(limit)
        if chapters:
            logger.info(f"✅ Method 2 successful: {len(chapters)} chapters found")
            return chapters
        
        logger.warning("❌ All methods failed to find chapters")
        return []

    async def get_chapter_images(self, chapter_url: str) -> Optional[List[str]]:
        """Get image URLs from chapter page - converts webp to jpeg"""
        images = []
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(chapter_url, timeout=60) as resp:
                    if resp.status != 200:
                        logger.error(f"Failed to fetch chapter page: {resp.status}")
                        return None
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')

                # Find the chapter reader container
                container = soup.find('div', class_='container-chapter-reader')
                if not container:
                    logger.warning("No chapter reader container found")
                    return None

                # Find all images in the container
                img_tags = container.find_all('img')
                
                for img in img_tags:
                    # Try multiple attributes for image source
                    src = img.get('src') or img.get('data-src') or img.get('data-original')
                    
                    if src:
                        # Skip GIFs and logos
                        if src.lower().endswith('.gif') or 'logo' in src.lower():
                            continue
                        
                        # Handle relative URLs
                        if not src.startswith('http'):
                            if src.startswith('//'):
                                src = 'https:' + src
                            else:
                                src = urljoin(self.base_url, src)
                        
                        # Convert webp to jpeg
                        src = self.convert_webp_to_jpeg(src.strip())
                        images.append(src)
                        
                        logger.debug(f"Image URL: {src}")
                
                if images:
                    logger.info(f"✅ Found {len(images)} images in chapter (converted webp to jpeg)")
                else:
                    logger.warning("No images found in chapter")

            except Exception as e:
                logger.error(f"get_chapter_images error: {e}")
                return None

        return images if images else None

    async def download_image(self, url: str, save_path: str) -> bool:
        """Download image from URL and save to file"""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=60) as resp:
                    if resp.status == 200:
                        with open(save_path, 'wb') as f:
                            f.write(await resp.read())
                        logger.info(f"✅ Downloaded: {save_path}")
                        return True
                    else:
                        logger.error(f"Failed to download {url}: Status {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return False

    async def download_chapter_images(self, chapter_url: str, save_dir: str) -> int:
        """Download all images from a chapter to a directory"""
        import os
        
        images = await self.get_chapter_images(chapter_url)
        if not images:
            logger.error("No images found to download")
            return 0
        
        # Create directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
        
        downloaded = 0
        for idx, image_url in enumerate(images, 1):
            filename = f"page_{idx:03d}.jpeg"
            save_path = os.path.join(save_dir, filename)
            
            if await self.download_image(image_url, save_path):
                downloaded += 1
        
        logger.info(f"✅ Downloaded {downloaded}/{len(images)} images to {save_dir}")
        return downloaded

    async def get_manga_info(self, manga_id: str) -> Optional[Dict]:
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(manga_id, timeout=60) as resp:
                    if resp.status != 200:
                        return {'id': manga_id, 'title': 'Unknown', 'cover_url': None}
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    title_elem = soup.find('h1') or soup.find('h2')
                    title = title_elem.get_text(strip=True) if title_elem else 'Unknown'

                    cover_div = soup.find('div', class_=re.compile(r'manga-info-pic|info-image', re.I))
                    cover_url = None
                    if cover_div:
                        img = cover_div.find('img')
                        if img:
                            cover_url = img.get('src') or img.get('data-src')

                    return {'id': manga_id, 'title': title, 'cover_url': cover_url}
        except Exception as e:
            logger.error(f"get_manga_info error: {e}")
            return None

    async def get_chapter_info(self, chapter_id: str) -> Optional[Dict]:
        try:
            parts = chapter_id.split('/')
            manga_id = '/'.join(parts[:-2]) if len(parts) >= 2 else chapter_id

            chapter_num = "0"
            num_match = re.search(r'chapter[-/](\d+(?:\.\d+)?)', chapter_id, re.I)
            if num_match:
                chapter_num = num_match.group(1)

            return {
                'id': chapter_id,
                'chapter': chapter_num,
                'title': '',
                'manga_title': 'Unknown',
                'manga_id': manga_id
            }
        except Exception:
            return None

    async def search_manga(self, query: str, limit: int = 10) -> List[Dict]:
        results = []
        search_url = f"{self.base_url}/search/{query.replace(' ', '_')}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(search_url, timeout=60) as resp:
                    if resp.status != 200:
                        return []
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    items = soup.find_all('div', class_='story_item')[:limit]
                    for item in items:
                        a_tag = item.find('a')
                        if not a_tag:
                            continue
                        title = a_tag.get('title') or a_tag.get_text(strip=True)
                        href = a_tag['href']
                        img = item.find('img')
                        cover = img['src'] if img and img.get('src') else None

                        results.append({
                            'id': urljoin(self.base_url, href),
                            'title': title,
                            'description': f"Mangakakalot: {title}",
                            'cover_url': cover
                        })
            except Exception as e:
                logger.error(f"search_manga error: {e}")

        return results
