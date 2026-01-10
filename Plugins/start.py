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
        text = message.text
        if len(text) > 7:
            try:
                base64_string = text.split(" ", 1)[1]
            except IndexError:
                return

        string = await decode(base64_string)
        temp_msg = await message.reply("<b>Please wait...</b>")
        try:
            messages = await get_messages(client, ids)
        except Exception as e:
            await message.reply_text("Something went wrong!")
            print(f"Error getting messages: {e}")
            return
        finally:
            await temp_msg.delete()
        await Seishiro.add_user(client, message)
        
        caption = (
            f"<b>👋 ʜᴇʟʟᴏ {message.from_user.first_name}!</b>\n\n"
            f"<blockquote><b>ɪ ᴀᴍ ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴀɴɢᴀ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ & ᴜᴘʟᴏᴀᴅᴇʀ ʙᴏᴛ."</b></blockquote>\n\n"
            f"<i>ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ᴄᴏɴᴛʀᴏʟ ᴍᴇ!</i>"
        )
        
        if hasattr(Config, "PICS") and Config.PICS:
            START_PIC = random.choice(Config.PICS)
        else:
            START_PIC = "https://ibb.co/Y7JxBDPp"

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Sᴇᴛᴛɪɴɢs", callback_data="settings_menu"),
                InlineKeyboardButton("Hᴇʟᴘ", callback_data="help_menu")
            ],
            [
                InlineKeyboardButton("ᴄʜᴀɴɴᴇʟ", url="https://t.me/RexBots_Official"),
                InlineKeyboardButton("Dᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/RexBots_Official")
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
        f"Iᴛ's ᴀ ᴀᴅᴠᴀɴᴄᴇ ᴀᴜᴛᴏ ᴍᴀɴɢᴀ ʙᴏᴛ ғᴏʀ sᴇᴀʀᴄʜ ᴀ ᴘᴀʀᴛɪᴄᴜʟᴀʀ ᴍᴀɴɢᴀ ᴜsᴇ ʟɪᴋᴇ ᴛʜɪs.\n"
        f"Usᴀɢᴇ:- /search <manga name>"
            )
    
    buttons = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="start_menu")]]
    
    await edit_msg_with_pic(callback_query.message, paraphrased, InlineKeyboardMarkup(buttons))


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat
