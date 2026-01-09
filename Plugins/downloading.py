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
from typing import List, Dict, Optional, Callable, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageColor
import zipfile
import re
import pypdf
from pyrogram.errors import FileReferenceExpired, FloodWait, BadRequest
from pyrogram import Client

logger = logging.getLogger(__name__)

class Downloader:
    def __init__(self, Config):
        self.Config = Config
        self.bot = None  # Store bot instance for message refresh

    def set_bot(self, bot: Client):
        """Set the Pyrogram bot instance for file operations"""
        self.bot = bot

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

    async def get_fresh_file_url(self, chat_id: int, message_id: int) -> Tuple[Optional[str], Optional[str]]:
        """
        Refresh message and get new file_id and download URL
        This is the critical function that fixes FILE_REFERENCE_EXPIRED
        """
        if not self.bot:
            logger.error("Bot instance not set. Call set_bot() first.")
            return None, None
        
        try:
            # Re-fetch the message to get fresh file reference
            message = await self.bot.get_messages(chat_id, message_id)
            
            if not message:
                logger.error(f"Could not fetch message {message_id}")
                return None, None
            
            # Extract file info based on media type
            file_id = None
            if message.photo:
                file_id = message.photo.file_id
            elif message.document:
                file_id = message.document.file_id
            elif message.video:
                file_id = message.video.file_id
            else:
                logger.error(f"Message {message_id} has no supported media")
                return None, None
            
            # Get the file path with fresh reference
            file = await self.bot.get_file(file_id)
            file_url = f"https://api.telegram.org/file/bot{self.bot.bot_token}/{file.file_path}"
            
            logger.info(f"Successfully refreshed file reference for message {message_id}")
            return file_id, file_url
            
        except FileReferenceExpired as e:
            logger.error(f"FILE_REFERENCE_EXPIRED even after message refresh: {e}")
            return None, None
        except FloodWait as e:
            logger.warning(f"FloodWait {e.value}s while refreshing message")
            await asyncio.sleep(e.value)
            return None, None
        except Exception as e:
            logger.error(f"Error refreshing message {message_id}: {type(e).__name__}: {e}")
            return None, None

    async def download_image(
        self, 
        url: str, 
        output_path: Path, 
        max_retries: int = 3, 
        headers: dict = None, 
        file_id: str = None, 
        get_file_callback: Callable = None,
        message_id: int = None,
        chat_id: int = None,
        refresh_message_callback: Callable = None
    ) -> bool:
        """
        Download image with comprehensive FILE_REFERENCE_EXPIRED handling
        """
        current_file_id = file_id
        current_url = url
        
        for attempt in range(max_retries):
            try:
                # CRITICAL: Refresh file reference on retry
                if attempt > 0 and message_id and chat_id:
                    logger.info(f"Attempt {attempt + 1}/{max_retries}: Refreshing file reference for message {message_id}")
                    
                    # Use custom callback if provided, otherwise use built-in method
                    if refresh_message_callback:
                        new_file_id, new_url = await refresh_message_callback(chat_id, message_id)
                    else:
                        new_file_id, new_url = await self.get_fresh_file_url(chat_id, message_id)
                    
                    if new_file_id and new_url:
                        current_file_id = new_file_id
                        current_url = new_url
                        logger.info(f"✓ Got fresh file reference")
                        await asyncio.sleep(1)  # Small delay to avoid rate limiting
                    else:
                        logger.error(f"✗ Failed to refresh file reference")
                        if attempt == max_retries - 1:
                            return False
                        await asyncio.sleep(2 ** attempt)
                        continue
                
                request_headers = headers if headers else self.session.headers
                
                async with self.session.get(current_url, headers=request_headers) as response:
                    # Handle rate limiting
                    if response.status == 429:
                        retry_after = int(response.headers.get('Retry-After', min(2 ** attempt, 10)))
                        logger.warning(f"Rate limited. Waiting {retry_after}s")
                        await asyncio.sleep(retry_after)
                        continue
                    
                    # Handle expired file reference in HTTP response
                    if response.status == 400:
                        error_text = await response.text()
                        if 'FILE_REFERENCE_EXPIRED' in error_text or 'file reference' in error_text.lower():
                            logger.warning(f"FILE_REFERENCE_EXPIRED in HTTP response")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(2 ** attempt)
                                continue
                            return False
                        else:
                            logger.error(f"HTTP 400: {error_text[:200]}")
                            return False
                    
                    # Non-retriable client errors
                    if 400 <= response.status < 500 and response.status not in [400, 429]:
                        logger.error(f"Client error {response.status}")
                        return False
                    
                    response.raise_for_status()

                    # Download with size check and memory management
                    size = 0
                    async with aiofiles.open(output_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            size += len(chunk)
                            if size > self.Config.MAX_IMAGE_SIZE:
                                logger.error(f"Image too large: {size} bytes")
                                try:
                                    output_path.unlink(missing_ok=True)
                                except:
                                    pass
                                return False
                            await f.write(chunk)
                    
                    logger.debug(f"✓ Downloaded {output_path.name} ({size} bytes)")
                    return True
                    
            except FileReferenceExpired as e:
                logger.warning(f"⚠ FILE_REFERENCE_EXPIRED caught (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1 and (message_id and chat_id):
                    await asyncio.sleep(2 ** attempt)
                    continue
                logger.error("Cannot recover from FILE_REFERENCE_EXPIRED")
                return False
                    
            except FloodWait as e:
                logger.warning(f"⚠ FloodWait: {e.value}s")
                await asyncio.sleep(e.value)
                # Don't count as retry
                max_retries += 1
                continue
                    
            except aiohttp.ClientResponseError as e:
                logger.error(f"HTTP error {e.status} (attempt {attempt + 1}/{max_retries})")
                if e.status == 400 and attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    
            except asyncio.TimeoutError:
                logger.error(f"Timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    
            except Exception as e:
                logger.error(f"Error (attempt {attempt + 1}/{max_retries}): {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
        
        # Cleanup failed download
        try:
            if output_path.exists():
                output_path.unlink()
        except:
            pass
            
        logger.error(f"✗ Failed to download after {max_retries} attempts")
        return False

    async def download_images(
        self, 
        urls: List[str], 
        output_dir: Path, 
        progress_callback=None, 
        headers: dict = None, 
        file_ids: List[str] = None, 
        get_file_callback: Callable = None,
        message_ids: List[int] = None,
        chat_id: int = None,
        refresh_message_callback: Callable = None
    ) -> bool:
        """Download multiple images with proper error handling and memory management"""
        output_dir.mkdir(parents=True, exist_ok=True)
        batch_size = 2  # Reduced for Heroku memory limits
        successful = 0
        failed_items = []

        for i in range(0, len(urls), batch_size):
            batch_end = min(i + batch_size, len(urls))
            tasks = []
            
            for j in range(i, batch_end):
                url = urls[j]
                output_path = output_dir / f"{j + 1:03d}.jpg"
                file_id = file_ids[j] if file_ids and len(file_ids) > j else None
                message_id = message_ids[j] if message_ids and len(message_ids) > j else None
                
                tasks.append(
                    self.download_image(
                        url, 
                        output_path, 
                        headers=headers, 
                        file_id=file_id, 
                        get_file_callback=get_file_callback,
                        message_id=message_id,
                        chat_id=chat_id,
                        refresh_message_callback=refresh_message_callback
                    )
                )

            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for idx, result in enumerate(results):
                actual_idx = i + idx
                if isinstance(result, Exception):
                    logger.error(f"Image {actual_idx + 1} failed: {result}")
                    failed_items.append((actual_idx, str(result)))
                elif result is True:
                    successful += 1
                else:
                    failed_items.append((actual_idx, "Download failed"))
            
            # Progress update
            if progress_callback:
                try:
                    await progress_callback(successful, len(urls))
                except Exception as e:
                    logger.error(f"Progress callback error: {e}")
            
            # Critical: Force garbage collection to prevent memory issues
            gc.collect()
            await asyncio.sleep(2)  # Longer pause for stability

        # Retry failed items
        if failed_items and chat_id:
            logger.info(f"Retrying {len(failed_items)} failed downloads")
            await asyncio.sleep(3)
            
            for idx, reason in failed_items[:]:
                url = urls[idx]
                output_path = output_dir / f"{idx + 1:03d}.jpg"
                message_id = message_ids[idx] if message_ids and len(message_ids) > idx else None
                
                if message_id:
                    try:
                        # Get fresh reference
                        if refresh_message_callback:
                            new_file_id, new_url = await refresh_message_callback(chat_id, message_id)
                        else:
                            new_file_id, new_url = await self.get_fresh_file_url(chat_id, message_id)
                        
                        if new_file_id and new_url:
                            result = await self.download_image(
                                new_url,
                                output_path,
                                max_retries=2,
                                headers=headers,
                                file_id=new_file_id,
                                message_id=message_id,
                                chat_id=chat_id,
                                refresh_message_callback=refresh_message_callback
                            )
                            if result:
                                successful += 1
                                failed_items.remove((idx, reason))
                    except Exception as e:
                        logger.error(f"Retry failed for image {idx + 1}: {e}")
                
                await asyncio.sleep(1.5)
                gc.collect()  # Force cleanup

        success_rate = successful / len(urls) if urls else 0
        logger.info(f"Downloaded {successful}/{len(urls)} images ({success_rate:.1%})")
        
        if failed_items:
            failed_indices = [idx for idx, _ in failed_items]
            logger.warning(f"Failed images: {failed_indices}")
        
        return success_rate >= 0.8

    def validate_image(self, img_path: Path) -> bool:
        """Validate image file"""
        if not img_path.exists() or img_path.stat().st_size == 0:
            return False
        try:
            with Image.open(img_path) as img:
                img.verify()
            return True
        except Exception as e:
            logger.error(f"Invalid image {img_path}: {e}")
            return False

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

                if i % 15 == 0:  # More frequent cleanup
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
                return False

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
            if intro and intro.exists() and self.validate_image(intro):
                final_images.append(intro)
            final_images.extend(img_files)
            if outro and outro.exists() and self.validate_image(outro):
                final_images.append(outro)

            with zipfile.ZipFile(cbz_path, 'w', zipfile.ZIP_DEFLATED) as cbz:
                for idx, img_path in enumerate(final_images):
                    if quality is not None:
                        try:
                            with Image.open(img_path) as img:
                                if img.mode != 'RGB': 
                                    img = img.convert('RGB')
                                with cbz.open(f"{idx:04d}.jpg", "w") as zf:
                                    img.save(zf, "JPEG", quality=quality, optimize=True)
                        except Exception as e:
                            logger.error(f"Failed to process {img_path}: {e}")
                            cbz.write(img_path, arcname=f"{idx:04d}.jpg")
                    else:
                        cbz.write(img_path, arcname=f"{idx:04d}.jpg")
                    
                    if idx % 15 == 0:
                        gc.collect()
            
            return cbz_path
        except Exception as e:
            logger.error(f"CBZ creation failed: {e}")
            return None

    def create_chapter_file(self, chapter_dir: Path, manga_title: str, chapter_num: str, chapter_title: str, file_type: str = "pdf", intro: Path = None, outro: Path = None, quality: int = None, watermark: dict = None, password: str = None) -> Optional[Path]:
        """Dispatcher for creating chapter file"""
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
            
            positions = {
                "top-left": (padding, padding),
                "top-right": (width - text_width - padding, padding),
                "bottom-left": (padding, height - text_height - padding),
                "bottom-right": (width - text_width - padding, height - text_height - padding),
                "center": ((width - text_width) // 2, (height - text_height) // 2)
            }
            x, y = positions.get(position, positions["bottom-right"])
                
            draw.text((x, y), text, font=font, fill=fill_color)
            return img
        except Exception as e:
            logger.error(f"Watermark failed: {e}")
            return img

    def apply_password(self, pdf_path: Path, password: str) -> bool:
        """Apply password protection to PDF"""
        if not password: 
            return True
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
            if intro and intro.exists() and self.validate_image(intro):
                final_images.append(intro)
            final_images.extend(img_files)
            if outro and outro.exists() and self.validate_image(outro):
                final_images.append(outro)

            images_to_save = []
            first_image = None
            q = quality if quality is not None else 85
            
            for i, img_path in enumerate(final_images):
                try:
                    if not self.validate_image(img_path):
                        continue
                    
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

                    if i % 15 == 0:
                        gc.collect()
                
                except Exception as e:
                    logger.error(f"Failed to process {img_path}: {e}")
                    continue

            if not first_image:
                return None

            first_image.save(
                pdf_path, "PDF", resolution=72.0, save_all=True,
                append_images=images_to_save, optimize=True, quality=q
            )
            
            for img in images_to_save: 
                img.close()
            first_image.close()
            gc.collect()
            
            if password:
                self.apply_password(pdf_path, password)
            
            return pdf_path
            
        except Exception as e:
            logger.error(f"PDF v2 failed: {e}", exc_info=True)
            return None

    async def download_cover(
        self, 
        cover_url: str, 
        output_path: Path, 
        headers: dict = None, 
        file_id: str = None, 
        get_file_callback: Callable = None,
        message_id: int = None,
        chat_id: int = None,
        refresh_message_callback: Callable = None
    ) -> bool:
        """Download cover image"""
        if not cover_url:
            return False
        return await self.download_image(
            cover_url, 
            output_path, 
            headers=headers, 
            file_id=file_id, 
            get_file_callback=get_file_callback,
            message_id=message_id,
            chat_id=chat_id,
            refresh_message_callback=refresh_message_callback
        )


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
# Support group @rexbotschat
