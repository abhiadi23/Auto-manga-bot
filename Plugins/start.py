# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat


import logging
import random
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Database.database import Seishiro
from config import Config
from Plugins.helper import *

logger = logging.getLogger(__name__)
logger.info("PLUGIN LOAD: start.py loaded successfully")


@Client.on_message(filters.command("start"))
async def start_msg(client, message):
    try:
        await Seishiro.add_user(client, message)
        
        caption = (
            f"<b>👋 ʜᴇʟʟᴏ {message.from_user.first_name}!</b>\n\n"
            f"<blockquote><b>ɪ ᴀᴍ ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴀɴɢᴀ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ & ᴜᴘʟᴏᴀᴅᴇʀ ʙᴏᴛ."</b></blockquote>\n\n"
            f"<i>  ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ᴄᴏɴᴛʀᴏʟ ᴍᴇ!  </i>"
        )
        
        if hasattr(Config, "PICS") and Config.PICS:
            START_PIC = random.choice(Config.PICS)
        else:
            START_PIC = "https://ibb.co/Y7JxBDPp"

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(" Settings", callback_data="settings_menu"),
                InlineKeyboardButton(" Help", callback_data="help_menu")
            ],
            [
                InlineKeyboardButton(" Official Channel", url="https://t.me/RexBots_Official"),
                InlineKeyboardButton(" Developer", url="https://t.me/RexBots_Official")
            ]
        ])

        try:
            await message.reply_photo(
                photo=START_PIC,
                caption=caption,
                reply_markup=buttons,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as img_e:
            logger.error(f"Image failed to load: {img_e}")
            await message.reply_text(
                text=caption,
                reply_markup=buttons,
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
    except Exception as e:
        logger.error(f"/start failed: {e}", exc_info=True)
        try:
            await message.reply_text(f"✅ Bot is alive! (Error displaying menu: {e})")
        except:
            pass

# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat


@Client.on_callback_query(filters.regex("^help_menu$"))
async def help_menu(client, callback_query):
    paraphrased = (
        "<b>📚 How to Use</b>\n\n"
        "• <b>Search Manga:</b> Just send me the manga name (e.g. `One Piece`) to begin.\n\n"
        "• <b>Select Source:</b> Choose your preferred Language and Website from the options.\n\n"
        "• <b>Download or Subscribe:</b> You can download individual chapters or Subscribe to get auto-updates when new chapters are released.\n\n"
        "<b>📢 Updates Channel:</b> @RexBots_Official"
    )
    
    buttons = [[InlineKeyboardButton("🔙 back", callback_data="start_menu")]]
    
    await edit_msg_with_pic(callback_query.message, paraphrased, InlineKeyboardMarkup(buttons))


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat
