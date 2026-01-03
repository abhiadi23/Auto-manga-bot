# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
# Support group @rexbotschat

import logging
import asyncio
import aiohttp
import aiofiles
import gc
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from PIL import Image, ImageDraw, ImageFont, ImageColor
import zipfile
import re
import pypdf

try:
    from curl_cffi import requests as curl_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False
    logging.warning("⚠️ curl_cffi not available - some CDN-protected images may fail to download")
    logging.warning("Install with: pip install curl-cffi")

logger = logging.getLogger(__name__)

class Downloader:
    def __init__(self, Config):
        self.Config = Config
        self.session = None

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=120, connect=30)
        self.session = aiohttp.ClientSession(
            headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://mangadex.org/'},
            timeout=timeout
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            await asyncio.sleep(0.25)

    def download_image_sync_curl(self, url: str, output_path: Path, referer: str = None, max_retries: int = 3) -> bool:
        """
        Synchronous download using curl_cffi to bypass CDN protection
        Use this for 2xstorage.com and other protected CDNs
        """
        if not CURL_CFFI_AVAILABLE:
            logger.warning(f"curl_cffi not available, cannot download: {url}")
            return False
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site',
        }
        
        if referer:
            headers['Referer'] = referer
        
        for attempt in range(max_retries):
            try:
                logger.info(f"📥 [{attempt + 1}/{max_retries}] Downloading: {url}")
                
                response = curl_requests.get(
                    url,
                    headers=headers,
                    impersonate="chrome120",  # This bypasses Cloudflare
                    timeout=60,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    size = len(response.content)
                    
                    if size > self.Config.MAX_IMAGE_SIZE:
                        logger.error(f"❌ Image too large: {size} bytes")
                        return False
                    
                    # Save to file
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    
                    logger.info(f"✅ Downloaded: {url} ({size / 1024:.1f} KB)")
                    return True
                
                elif response.status_code == 403:
                    logger.warning(f"⚠️ 403 Forbidden: {url}")
                    if attempt < max_retries - 1:
                        delay = 2 ** (attempt + 1)  # 2s, 4s, 8s
                        logger.info(f"⏳ Waiting {delay}s before retry...")
                        import time
                        time.sleep(delay)
                    continue
                
                elif response.status_code == 429:
                    logger.warning(f"⚠️ Rate limited (429): {url}")
                    delay = 2 ** (attempt + 2)  # 4s, 8s, 16s
                    logger.info(f"⏳ Waiting {delay}s before retry...")
                    import time
                    time.sleep(delay)
                    continue
                
                else:
                    logger.error(f"❌ HTTP {response.status_code}: {url}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(2 ** attempt)
                    continue
                    
            except Exception as e:
                logger.error(f"❌ Download error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)
        
        logger.error(f"❌ All {max_retries} attempts failed: {url}")
        return False

    async def download_image(self, url: str, output_path: Path, max_retries: int = 3, headers: dict = None, referer: str = None) -> bool:
        """
        Download image with automatic fallback:
        1. Try curl_cffi first (for CDN-protected images)
        2. Fall back to aiohttp if curl_cffi not available
        """
        # Detect if URL is from a protected CDN
        protected_domains = [
            '2xstorage.com',
            'cloudflare',
            'imgcdn',
            'scans-ongoing-1.lastation.us',
            'scans-ongoing-2.lastation.us'
        ]
        
        is_protected = any(domain in url.lower() for domain in protected_domains)
        
        # For protected CDNs, use curl_cffi
        if is_protected and CURL_CFFI_AVAILABLE:
            logger.info(f"🔒 Detected protected CDN, using curl_cffi: {url}")
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                self.download_image_sync_curl,
                url,
                output_path,
                referer,
                max_retries
            )
        
        # For non-protected or if curl_cffi unavailable, use aiohttp
        logger.info(f"📥 Using aiohttp: {url}")
        for attempt in range(max_retries):
            try:
                request_headers = headers if headers else self.session.headers
                
                # Add referer if provided
                if referer:
                    request_headers = dict(request_headers)
                    request_headers['Referer'] = referer
                
                async with self.session.get(url, headers=request_headers) as response:
                    if response.status == 429:
                        delay = 2 ** attempt
                        logger.warning(f"⚠️ Rate limited, waiting {delay}s...")
                        await asyncio.sleep(delay)
                        continue
                    
                    if response.status == 403:
                        logger.warning(f"⚠️ 403 Forbidden with aiohttp: {url}")
                        if CURL_CFFI_AVAILABLE:
                            logger.info("🔄 Switching to curl_cffi...")
                            loop = asyncio.get_event_loop()
                            return await loop.run_in_executor(
                                None,
                                self.download_image_sync_curl,
                                url,
                                output_path,
                                referer,
                                max_retries
                            )
                        else:
                            logger.error("❌ curl_cffi not available, cannot bypass protection")
                            return False
                    
                    response.raise_for_status()

                    size = 0
                    async with aiofiles.open(output_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            size += len(chunk)
                            if size > self.Config.MAX_IMAGE_SIZE:
                                logger.error(f"❌ Image too large: {size} bytes")
                                return False
                            await f.write(chunk)
                    
                    logger.info(f"✅ Downloaded: {url} ({size / 1024:.1f} KB)")
                    return True
                    
            except Exception as e:
                logger.error(f"❌ Download failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
        
        return False

    async def download_images(self, urls: List[str], output_dir: Path, progress_callback=None, headers: dict = None, referer: str = None) -> bool:
        """
        Download multiple images with progress tracking
        Now supports referer for CDN-protected images
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        batch_size = 10
        successful = 0

        logger.info(f"📚 Starting download of {len(urls)} images")
        logger.info(f"   Output: {output_dir}")
        if referer:
            logger.info(f"   Referer: {referer}")

        for i in range(0, len(urls), batch_size):
            tasks = []
            for j, url in enumerate(urls[i:i + batch_size], i + 1):
                output_path = output_dir / f"{j:03d}.jpg"
                tasks.append(self.download_image(url, output_path, headers=headers, referer=referer))
            
            # Add delay between batches for CDN protection
            if i > 0:
                await asyncio.sleep(1.5)  # 1.5s delay between batches

            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful += sum(1 for r in results if r is True)
            
            if progress_callback:
                try:
                    await progress_callback(successful, len(urls))
                except Exception:
                    pass
            
            logger.info(f"📊 Progress: {successful}/{len(urls)} images downloaded")
                    
            gc.collect()
            await asyncio.sleep(0.5)

        success_rate = successful / len(urls) if urls else 0
        logger.info(f"✅ Download complete: {successful}/{len(urls)} images ({success_rate:.1%})")
        
        return success_rate >= 0.8

    def create_pdf(self, chapter_dir: Path, manga_title: str, chapter_num: str, chapter_title: str) -> Optional[Path]:
        try:
            base_name = f"{manga_title} - Ch {chapter_num}"
            if chapter_title:
                base_name += f" - {chapter_title}"
            safe_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_'))[:100]
            pdf_path = chapter_dir.parent / f"{safe_name}.pdf"

            img_files = sorted(chapter_dir.glob("*.jpg"))
            if not img_files:
                return None

            images_to_save = []
            first_image = None

            for i, img_path in enumerate(img_files):
                img = Image.open(img_path)
                if img.width > 2000 or img.height > 2000:
                    ratio = min(2000 / img.width, 2000 / img.height)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                if i == 0:
                    first_image = img
                else:
                    images_to_save.append(img)

                if i % 20 == 0:
                    gc.collect()

            if not first_image:
                return None

            first_image.save(
                pdf_path, "PDF", resolution=72.0, save_all=True,
                append_images=images_to_save, optimize=True
            )

            if pdf_path.stat().st_size > self.Config.MAX_PDF_SIZE:
                logger.error(f"PDF too large: {pdf_path.stat().st_size} bytes")
                pdf_path.unlink()
                return None

            for img in images_to_save:
                img.close()
            first_image.close()
            gc.collect()

            return pdf_path
        except Exception as e:
            logger.error(f"PDF creation failed: {e}")
            return None

    def create_cbz(self, chapter_dir: Path, manga_title: str, chapter_num: str, chapter_title: str, intro: Path = None, outro: Path = None, quality: int = None) -> Optional[Path]:
        try:
            base_name = f"{manga_title} - Ch {chapter_num}"
            if chapter_title:
                base_name += f" - {chapter_title}"
            safe_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_'))[:100]
            cbz_path = chapter_dir.parent / f"{safe_name}.cbz"

            img_files = sorted(chapter_dir.glob("*.jpg"))
            if not img_files:
                return None
            
            final_images = []
            if intro and intro.exists(): final_images.append(intro)
            final_images.extend(img_files)
            if outro and outro.exists(): final_images.append(outro)

            with zipfile.ZipFile(cbz_path, 'w', zipfile.ZIP_DEFLATED) as cbz:
                for idx, img_path in enumerate(final_images):
                    if quality is not None:
                         try:
                             with Image.open(img_path) as img:
                                 if img.mode != 'RGB': img = img.convert('RGB')
                                 with cbz.open(f"{idx:04d}.jpg", "w") as zf:
                                     img.save(zf, "JPEG", quality=quality, optimize=True)
                         except:
                             cbz.write(img_path, arcname=f"{idx:04d}.jpg")
                    else:
                        cbz.write(img_path, arcname=f"{idx:04d}.jpg")
            
            return cbz_path
        except Exception as e:
            logger.error(f"CBZ creation failed: {e}")
            return None

    def create_chapter_file(self, chapter_dir: Path, manga_title: str, chapter_num: str, chapter_title: str, file_type: str = "pdf", intro: Path = None, outro: Path = None, quality: int = None, watermark: dict = None, password: str = None) -> Optional[Path]:
        """Dispatcher for creating chapter file based on type"""
        if file_type.lower() == "cbz":
            return self.create_cbz(chapter_dir, manga_title, chapter_num, chapter_title, intro, outro, quality)
        else:
            return self.create_pdf_v2(chapter_dir, manga_title, chapter_num, chapter_title, intro, outro, quality, watermark, password=password)

    def apply_watermark(self, img: Image.Image, watermark: dict) -> Image.Image:
        if not watermark or not watermark.get("text"):
            return img
        
        try:
            draw = ImageDraw.Draw(img, "RGBA")
            text = watermark["text"]
            position = watermark.get("position", "bottom-right")
            color_hex = watermark.get("color", "#FFFFFF")
            opacity = int(watermark.get("opacity", 128))
            font_size = int(watermark.get("font_size", 30))
            
            try:
                rgb = ImageColor.getrgb(color_hex)
            except:
                rgb = (255, 255, 255)
            
            fill_color = (*rgb, opacity)
            
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            width, height = img.size
            padding = 20
            
            x, y = 0, 0
            if position == "top-left":
                x, y = padding, padding
            elif position == "top-right":
                x, y = width - text_width - padding, padding
            elif position == "bottom-left":
                x, y = padding, height - text_height - padding
            elif position == "bottom-right":
                x, y = width - text_width - padding, height - text_height - padding
            elif position == "center":
                x, y = (width - text_width) // 2, (height - text_height) // 2
                
            draw.text((x, y), text, font=font, fill=fill_color)
            return img
        except Exception as e:
            logger.error(f"Watermark apply failed: {e}")
            return img

    def apply_password(self, pdf_path: Path, password: str) -> bool:
        """Apply password protection to PDF"""
        if not password: return True
        try:
            reader = pypdf.PdfReader(pdf_path)
            writer = pypdf.PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
            
            writer.encrypt(password)
            
            temp_path = pdf_path.with_suffix('.temp.pdf')
            with open(temp_path, "wb") as f:
                writer.write(f)
            
            pdf_path.unlink()
            temp_path.rename(pdf_path)
            return True
        except Exception as e:
            logger.error(f"Password protection failed: {e}")
            return False

    def create_pdf_v2(self, chapter_dir: Path, manga_title: str, chapter_num: str, chapter_title: str, intro: Path = None, outro: Path = None, quality: int = None, watermark: dict = None, password: str = None) -> Optional[Path]:
         try:
            clean_title = re.sub(r'\[Ch-.*?\]', '', manga_title, flags=re.IGNORECASE)
            clean_title = re.sub(r'\s*-\s*Chapter\s*\d+', '', clean_title, flags=re.IGNORECASE)
            clean_title = clean_title.strip()
            
            base_name = f"{clean_title} - Ch {chapter_num}"
            if chapter_title:
                base_name += f" - {chapter_title}"
            safe_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_'))[:100]
            pdf_path = chapter_dir.parent / f"{safe_name}.pdf"

            img_files = sorted(chapter_dir.glob("*.jpg"))
            if not img_files:
                return None

            final_images = []
            if intro and intro.exists(): final_images.append(intro)
            final_images.extend(img_files)
            if outro and outro.exists(): final_images.append(outro)

            images_to_save = []
            first_image = None
            
            q = quality if quality is not None else 85
            
            for i, img_path in enumerate(final_images):
                img = Image.open(img_path)
                if img.width > 2000 or img.height > 2000:
                    ratio = min(2000 / img.width, 2000 / img.height)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                if watermark:
                    img = self.apply_watermark(img, watermark)

                if i == 0:
                    first_image = img
                else:
                    images_to_save.append(img)

                if i % 20 == 0:
                    gc.collect()

            if not first_image:
                return None

            first_image.save(
                pdf_path, "PDF", resolution=72.0, save_all=True,
                append_images=images_to_save, optimize=True, quality=q
            )
            
            for img in images_to_save: img.close()
            first_image.close()
            gc.collect()
            
            if password:
                self.apply_password(pdf_path, password)
            
            return pdf_path
         except Exception as e:
             logger.error(f"PDF v2 failed: {e}")
             return None

    async def download_cover(self, cover_url: str, output_path: Path, headers: dict = None) -> bool:
        if not cover_url:
            return False
        return await self.download_image(cover_url, output_path, headers=headers)


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
# Support group @rexbotschat
