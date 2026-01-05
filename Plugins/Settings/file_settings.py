# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat


from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Database.database import Seishiro
from Plugins.helper import admin, get_styled_text, user_states, edit_msg_with_pic
from Plugins.Settings.input_helper import timeout_handler
import asyncio


@Client.on_callback_query(filters.regex("^set_format_btn$"))
async def set_format_cb(client, callback_query):
    text = get_styled_text(
        "<b>📂 sᴇᴛ ғɪʟᴇ ɴᴀᴍᴇ ғᴏʀᴍᴀᴛ</b>\n\n"
        "ᴄᴜʀʀᴇɴᴛ ғᴏʀᴍᴀᴛ: " + await Seishiro.get_format() + "\n\n"
        "ᴠᴀʀɪᴀʙʟᴇs: `{manga_name}`, `{chapter}`\n"
        "<i>sᴇɴᴅ ɴᴇᴡ ғᴏʀᴍᴀᴛ ɴᴏᴡ...</i>\n"
        "<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_format"}
    
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_format"))

@Client.on_callback_query(filters.regex("^set_file_type_btn$"))
async def set_file_type_cb(client, callback_query):
    current = await Seishiro.get_config("file_type", "PDF")
    new = "CBZ" if current == "PDF" else "PDF"
    await Seishiro.set_config("file_type", new)
    await callback_query.answer(f"ғɪʟᴇ ᴛʏᴘᴇ sᴡɪᴛᴄʜᴇᴅ ᴛᴏ {new}", show_alert=True)

@Client.on_callback_query(filters.regex("^set_compress_btn$"))
async def set_compress_cb(client, callback_query):
    quality = await Seishiro.get_config("image_quality") # If None, assume 100 or original
    val_disp = f"{quality}" if quality is not None else "ɴᴏɴᴇ"
    
    text = get_styled_text(
        f"<b>ɪᴍᴀɢᴇ ᴄᴏᴍᴘʀᴇss</b>\n\n"
        f"➥ ʏᴏᴜʀ ᴠᴀʟᴜᴇ: {val_disp}"
    )
    
    buttons = []
    row = []
    for i in range(0, 101, 5):
        row.append(InlineKeyboardButton(str(i), callback_data=f"set_qual_{i}"))
        if len(row) == 5:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
        
    buttons.append([InlineKeyboardButton("| ᴅᴇʟᴇᴛᴇ |", callback_data="del_quality")])
    buttons.append([
        InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="settings_menu"),
        InlineKeyboardButton("| ᴄʟᴏsᴇ |", callback_data="stats_close")
    ])
    
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)

@Client.on_callback_query(filters.regex("^set_qual_"))
async def set_quality_action(client, callback_query):
    qual = int(callback_query.data.split("_")[-1])
    await Seishiro.set_config("image_quality", qual)
    await callback_query.answer(f"ǫᴜᴀʟɪᴛʏ sᴇᴛ ᴛᴏ {qual}%", show_alert=True)
    await set_compress_cb(client, callback_query)

@Client.on_callback_query(filters.regex("^del_quality$"))
async def del_quality_action(client, callback_query):
    await Seishiro.set_config("image_quality", None)
    await callback_query.answer("ᴄᴏᴍᴘʀᴇssɪᴏɴ ʀᴇᴍᴏᴠᴇᴅ (ᴅᴇғᴀᴜʟᴛ 100%)", show_alert=True)
    await set_compress_cb(client, callback_query)

@Client.on_callback_query(filters.regex("^set_password_btn$"))
async def set_password_cb(client, callback_query):
    text = get_styled_text(
        "<b>🔐 sᴇᴛ ᴘᴅғ ᴘᴀssᴡᴏʀᴅ</b>\n\n"
        "sᴇɴᴅ ᴛʜᴇ ᴘᴀssᴡᴏʀᴅ ᴛᴏ ᴘʀᴏᴛᴇᴄᴛ ᴘᴅғs ᴡɪᴛʜ.\n"
        "sᴇɴᴅ `OFF` ᴛᴏ ᴅɪsᴀʙʟᴇ.\n"
        "<i>sᴇɴᴅ ᴘᴀssᴡᴏʀᴅ ɴᴏᴡ...</i>\n"
        "<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_password"}
    
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_password"))

# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat


@Client.on_callback_query(filters.regex("^set_merge_size_btn$"))
async def set_merge_size_cb(client, callback_query):
    current = await Seishiro.get_config("merge_size_limit", "Unset")
    text = get_styled_text(
        f"<b>⚖️ ᴍᴇʀɢᴇ sɪᴢᴇ ʟɪᴍɪᴛ</b>\n\n"
        f"ᴄᴜʀʀᴇɴᴛ: {current}MB\n\n"
        "sᴇʟᴇᴄᴛ ᴀ ᴘʀᴇsᴇᴛ ᴏʀ ᴄʜᴏᴏsᴇ ᴄᴜsᴛᴏᴍ:"
    )
    buttons = [
        [
            InlineKeyboardButton("50 ᴍʙ", callback_data="set_ms_50"),
            InlineKeyboardButton("100 ᴍʙ", callback_data="set_ms_100"),
            InlineKeyboardButton("500 ᴍʙ", callback_data="set_ms_500")
        ],
        [
            InlineKeyboardButton("ᴄᴜsᴛᴏᴍ", callback_data="set_ms_custom"),
            InlineKeyboardButton("ᴅɪsᴀʙʟᴇ", callback_data="set_ms_disable")
        ],
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings_menu")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)

@Client.on_callback_query(filters.regex("^set_ms_"))
async def merge_size_action(client, callback_query):
    action = callback_query.data.split("_")[2]
    if action == "custom":
        user_states[callback_query.from_user.id] = {"state": "waiting_merge_size"}
        text = get_styled_text(
             "<i>sᴇɴᴅ sɪᴢᴇ ʟɪᴍɪᴛ (MB) ɴᴏᴡ...</i>\n"
             "<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
        )
        buttons = [
            [InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")],
            [InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="settings_menu")]
        ]
        await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
        
        asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_merge_size"))
    elif action == "disable":
        await Seishiro.set_config("merge_size_limit", 0)
        await callback_query.answer("ᴍᴇʀɢᴇ sɪᴢᴇ ʟɪᴍɪᴛ ᴅɪsᴀʙʟᴇᴅ!", show_alert=True)
        await set_merge_size_cb(client, callback_query) # refresh
    else:
        try:
            size = int(action)
            await Seishiro.set_config("merge_size_limit", size)
            await callback_query.answer(f"ʟɪᴍɪᴛ sᴇᴛ ᴛᴏ {size}MB", show_alert=True)
            await set_merge_size_cb(client, callback_query)
        except:
            await callback_query.answer("ᴇʀʀᴏʀ", show_alert=True)


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat
