# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat

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
import pypdf # Added for PDF password protection

logger = logging.getLogger(__name__)

class Downloader:
    def __init__(self, Config):
        self.Config = Config

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
        Download image with improved FILE_REFERENCE_EXPIRED handling
        
        Args:
            url: Direct download URL or Telegram file path
            output_path: Where to save the file
            max_retries: Maximum retry attempts
            headers: Optional HTTP headers
            file_id: Telegram file_id for refreshing
            get_file_callback: Callback to get fresh file URL (args: file_id)
            message_id: Message ID containing the file
            chat_id: Chat ID containing the message
            refresh_message_callback: Callback to refresh message and get new file_id (args: chat_id, message_id)
        """
        current_file_id = file_id
        
        for attempt in range(max_retries):
            try:
                # For Telegram files with expired references, refresh the message first
                if attempt > 0 and refresh_message_callback and message_id and chat_id:
                    try:
                        logger.info(f"Refreshing message {message_id} to get new file reference (attempt {attempt + 1}/{max_retries})")
                        new_file_id, new_url = await refresh_message_callback(chat_id, message_id)
                        if new_file_id and new_url:
                            current_file_id = new_file_id
                            url = new_url
                            logger.info(f"Got fresh file_id and URL from message refresh")
                            # Small delay to avoid rate limiting
                            await asyncio.sleep(1)
                        else:
                            logger.error("Failed to refresh message and get new file reference")
                            if attempt == max_retries - 1:
                                return False
                            await asyncio.sleep(2)
                            continue
                    except Exception as e:
                        logger.error(f"Error refreshing message: {e}")
                        if attempt == max_retries - 1:
                            return False
                        await asyncio.sleep(2)
                        continue
                
                # If we only have file_id callback (fallback method)
                elif attempt > 0 and get_file_callback and current_file_id and not refresh_message_callback:
                    try:
                        logger.info(f"Refreshing file reference for {current_file_id} (attempt {attempt + 1}/{max_retries})")
                        fresh_url = await get_file_callback(current_file_id)
                        if fresh_url:
                            url = fresh_url
                            logger.info("File reference refreshed via get_file")
                            await asyncio.sleep(1)
                        else:
                            logger.error("Failed to get fresh file URL")
                            if attempt == max_retries - 1:
                                return False
                            await asyncio.sleep(2)
                            continue
                    except Exception as e:
                        error_str = str(e).lower()
                        if 'file_reference_expired' in error_str or 'file reference' in error_str:
                            logger.warning(f"FILE_REFERENCE_EXPIRED during callback: {e}")
                            # Can't refresh without message context
                            if attempt == max_retries - 1:
                                return False
                            await asyncio.sleep(2)
                            continue
                        else:
                            logger.error(f"Error getting fresh file: {e}")
                            if attempt == max_retries - 1:
                                return False
                            await asyncio.sleep(2)
                            continue
                
                request_headers = headers if headers else self.session.headers
                
                async with self.session.get(url, headers=request_headers) as response:
                    # Handle rate limiting
                    if response.status == 429:
                        retry_after = int(response.headers.get('Retry-After', min(2 ** attempt, 10)))
                        logger.warning(f"Rate limited. Waiting {retry_after}s before retry")
                        await asyncio.sleep(retry_after)
                        continue
                    
                    # Handle FILE_REFERENCE_EXPIRED and related 400 errors
                    if response.status == 400:
                        error_text = await response.text()
                        if any(keyword in error_text.lower() for keyword in ['file_reference_expired', 'file reference', 'invalid file', 'file id']):
                            logger.warning(f"File reference expired in HTTP response (attempt {attempt + 1}/{max_retries})")
                            # Need message refresh for proper fix
                            if refresh_message_callback and message_id and chat_id:
                                await asyncio.sleep(min(2 ** attempt, 10))
                                continue
                            elif get_file_callback and current_file_id:
                                await asyncio.sleep(min(2 ** attempt, 10))
                                continue
                            else:
                                logger.error("Cannot refresh file reference - no refresh callback provided")
                                return False
                        else:
                            logger.error(f"HTTP 400 error: {error_text[:200]}")
                            return False
                    
                    # Handle other client errors (non-retriable)
                    if 400 <= response.status < 500 and response.status not in [400, 429]:
                        logger.error(f"Client error {response.status}: {await response.text()}")
                        return False
                    
                    # Raise for server errors
                    response.raise_for_status()

                    # Download with size check
                    size = 0
                    async with aiofiles.open(output_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            size += len(chunk)
                            if size > self.Config.MAX_IMAGE_SIZE:
                                logger.error(f"Image too large: {size} bytes (max: {self.Config.MAX_IMAGE_SIZE})")
                                # Clean up partial file
                                try:
                                    output_path.unlink(missing_ok=True)
                                except:
                                    pass
                                return False
                            await f.write(chunk)
                    
                    logger.debug(f"Successfully downloaded {output_path.name} ({size} bytes)")
                    return True
                    
            except aiohttp.ClientResponseError as e:
                # Special handling for 400 errors with file_id
                if e.status == 400:
                    logger.warning(f"HTTP 400 error, need to refresh file reference (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(min(2 ** attempt, 10))
                    continue
                    
                logger.error(f"Download failed with {e.status} (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(min(2 ** attempt, 10))
                    
            except asyncio.TimeoutError:
                logger.error(f"Download timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(min(2 ** attempt, 10))
                    
            except Exception as e:
                error_str = str(e).lower()
                # Detect Pyrogram FILE_REFERENCE_EXPIRED
                if 'file_reference_expired' in error_str or 'file reference' in error_str:
                    logger.warning(f"Pyrogram FILE_REFERENCE_EXPIRED detected (attempt {attempt + 1}/{max_retries})")
                    # Need to refresh via message
                    if attempt < max_retries - 1:
                        await asyncio.sleep(min(2 ** attempt, 10))
                        continue
                else:
                    logger.error(f"Download failed (attempt {attempt + 1}/{max_retries}): {type(e).__name__}: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(min(2 ** attempt, 10))
        
        # Clean up failed download
        try:
            if output_path.exists():
                output_path.unlink()
        except:
            pass
            
        logger.error(f"Failed to download after {max_retries} attempts")
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
        """
        Download multiple images with improved error handling and progress tracking
        
        Args:
            urls: List of URLs to download
            output_dir: Directory to save files
            progress_callback: Optional callback for progress updates
            headers: Optional HTTP headers
            file_ids: List of Telegram file_ids
            get_file_callback: Callback to get file URL from file_id
            message_ids: List of message IDs containing the files
            chat_id: Chat ID containing the messages
            refresh_message_callback: Callback to refresh messages and get new file data
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        batch_size = 3  # Reduced to 3 for better stability on Heroku
        successful = 0
        failed_items = []  # Store (index, reason) tuples

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

            # Execute batch with error collection
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for idx, result in enumerate(results):
                actual_idx = i + idx
                if isinstance(result, Exception):
                    logger.error(f"Image {actual_idx + 1} failed with exception: {result}")
                    failed_items.append((actual_idx, str(result)))
                elif result is True:
                    successful += 1
                else:
                    failed_items.append((actual_idx, "Unknown failure"))
            
            # Update progress
            if progress_callback:
                try:
                    await progress_callback(successful, len(urls))
                except Exception as e:
                    logger.error(f"Progress callback error: {e}")
            
            # Cleanup and pause between batches
            gc.collect()
            await asyncio.sleep(1.5)  # Increased pause for Heroku stability

        # Retry failed downloads with message refresh
        if failed_items and refresh_message_callback and chat_id:
            logger.info(f"Retrying {len(failed_items)} failed downloads with message refresh")
            await asyncio.sleep(2)
            
            for idx, reason in failed_items[:]:  # Copy list for safe removal
                url = urls[idx]
                output_path = output_dir / f"{idx + 1:03d}.jpg"
                message_id = message_ids[idx] if message_ids and len(message_ids) > idx else None
                
                if message_id:
                    try:
                        # Refresh message to get new file_id
                        logger.info(f"Final retry for image {idx + 1} with message refresh")
                        new_file_id, new_url = await refresh_message_callback(chat_id, message_id)
                        
                        if new_file_id and new_url:
                            result = await self.download_image(
                                new_url,
                                output_path,
                                max_retries=2,
                                headers=headers,
                                file_id=new_file_id,
                                get_file_callback=get_file_callback,
                                message_id=message_id,
                                chat_id=chat_id,
                                refresh_message_callback=refresh_message_callback
                            )
                            if result:
                                successful += 1
                                failed_items.remove((idx, reason))
                                logger.info(f"Successfully downloaded image {idx + 1} on retry")
                    except Exception as e:
                        logger.error(f"Final retry failed for image {idx + 1}: {e}")
                
                await asyncio.sleep(1)

        success_rate = successful / len(urls) if urls else 0
        logger.info(f"Downloaded {successful}/{len(urls)} images ({success_rate:.1%})")
        
        if failed_items:
            failed_indices = [idx for idx, _ in failed_items]
            logger.warning(f"Failed to download images at indices: {failed_indices}")
        
        return success_rate >= 0.8

    def validate_image(self, img_path: Path) -> bool:
        """Validate if file is a proper image"""
        if not img_path.exists():
            logger.error(f"Image file does not exist: {img_path}")
            return False
        
        if img_path.stat().st_size == 0:
            logger.error(f"Image file is empty: {img_path}")
            return False
        
        try:
            with Image.open(img_path) as img:
                img.verify()  # Verify it's a valid image
            return True
        except Exception as e:
            logger.error(f"Invalid image file {img_path}: {e}")
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
            
            # Validate intro image
            if intro and intro.exists() and self.validate_image(intro):
                final_images.append(intro)
            elif intro:
                logger.warning(f"Skipping invalid intro image: {intro}")
            
            final_images.extend(img_files)
            
            # Validate outro image
            if outro and outro.exists() and self.validate_image(outro):
                final_images.append(outro)
            elif outro:
                logger.warning(f"Skipping invalid outro image: {outro}")

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
                            logger.error(f"Failed to process image {img_path}: {e}")
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
            
            pdf_path.unlink()  # Delete unprotected
            temp_path.rename(pdf_path)  # Move protected
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
                logger.error("No image files found in chapter directory")
                return None

            final_images = []
            
            # Validate and add intro image
            if intro and intro.exists():
                if self.validate_image(intro):
                    final_images.append(intro)
                else:
                    logger.warning(f"Skipping invalid intro image: {intro}")
            elif intro:
                logger.warning(f"Intro image does not exist: {intro}")
            
            final_images.extend(img_files)
            
            # Validate and add outro image
            if outro and outro.exists():
                if self.validate_image(outro):
                    final_images.append(outro)
                else:
                    logger.warning(f"Skipping invalid outro image: {outro}")
            elif outro:
                logger.warning(f"Outro image does not exist: {outro}")

            images_to_save = []
            first_image = None
            
            q = quality if quality is not None else 85
            
            for i, img_path in enumerate(final_images):
                try:
                    # Validate before opening
                    if not self.validate_image(img_path):
                        logger.warning(f"Skipping invalid image: {img_path}")
                        continue
                    
                    img = Image.open(img_path)
                    
                    # Resize if needed
                    if img.width > 2000 or img.height > 2000:
                        ratio = min(2000 / img.width, 2000 / img.height)
                        new_size = (int(img.width * ratio), int(img.height * ratio))
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Convert to RGB
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Apply watermark
                    if watermark:
                        img = self.apply_watermark(img, watermark)

                    if i == 0:
                        first_image = img
                    else:
                        images_to_save.append(img)

                    if i % 20 == 0:
                        gc.collect()
                
                except Exception as e:
                    logger.error(f"Failed to process image {img_path}: {e}")
                    continue

            if not first_image:
                logger.error("No valid first image found for PDF creation")
                return None

            # Save PDF
            first_image.save(
                pdf_path, "PDF", resolution=72.0, save_all=True,
                append_images=images_to_save, optimize=True, quality=q
            )
            
            # Cleanup
            for img in images_to_save: 
                img.close()
            first_image.close()
            gc.collect()
            
            # Apply password protection
            if password:
                self.apply_password(pdf_path, password)
            
            logger.info(f"PDF created successfully: {pdf_path}")
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
        """Download cover image with proper error handling"""
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
#Supoort group @rexbotschat
