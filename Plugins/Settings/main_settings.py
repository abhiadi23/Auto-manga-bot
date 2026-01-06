# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
# Support group @rexbotschat

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from Database.database import Seishiro
from Plugins.helper import get_styled_text, admin, edit_msg_with_pic
from Plugins.Settings.admin_settings import *

@Client.on_callback_query(filters.regex("^settings_menu$|^settings_menu_1$"))
async def settings_main_menu(client, callback_query):
    try:
        user_id = callback_query.from_user.id
        if user_id != Config.USER_ID and not await Seishiro.is_admin(user_id):
            await callback_query.answer("❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ sᴇᴛᴛɪɴɢs.", show_alert=True)
            return

        buttons = [
            [InlineKeyboardButton("• <u>ʀᴇxʙᴏᴛs ᴏғғɪᴄᴀʟ</u> •", callback_data="header_watermark")],
            [
                InlineKeyboardButton("ʙᴀɴɴᴇʀ", callback_data="set_banner_btn"),
                InlineKeyboardButton("ᴄᴀᴘᴛɪᴏɴ", callback_data="set_caption_btn")
            ],
            [
                InlineKeyboardButton("ᴄʜᴀɴɴᴇʟ sᴛɪᴄᴋᴇʀs", callback_data="set_channel_stickers_btn"),
                InlineKeyboardButton("ᴄᴏᴍᴘʀᴇss", callback_data="set_compress_btn")
            ],
            [
                InlineKeyboardButton("ғɪʟᴇ ɴᴀᴍᴇ", callback_data="set_format_btn"),
                InlineKeyboardButton("ғɪʟᴇ ᴛʏᴘᴇ", callback_data="set_file_type_btn")
            ],
            [
                InlineKeyboardButton("ʜʏᴘᴇʀ ʟɪɴᴋ", callback_data="set_hyperlink_btn"),
                InlineKeyboardButton("ᴍᴇʀɢᴇ sɪᴢᴇ", callback_data="set_merge_size_btn")
            ],
            [
                InlineKeyboardButton("ᴘᴀssᴡᴏʀᴅ", callback_data="set_password_btn"),
                InlineKeyboardButton("ʀᴇɢᴇx", callback_data="set_regex_btn")
            ],
            [
                InlineKeyboardButton("ᴛʜᴜᴍʙɴᴀɪʟ", callback_data="set_thumb_btn")
            ],
            [
                InlineKeyboardButton("• ʜᴏᴍᴇ", callback_data="start_menu"),
                InlineKeyboardButton("ɴᴇxᴛ •", callback_data="settings_menu_2")
            ]
        ]
        
        text = (
            "<blockquote><b>⚙️ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ (ᴘᴀɢᴇ 1/2)</b></blockquote>\n\n"
            "<blockquote>sᴇʟᴇᴄᴛ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴄᴏɴғɪɢᴜʀᴇ ᴛʜᴇ ʙᴏᴛ. "
            "ᴀʟʟ ᴄʜᴀɴɢᴇs ᴀʀᴇ sᴀᴠᴇᴅ ɪɴsᴛᴀɴᴛʟʏ ᴛᴏ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ.</blockquote>"
        )

        await edit_msg_with_pic(
            message=callback_query.message,
            text=text,
            buttons=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.HTML  # Fixed: correct parameter name and enum
        )
    except Exception as e:
        await callback_query.answer("ᴇʀʀᴏʀ ᴏᴘᴇɴɪɴɢ sᴇᴛᴛɪɴɢs", show_alert=True)


@Client.on_callback_query(filters.regex("^settings_menu_2$"))
async def settings_main_menu_2(client, callback_query):
    try:
        buttons = [
            [
                InlineKeyboardButton("ᴅᴜᴍᴘ ᴄʜɴʟ", callback_data="header_dump_channel"),
                InlineKeyboardButton("Uᴘʟᴏᴀᴅ ᴄʜɴʟ", callback_data="header_auto_update_channels")
            ],
            [InlineKeyboardButton("<u>ᴍᴏɴɪᴛᴏʀ & ғsᴜʙ</u>", callback_data="header_new_items")],
            [
                InlineKeyboardButton(
                    f"ᴍᴏɴɪᴛᴏʀ: {'✅ ᴏɴ' if await Seishiro.get_monitoring_status() else '❌ ᴏғғ'}",
                    callback_data="toggle_monitor"
                ),
                InlineKeyboardButton("ᴠɪᴇᴡ ᴘʀᴏɢʀᴇss 📊", callback_data="view_progress")
            ],
            [
                InlineKeyboardButton("sᴇᴛ ɪɴᴛᴇʀᴠᴀʟ", callback_data="set_interval_btn"),
                InlineKeyboardButton("ғsᴜʙ ᴍᴏᴅᴇ", callback_data="fsub_menu_btn")
            ],
            [
                InlineKeyboardButton("ᴡᴀᴛᴇʀᴍᴀʀᴋ", callback_data="set_watermark_btn"),
                InlineKeyboardButton("ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ", callback_data="set_deltimer_btn")
            ],
            [InlineKeyboardButton("ᴍᴀɴɢᴀ sᴏᴜʀᴄᴇ", callback_data="header_source")],
            [
                InlineKeyboardButton(
                    f"📡 sᴏᴜʀᴄᴇ: {await Seishiro.get_config('manga_source', 'mangadex')}",
                    callback_data="set_source_btn"
                )
            ],
            [InlineKeyboardButton("<u>ᴀᴅᴍɪɴ ᴄᴏɴᴛʀᴏʟs</u>", callback_data="header_admins")],
            [
                InlineKeyboardButton("ᴀᴅᴍɪɴs 👮‍♂️", callback_data="admin_menu_btn"),
                InlineKeyboardButton("ʙʀᴏᴀᴅᴄᴀsᴛ 📢", callback_data="broadcast_btn")
            ],
            [
                InlineKeyboardButton("Bᴀɴ/ᴜɴʙᴀɴ ❌", callback_data="ban_unban_menu_btn")
            ],
            [
                InlineKeyboardButton("• ʙᴀᴄᴋ", callback_data="settings_menu_1"),
                InlineKeyboardButton("❄️ ᴄʟᴏsᴇ ❄️", callback_data="stats_close")
            ]
        ]
        
        dump_ch = await Seishiro.get_config("dump_channel")
        update_ch = await Seishiro.get_default_channel()
        
        text = (
            "<blockquote><b>⚙️ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ (ᴘᴀɢᴇ 2/2)</b></blockquote>\n\n"
            f"<b>ᴄᴜʀʀᴇɴᴛ ᴄʜᴀɴɴᴇʟs:</b>\n"
            f"🗑️ ᴅᴜᴍᴘ: `{dump_ch if dump_ch else 'ɴᴏᴛ sᴇᴛ'}`\n"
            f"📢 Uᴘʟᴏᴀᴅ: `{update_ch if update_ch else 'ɴᴏᴛ sᴇᴛ'}`\n\n"
            "<blockquote>ᴜsᴇ ᴀʀʀᴏᴡs ᴛᴏ ɴᴀᴠɪɢᴀᴛᴇ ʙᴇᴛᴡᴇᴇɴ ᴘᴀɢᴇs.</blockquote>"
        )

        await edit_msg_with_pic(
            message=callback_query.message,
            text=text,
            buttons=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.HTML  # Added missing parse_mode
        )
    except Exception as e:
        await callback_query.answer("ᴇʀʀᴏʀ ᴏᴘᴇɴɪɴɢ sᴇᴛᴛɪɴɢs ᴘᴀɢᴇ 2", show_alert=True)


@Client.on_callback_query(filters.regex("^header_(?!dump_channel|source|auto_update_channels|auto_upload_channels|new_items).*$"))
async def header_callback(client, callback_query):
    await callback_query.answer("ᴠᴀʟᴜᴇs ɪɴ ᴛʜɪs sᴇᴄᴛɪᴏɴ:", show_alert=True)  # Fixed show_alert


@Client.on_callback_query(filters.regex("^stats_close$"))
async def close_callback(client, callback_query):
    await callback_query.message.delete()


@Client.on_callback_query(filters.regex("^start_menu$"))
async def start_menu_cb(client, callback_query):
    caption = (
        f"<b>👋 ʜᴇʟʟᴏ {callback_query.from_user.first_name}!</b>\n\n"
        "<blockquote>ɪ ᴀᴍ ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴀɴɢᴀ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ & ᴜᴘʟᴏᴀᴅᴇʀ ʙᴏᴛ.</blockquote>\n\n"
        "<i>ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ᴄᴏɴᴛʀᴏʟ ᴍᴇ!</i>"
    )
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚙️ sᴇᴛᴛɪɴɢs", callback_data="settings_menu"),
            InlineKeyboardButton("❓ ʜᴇʟᴘ", callback_data="help_menu")
        ],
        [
            InlineKeyboardButton("📢 ᴏғғɪᴄɪᴀʟ ᴄʜᴀɴɴᴇʟ", url="https://t.me/akaza7902"),
            InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/akaza7902")
        ]
    ])
    await edit_msg_with_pic(
        message=callback_query.message,
        text=caption,
        buttons=buttons,
        parse_mode=ParseMode.HTML  # Added parse_mode for consistency
    )


@Client.on_callback_query(filters.regex("^set_source_btn$"))
async def set_source_menu(client, callback_query):
    try:
        current = await Seishiro.get_config('manga_source', 'mangadex')
        text = (
            "<b>📡 sᴇʟᴇᴄᴛ ᴍᴀɴɢᴀ sᴏᴜʀᴄᴇ</b>\n\n"
            "<blockquote>ᴄʜᴏᴏsᴇ ᴡʜɪᴄʜ sᴏᴜʀᴄᴇ ᴛʜᴇ ʙᴏᴛ sʜᴏᴜʟᴅ ᴜsᴇ ғᴏʀ ᴀᴜᴛᴏᴍᴀᴛɪᴄ ᴜᴘᴅᴀᴛᴇs ᴀɴᴅ sᴇᴀʀᴄʜɪɴɢ.</blockquote>\n\n"
            f"<b>ᴄᴜʀʀᴇɴᴛ:</b> <code>{current}</code>"
        )
        
        buttons = [
            [
                InlineKeyboardButton(f"{'✅ ' if current == 'mangadex' else ''}ᴍᴀɴɢᴀᴅᴇx", callback_data="set_source_mangadex"),
                InlineKeyboardButton(f"{'✅ ' if current == 'webcentral' else ''}ᴡᴇʙᴄᴇɴᴛʀᴀʟ", callback_data="set_source_webcentral")
            ],
            [
                InlineKeyboardButton(f"{'✅ ' if current == 'mangaforest' else ''}ᴍᴀɴɢᴀғᴏʀᴇsᴛ", callback_data="set_source_mangaforest"),
                InlineKeyboardButton(f"{'✅ ' if current == 'mangakakalot' else ''}ᴍᴀɴɢᴀᴋᴀᴋᴀʟᴏᴛ", callback_data="set_source_mangakakalot")
            ],
            [
                InlineKeyboardButton(f"{'✅ ' if current == 'allmanga' else ''}ᴀʟʟᴍᴀɴɢᴀ", callback_data="set_source_allmanga")
            ],
            [
                InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="settings_menu_2")  # Better to go back to page 2
            ]
        ]
        
        await edit_msg_with_pic(
            message=callback_query.message,
            text=text,
            buttons=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await callback_query.answer("ᴇʀʀᴏʀ ᴏᴘᴇɴɪɴɢ sᴏᴜʀᴄᴇ ᴍᴇɴᴜ", show_alert=True)


@Client.on_callback_query(filters.regex("^set_source_(.+)$"))
async def set_source_callback(client, callback_query):
    new_source = callback_query.matches[0].group(1)
    await Seishiro.set_config('manga_source', new_source)
    await callback_query.answer(f"sᴏᴜʀᴄᴇ sᴇᴛ ᴛᴏ: {new_source}", show_alert=True)
    await set_source_menu(client, callback_query)  # Refresh the menu with new selection
