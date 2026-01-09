# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
# Support group @rexbotschat

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import Config
from Plugins.downloading import Downloader
from Plugins.Sites.mangadex import MangaDexAPI
from Plugins.Sites.mangaforest import MangaForestAPI
from Database.database import Seishiro
from Plugins.helper import edit_msg_with_pic, get_styled_text, user_states, user_data, WAITING_CHAPTER_INPUT
import logging
import asyncio
import shutil
from pathlib import Path
import os
import re

logger = logging.getLogger(__name__)

from Plugins.Sites.mangakakalot import MangakakalotAPI
from Plugins.Sites.allmanga import AllMangaAPI

SITES = {
    "MangaDex": MangaDexAPI,
    "MangaForest": MangaForestAPI,
    "Mangakakalot": MangakakalotAPI,
    "AllManga": AllMangaAPI,
    "WebCentral": None  # Placeholder until verified or imported
}

try:
    from Plugins.Sites.webcentral import WebCentralAPI
    SITES["WebCentral"] = WebCentralAPI
except ImportError:
    pass

def get_api_class(source):
    return SITES.get(source)

# Store search queries temporarily
search_queries = {}

@Client.on_message(filters.text & filters.private & ~filters.command(["start", "help", "settings", "search"]))
async def message_handler(client, message):
    user_id = message.from_user.id
    
    if user_id in user_states:
        if user_states[user_id] == WAITING_CHAPTER_INPUT:
            await custom_dl_input_handler(client, message)
            return
        return


@Client.on_message(filters.command("search") & filters.private)
async def search_command_handler(client, message):
    """Handle /search command for manga queries"""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("❌ ᴜꜱᴀɢᴇ: /search <query>")
        return
    
    query = parts[1].strip()
    if len(query) < 2:
        await message.reply("❌ ǫᴜᴇʀʏ ᴛᴏᴏ ꜱʜᴏʀᴛ.")
        return
    
    # Store the full query with user_id
    user_id = message.from_user.id
    search_queries[user_id] = query
    
    buttons = []
    row = []
    for source in SITES.keys():
        if SITES[source] is not None:
            # Only store source in callback, query retrieved from dict
            row.append(InlineKeyboardButton(source, callback_data=f"search_src_{source}_{user_id}"))
            if len(row) == 2:  # 2 buttons per row
                buttons.append(row)
                row = []
    
    if row:
        buttons.append(row)
    
    if not buttons:
        await message.reply("❌ ɴᴏ ꜱᴏᴜʀᴄᴇꜱ ᴀᴠᴀɪʟᴀʙʟᴇ.")
        return
        
    buttons.append([InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ", callback_data="stats_close")])
    
    await message.reply(
        f"<b>🔍 ꜱᴇᴀʀᴄʜ:</b> <code>{query}</code>\n\nꜱᴇʟᴇᴄᴛ ᴀ ꜱᴏᴜʀᴄᴇ ᴛᴏ ꜱᴇᴀʀᴄʜ ɪɴ:",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^search_src_"))
async def search_source_cb(client, callback_query):
    parts = callback_query.data.split("_", 3)
    source = parts[2]
    user_id = int(parts[3])
    
    # Retrieve the full query from storage
    query = search_queries.get(user_id)
    if not query:
        await callback_query.answer("ꜱᴇᴀʀᴄʜ ᴇxᴘɪʀᴇᴅ. ᴘʟᴇᴀꜱᴇ ꜱᴇᴀʀᴄʜ ᴀɢᴀɪɴ.", show_alert=True)
        return
    
    api_class = get_api_class(source)
    if not api_class:
        await callback_query.answer("ꜱᴏᴜʀᴄᴇ ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ", show_alert=True)
        return
        
    status_msg = await callback_query.message.edit_text(
        f"<i>🔍 ꜱᴇᴀʀᴄʜɪɴɢ {source}...</i>", 
        parse_mode=enums.ParseMode.HTML
    )
    
    try:
        async with api_class(Config) as api:
            results = await api.search_manga(query)
    except Exception as e:
        logger.error(f"Search error for {source}: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ ᴇʀʀᴏʀ ꜱᴇᴀʀᴄʜɪɴɢ {source}: {str(e)}")
        return
    
    if not results:
        await status_msg.edit_text(f"❌ ɴᴏ ʀᴇꜱᴜʟᴛꜱ ꜰᴏᴜɴᴅ ɪɴ {source}.")
        return

    buttons = []
    for m in results[:10]:  # Top 10
        title = m['title']
        buttons.append([InlineKeyboardButton(title, callback_data=f"view_{source}_{m['id']}")])
    
    buttons.append([InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ", callback_data="stats_close")])
    
    await status_msg.edit_text(
        f"<b>ꜰᴏᴜɴᴅ {len(results)} ʀᴇꜱᴜʟᴛꜱ ɪɴ {source}:</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^view_"))
async def view_manga_cb(client, query: CallbackQuery):
    parts = query.data.split(":")
    # Validate we have enough parts
    if len(parts) < 3:
        await query.answer("⚠️ Invalid callback data. Please search again.", show_alert=True)
        logger.error(f"Invalid callback data: {query.data}")
        return
        
        action = parts[0]  # "view_manga"
        source = parts[1]   # e.g., "mangadex", "asura"
        manga_id = parts[2] # The manga ID
        
        # Optional: validate manga_id is not empty
        if not manga_id or manga_id.strip() == "":
            await query.answer("⚠️ Invalid manga ID. Please try again.", show_alert=True)
            return
    
    api_class = get_api_class(source)
    if not api_class:
        return

    async with api_class(Config) as api:
        info = await api.get_manga_info(manga_id)
    
    if not info:
        await callback_query.answer("ᴇʀʀᴏʀ ꜰᴇᴛᴄʜɪɴɢ ᴅᴇᴛᴀɪʟꜱ", show_alert=True)
        return

    caption = (
        f"<b>📖 {info['title']}</b>\n"
        f"<b>ꜱᴏᴜʀᴄᴇ:</b> {source}\n"
        f"<b>ɪᴅ:</b> <code>{manga_id}</code>\n\n"
        f"ꜱᴇʟᴇᴄᴛ ᴀɴ ᴏᴘᴛɪᴏɴ:"
    )
    
    buttons = [
        [InlineKeyboardButton("⬇ ᴅᴏᴡɴʟᴏᴀᴅ ᴄʜᴀᴘᴛᴇʀꜱ", callback_data=f"chapters_{source}_{manga_id}_0")],
        [InlineKeyboardButton("⬇ ᴄᴜꜱᴛᴏᴍ ᴅᴏᴡɴʟᴏᴀᴅ (ʀᴀɴɢᴇ)", callback_data=f"custom_dl_{source}_{manga_id}")],
        [InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ", callback_data="stats_close")] 
    ]
    
    msg = callback_query.message
    await edit_msg_with_pic(msg, caption, InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^chapters_"))
async def chapters_list_cb(client, callback_query):
    parts = callback_query.data.split("_")
    if len(parts) < 4:
        await callback_query.answer("❌ ɪɴᴠᴀʟɪᴅ ᴄᴀʟʟʙᴀᴄᴋ ᴅᴀᴛᴀ", show_alert=True)
        return
    
    source = parts[1]
    offset = int(parts[-1])  # Last part is always offset
    manga_id = "_".join(parts[2:-1])  # Everything between source and offset
    
    api_class = get_api_class(source)
    async with api_class(Config) as api:
        chapters = await api.get_manga_chapters(manga_id, limit=10, offset=offset)
    
    if not chapters and offset == 0:
        await callback_query.answer("ɴᴏ ᴄʜᴀᴘᴛᴇʀꜱ ꜰᴏᴜɴᴅ.", show_alert=True)
        return
    elif not chapters:
        await callback_query.answer("ɴᴏ ᴍᴏʀᴇ ᴄʜᴀᴘᴛᴇʀꜱ.", show_alert=True)
        return

    buttons = []
    row = []
    for ch in chapters:
        ch_num = ch['chapter']
        btn_text = f"ᴄʜ {ch_num}"
        
        row.append(InlineKeyboardButton(btn_text, callback_data=f"dl_ask_{source}_{manga_id}_{ch['id'][:20]}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    nav = []
    if offset >= 10:
        nav.append(InlineKeyboardButton("⬅ ᴘʀᴇᴠ", callback_data=f"chapters_{source}_{manga_id}_{offset-10}"))
    nav.append(InlineKeyboardButton("ɴᴇxᴛ ➡", callback_data=f"chapters_{source}_{manga_id}_{offset+10}"))
    buttons.append(nav)
    
    buttons.append([InlineKeyboardButton("⬅ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɴɢᴀ", callback_data=f"view_{source}_{manga_id}")])
    
    caption_text = f"<b>ꜱᴇʟᴇᴄᴛ ᴄʜᴀᴘᴛᴇʀ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ (ꜱᴛᴀɴᴅᴀʀᴅ):</b>\nᴘᴀɢᴇ: {int(offset/10)+1}\n<i>ɴᴏᴛᴇ: ᴜᴘʟᴏᴀᴅꜱ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛ ᴄʜᴀɴɴᴇʟ.</i>"
    
    try:
        if callback_query.message.photo:
            await callback_query.message.edit_caption(caption=caption_text, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await callback_query.message.edit_text(caption_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        print(f"ᴇᴅɪᴛ ᴇʀʀᴏʀ: {e}")


@Client.on_callback_query(filters.regex("^custom_dl_"))
async def custom_dl_start_cb(client, callback_query):
    parts = callback_query.data.split("_")
    source = parts[2]
    manga_id = "_".join(parts[3:])
    
    user_id = callback_query.from_user.id
    
    user_states[user_id] = WAITING_CHAPTER_INPUT
    user_data[user_id] = {
        'source': source,
        'manga_id': manga_id
    }
    
    await callback_query.message.reply_text(
        "<b>⬇ ᴄᴜꜱᴛᴏᴍ ᴅᴏᴡɴʟᴏᴀᴅ ᴍᴏᴅᴇ</b>\n\n"
        "ᴘʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴄʜᴀᴘᴛᴇʀ ɴᴜᴍʙᴇʀ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ.\n"
        "ʏᴏᴜ ᴄᴀɴ ᴅᴏᴡɴʟᴏᴀᴅ ᴀ ꜱɪɴɢʟᴇ ᴄʜᴀᴘᴛᴇʀ ᴏʀ ᴀ ʀᴀɴɢᴇ.\n\n"
        "<b>ᴇxᴀᴍᴘʟᴇꜱ:</b>\n"
        "<code>5</code> (ᴅᴏᴡɴʟᴏᴀᴅ ᴄʜᴀᴘᴛᴇʀ 5)\n"
        "<code>10-20</code> (ᴅᴏᴡɴʟᴏᴀᴅ ᴄʜᴀᴘᴛᴇʀꜱ 10 ᴛᴏ 20)\n\n"
        "<i>ᴅᴏᴡɴʟᴏᴀᴅꜱ ᴡɪʟʟ ʙᴇ ꜱᴇɴᴛ ᴛᴏ ʏᴏᴜʀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ.</i>",
        parse_mode=enums.ParseMode.HTML
    )
    await callback_query.answer()


async def custom_dl_input_handler(client, message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if user_id in user_states:
        del user_states[user_id]
        
    data = user_data.get(user_id)
    if not data:
        await message.reply("❌ ꜱᴇꜱꜱɪᴏɴ ᴇxᴘɪʀᴇᴅ. ᴘʟᴇᴀꜱᴇ ꜱᴇᴀʀᴄʜ ᴀɢᴀɪɴ.")
        return
        
    source = data['source']
    manga_id = data['manga_id']
    
    target_chapters = []  # List of floats/strings numbers
    is_range = False
    
    try:
        if "-" in text:
            is_range = True
            start, end = map(float, text.split("-"))
            range_min = min(start, end)
            range_max = max(start, end)
        else:
            target_chapters.append(float(text))
    except ValueError:
        await message.reply("❌ ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ. ᴘʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ɴᴜᴍʙᴇʀꜱ ʟɪᴋᴇ `5` ᴏʀ `10-20`.")
        return

    status_msg = await message.reply("<i>⏳ ꜰᴇᴛᴄʜɪɴɢ ᴄʜᴀᴘᴛᴇʀ ʟɪꜱᴛ...</i>", parse_mode=enums.ParseMode.HTML)
    
    api_class = get_api_class(source)
    all_chapters = []
    
    async with api_class(Config) as api:
        offset = 0
        while True:
            batch = await api.get_manga_chapters(manga_id, limit=100, offset=offset)
            if not batch:
                break
            all_chapters.extend(batch)
            if len(batch) < 100:
                break
            offset += 100
            if len(all_chapters) > 2000:
                break  # Safety break
            
    if not all_chapters:
        await status_msg.edit_text("❌ ɴᴏ ᴄʜᴀᴘᴛᴇʀꜱ ꜰᴏᴜɴᴅ.")
        return

    to_download = []
    for ch in all_chapters:
        try:
            ch_num = float(ch['chapter'])
            if is_range:
                if range_min <= ch_num <= range_max:
                    to_download.append(ch)
            else:
                if ch_num in target_chapters:
                    to_download.append(ch)
        except:
            pass  # Skip non-numeric chapters
             
    if not to_download:
        await status_msg.edit_text(f"❌ ɴᴏ ᴄʜᴀᴘᴛᴇʀꜱ ꜰᴏᴜɴᴅ ꜰᴏʀ ɪɴᴘᴜᴛ: {text}")
        return

    await status_msg.edit_text(f"✅ ꜰᴏᴜɴᴅ {len(to_download)} ᴄʜᴀᴘᴛᴇʀꜱ. ꜱᴛᴀʀᴛɪɴɢ ᴅᴏᴡɴʟᴏᴀᴅ...")
    
    to_download.sort(key=lambda x: float(x['chapter']))
    
    for ch in to_download:
        await execute_download(client, message.chat.id, source, manga_id, ch['id'], user_id)


async def execute_download(client, target_chat_id, source, manga_id, chapter_id, status_chat_id=None):
    """
    Downloads and uploads a chapter.
    status_chat_id: Where to send updates (if different from target).
    """
    if not status_chat_id:
        status_chat_id = target_chat_id
    
    status_msg = await client.send_message(status_chat_id, "<i>⏳ ɪɴɪᴛɪᴀʟɪᴢɪɴɢ ᴅᴏᴡɴʟᴏᴀᴅ...</i>", parse_mode=enums.ParseMode.HTML)
    
    try:
        api_class = get_api_class(source)
        async with api_class(Config) as api:
            meta = await api.get_chapter_info(chapter_id)
            if not meta:
                await status_msg.edit_text("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ɢᴇᴛ ᴄʜᴀᴘᴛᴇʀ ɪɴꜰᴏ.")
                return
            
            if meta.get('manga_title') in ['Unknown', None]:
                m_info = await api.get_manga_info(manga_id)
                if m_info:
                    meta['manga_title'] = m_info['title']

            images = await api.get_chapter_images(chapter_id)
            
        if not images:
            await status_msg.edit_text(f"❌ ɴᴏ ɪᴍᴀɢᴇꜱ ɪɴ ᴄʜᴀᴘᴛᴇʀ {meta.get('chapter', '?')}")
            return
            
        chapter_dir = Path(Config.DOWNLOAD_DIR) / f"{source}_{manga_id}" / f"ch_{meta['chapter']}"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        
        await status_msg.edit_text(f"<i>⬇ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ {len(images)} ᴘᴀɢᴇꜱ...</i>", parse_mode=enums.ParseMode.HTML)
        
        async with Downloader(Config) as downloader:
            if not await downloader.download_images(images, chapter_dir):
                await status_msg.edit_text("❌ ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ.")
                return
            
            await status_msg.edit_text("<i>⚙️ ᴘʀᴏᴄᴇꜱꜱɪɴɢ ᴘᴅꜰ...</i>", parse_mode=enums.ParseMode.HTML)
            
            file_type = await Seishiro.get_config("file_type", "pdf")
            quality = await Seishiro.get_config("image_quality")
            
            banner_1 = await Seishiro.get_config("banner_image_1")
            banner_2 = await Seishiro.get_config("banner_image_2")
            
            intro_p = None
            outro_p = None
            if banner_1:
                intro_p = chapter_dir.parent / "intro.jpg"
                try:
                    await client.download_media(banner_1, file_name=str(intro_p))
                except:
                    intro_p = None
            if banner_2:
                outro_p = chapter_dir.parent / "outro.jpg"
                try:
                    await client.download_media(banner_2, file_name=str(outro_p))
                except:
                    outro_p = None

            final_path = await asyncio.to_thread(
                downloader.create_chapter_file,
                chapter_dir, meta['manga_title'], meta['chapter'], meta['title'],
                file_type, intro_p, outro_p, quality
            )
            
            if intro_p and intro_p.exists():
                intro_p.unlink()
            if outro_p and outro_p.exists():
                outro_p.unlink()
            
            if not final_path:
                await status_msg.edit_text("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴄʀᴇᴀᴛᴇ ꜰɪʟᴇ.")
                return
            
            await status_msg.edit_text(f"<i>⬆ ᴜᴘʟᴏᴀᴅɪɴɢ...</i>", parse_mode=enums.ParseMode.HTML)
            caption = f"<b>{meta['manga_title']} - ᴄʜ {meta['chapter']}</b>"
            
            await client.send_document(
                chat_id=target_chat_id,
                document=final_path,
                caption=caption,
                parse_mode=enums.ParseMode.HTML
            )
            
            shutil.rmtree(chapter_dir, ignore_errors=True)
            if final_path.exists():
                final_path.unlink()
            
            await status_msg.delete()

    except Exception as e:
        logger.error(f"ᴅʟ ᴇʀʀᴏʀ: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ ᴇʀʀᴏʀ: {e}")


@Client.on_callback_query(filters.regex("^dl_ask_"))
async def dl_ask_cb(client, callback_query):
    data = callback_query.data.split("_")
    source = data[2]
    manga_id = data[3]
    chapter_id = "_".join(data[4:])
    
    db_channel = await Seishiro.get_default_channel()
    channel_id = int(db_channel) if db_channel else Config.CHANNEL_ID
    
    await callback_query.answer("ꜱᴛᴀʀᴛɪɴɢ ᴅᴏᴡɴʟᴏᴀᴅ...", show_alert=False)
    await execute_download(client, channel_id, source, manga_id, chapter_id, callback_query.message.chat.id)


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
# Support group @rexbotschat
