# ʀᴇxʙᴏᴛs
# ᴅᴏɴ'ᴛ ʀᴇᴍᴏᴠᴇ ᴄʀᴇᴅɪᴛ
# ᴛᴇʟᴇɢʀᴀᴍ ᴄʜᴀɴɴᴇʟ @ʀᴇxʙᴏᴛs_ᴏғғɪᴄɪᴀʟ 
# sᴜᴘᴏᴏʀᴛ ɢʀᴏᴜᴘ @ʀᴇxʙᴏᴛsᴄʜᴀᴛ

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from Database.database import Seishiro
from Plugins.helper import admin, get_styled_text, user_states, edit_msg_with_pic
from Plugins.Settings.input_helper import timeout_handler
import asyncio
import logging

logger = logging.getLogger(__name__)


@Client.on_callback_query(filters.regex("^(set_caption_btn|view_caption_cb)$"))
async def caption_settings_callback(client, callback_query):
    data = callback_query.data
    if data == "set_caption_btn":
        text = get_styled_text(
            "<b>📝 sᴇᴛ ᴄᴀᴘᴛɪᴏɴ</b>\n\n"
            "sᴇɴᴅs ᴛʜᴇ ᴄᴀᴘᴛɪᴏɴ ᴛᴇxᴛ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜsᴇ.\n"
            "ᴠᴀʀɪᴀʙʟᴇs: `{manga_name}`, `{chapter}`\n\n"
            "<i>sᴇɴᴅ ᴛᴇxᴛ ɴᴏᴡ...</i>"
        )
        user_states[callback_query.from_user.id] = {"state": "waiting_caption"}
        await edit_msg_with_pic(callback_query.message, text, None) # ɴᴏ ʙᴜᴛᴛᴏɴs sʜᴏᴡɴ ɪɴ ᴛʜɪs sɴɪᴘᴘᴇᴛ ʙᴜᴛ ᴜsᴜᴀʟʟʏ ᴛʜᴇʀᴇ ᴀʀᴇ
    elif data == "view_caption_cb":
        pass

@Client.on_message(filters.command("set_caption") & filters.private & admin)
async def set_caption_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply("ᴜsᴀɢᴇ: /set_caption <text>")
    text = message.text.split(None, 1)[1]
    await Seishiro.set_caption(text)
    await message.reply("<blockquote><b>✅ ᴄᴀᴘᴛɪᴏɴ ᴜᴘᴅᴀᴛᴇᴅ</b></blockquote>")

@Client.on_message(filters.command("set_banner") & filters.private & admin)
async def set_banner_cmd(client, message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴛᴏ sᴇᴛ ʙᴀɴɴᴇʀ.")
    file_id = message.reply_to_message.photo.file_id
    await Seishiro.set_config("banner_image", file_id)
    await message.reply("<blockquote><b>✅ ʙᴀɴɴᴇʀ ɪᴍᴀɢᴇ ᴜᴘᴅᴀᴛᴇᴅ</b></blockquote>")


async def get_banner_menu(client):
    b1 = await Seishiro.get_config("banner_image_1")
    b2 = await Seishiro.get_config("banner_image_2")
    
    status_1 = "sᴇᴛ" if b1 else "ɴᴏɴᴇ"
    status_2 = "sᴇᴛ" if b2 else "ɴᴏɴᴇ"
    
    text = get_styled_text(
        f"<b>ʙᴀɴɴᴇʀ sᴇᴛᴛɪɴɢ</b>\n\n"
        f"➥ ғɪʀsᴛ ʙᴀɴɴᴇʀ: {status_1}\n"
        f"➥ ʟᴀsᴛ ʙᴀɴɴᴇʀ: {status_2}"
    )
    
    buttons = [
        [
            InlineKeyboardButton("sᴇᴛ / ᴄʜᴀɴɢᴇ - 1", callback_data="set_banner_1"),
            InlineKeyboardButton("ᴅᴇʟᴇᴛᴇ - 1", callback_data="del_banner_1")
        ],
        [InlineKeyboardButton("sʜᴏᴡ ʙᴀɴɴᴇʀ - 1", callback_data="show_banner_1")],
        
        [
            InlineKeyboardButton("sᴇᴛ / ᴄʜᴀɴɢᴇ - 2", callback_data="set_banner_2"),
            InlineKeyboardButton("ᴅᴇʟᴇᴛᴇ - 2", callback_data="del_banner_2")
        ],
        [InlineKeyboardButton("sʜᴏᴡ ʙᴀɴɴᴇʀ - 2", callback_data="show_banner_2")],
        
        [
            InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="settings_menu"),
            InlineKeyboardButton("❄ ᴄʟᴏsᴇ ❄", callback_data="stats_close")
        ]
    ]
    return text, InlineKeyboardMarkup(buttons)

@Client.on_callback_query(filters.regex("^set_banner_btn$"))
async def set_banner_cb(client, callback_query):
    text, markup = await get_banner_menu(client)
    await edit_msg_with_pic(callback_query.message, text, markup)

@Client.on_callback_query(filters.regex("^set_banner_(1|2)$"))
async def set_banner_input_cb(client, callback_query):
    num = callback_query.data.split("_")[-1]
    text = get_styled_text(
        f"<i>sᴇɴᴅ ʙᴀɴɴᴇʀ {num} ɪᴍᴀɢᴇ ɴᴏᴡ...</i>\n"
        f"<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": f"waiting_banner_{num}"}
    
    buttons = [
        [InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")],
        [InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="settings_menu")]
    ]
    
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, f"waiting_banner_{num}"))

@Client.on_callback_query(filters.regex("^del_banner_(1|2)$"))
async def del_banner_cb(client, callback_query):
    num = callback_query.data.split("_")[-1]
    await Seishiro.set_config(f"banner_image_{num}", None)
    await callback_query.answer(f"ʙᴀɴɴᴇʀ {num} ᴅᴇʟᴇᴛᴇᴅ!", show_alert=True)
    await set_banner_cb(client, callback_query)

# ʀᴇxʙᴏᴛs
# ᴅᴏɴ'ᴛ ʀᴇᴍᴏᴠᴇ ᴄʀᴇᴅɪᴛ
# ᴛᴇʟᴇɢʀᴀᴍ ᴄʜᴀɴɴᴇʟ @ʀᴇxʙᴏᴛs_ᴏғғɪᴄɪᴀʟ 
# sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ @ʀᴇxʙᴏᴛsᴄʜᴀᴛ


@Client.on_callback_query(filters.regex("^show_banner_(1|2)$"))
async def show_banner_cb(client, callback_query):
    num = callback_query.data.split("_")[-1]
    file_id = await Seishiro.get_config(f"banner_image_{num}")
    if file_id:
        await callback_query.message.reply_photo(file_id, caption=f"ʙᴀɴɴᴇʀ {num}")
    else:
        await callback_query.answer("ɴᴏ ʙᴀɴɴᴇʀ sᴇᴛ.", show_alert=True)

@Client.on_callback_query(filters.regex("^set_caption_btn$"))
async def set_caption_cb(client, callback_query):
    curr = await Seishiro.get_caption()
    curr_disp = "sᴇᴛ" if curr else "ɴᴏɴᴇ"
    
    text = get_styled_text(
        "<b>ᴄᴀᴘᴛɪᴏɴ</b>\n\n"
        "<b>ғᴏʀᴍᴀᴛ:</b>\n"
        "➥ {manga_title}: ᴍᴀɴɢᴀ ɴᴀᴍᴇ\n"
        "➥ {chapter_num}: ᴄʜᴀᴘᴛᴇʀ ɴᴜᴍʙᴇʀ\n"
        "➥ {file_name}: ғɪʟᴇ ɴᴀᴍᴇ\n\n"
        f"➥ ʏᴏᴜʀ ᴠᴀʟᴜᴇ: {curr_disp}"
    )
    
    buttons = [
        [
            InlineKeyboardButton("sᴇᴛ / ᴄʜᴀɴɢᴇ", callback_data="set_caption_input"),
            InlineKeyboardButton("ᴅᴇʟᴇᴛᴇ", callback_data="del_caption_btn")
        ],
        [
            InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="settings_menu"),
            InlineKeyboardButton("❄ ᴄʟᴏsᴇ ❄", callback_data="stats_close")
        ]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)

@Client.on_callback_query(filters.regex("^set_caption_input$"))
async def caption_input_cb(client, callback_query):
    text = get_styled_text(
        "<i>sᴇɴᴅ ɴᴇᴡ ᴄᴀᴘᴛɪᴏɴ ᴛᴇxᴛ ɴᴏᴡ...</i>\n"
        "<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_caption"}
    
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_caption"))

@Client.on_callback_query(filters.regex("^del_caption_btn$"))
async def del_caption_cb_ui(client, callback_query):
    await Seishiro.set_caption(None)
    await callback_query.answer("ᴄᴀᴘᴛɪᴏɴ ᴅᴇʟᴇᴛᴇᴅ!", show_alert=True)
    await set_caption_cb(client, callback_query)


@Client.on_callback_query(filters.regex("^set_(channel_stickers|update_sticker)_btn$"))
async def sticker_placeholder(client, callback_query):
    key = callback_query.data
    text = get_styled_text(
        f"<b>👾 sᴇᴛ {key.replace('set_', '').replace('_btn', '').replace('_', ' ').title()}</b>\n\n"
        "sᴇɴᴅ ᴛʜᴇ sᴛɪᴄᴋᴇʀ ɪᴅ ᴏʀ sᴛɪᴄᴋᴇʀ ɴᴏᴡ.\n"
        "<i>sᴇɴᴅ sᴛɪᴄᴋᴇʀ ɴᴏᴡ...</i>\n"
        "<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": f"waiting_channel_stickers"}
    
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, f"waiting_{key}"))

@Client.on_callback_query(filters.regex("^set_update_text_btn$"))
async def update_text_cb(client, callback_query):
    text = get_styled_text(
        "<b>📝 sᴇᴛ ᴜᴘᴅᴀᴛᴇ ᴛᴇxᴛ</b>\n\n"
        "sᴇɴᴅ ᴛʜᴇ ᴛᴇxᴛ ғᴏʀ ᴜᴘᴅᴀᴛᴇs.\n"
        "<i>sᴇɴᴅ ᴛᴇxᴛ ɴᴏᴡ...</i>\n"
        "<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_update_text"}
    
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_update_text"))

@Client.on_callback_query(filters.regex("^set_thumb_btn$"))
async def set_thumb_cb(client, callback_query):
    text = get_styled_text(
        "<b>🖼️ sᴇᴛ ᴛʜᴜᴍʙɴᴀɪʟ</b>\n\n"
        "sᴇɴᴅ ᴛʜᴇ ᴘʜᴏᴛᴏ ᴛᴏ ᴜsᴇ ᴀs ᴅᴇғᴀᴜʟᴛ ᴛʜᴜᴍʙɴᴀɪʟ.\n"
        "<i>sᴇɴᴅ ᴘʜᴏᴛᴏ ɴᴏᴡ...</i>\n"
        "<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_thumb"}
    
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_thumb"))



# ʀᴇxʙᴏᴛs
# ᴅᴏɴ'ᴛ ʀᴇᴍᴏᴠᴇ ᴄʀᴇᴅɪᴛ
# ᴛᴇʟᴇɢʀᴀᴍ ᴄʜᴀɴɴᴇʟ @ʀᴇxʙᴏᴛs_ᴏғғɪᴄɪᴀʟ 
# sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ @ʀᴇxʙᴏᴛsᴄʜᴀᴛ
