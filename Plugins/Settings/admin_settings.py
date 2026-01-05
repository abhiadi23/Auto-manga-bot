# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat


from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Database.database import Seishiro
from Plugins.helper import get_styled_text, user_states, edit_msg_with_pic
from Plugins.Settings.input_helper import timeout_handler
from Plugins.Settings.main_settings import *
import asyncio
from config import Config


@Client.on_callback_query(filters.regex("^admin_menu_btn$"))
async def admin_menu_cb(client, callback_query):
    if callback_query.from_user.id != Config.USER_ID and not await Seishiro.is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ ᴀᴅᴍɪɴ ᴏɴʟʏ ᴀʀᴇᴀ!", show_alert=True)
        return

    text = get_styled_text(
        "<b>👮‍♂️ ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ</b>\n\n"
        "ᴍᴀɴᴀɢᴇ ʙᴏᴛ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs."
    )
    
    buttons = [
        [
            InlineKeyboardButton("ᴀᴅᴅ ᴀᴅᴍɪɴ ➕", callback_data="admin_add_btn"),
            InlineKeyboardButton("ᴅᴇʟ ᴀᴅᴍɪɴ ➖", callback_data="admin_del_btn")
        ],
        [
            InlineKeyboardButton("ʟɪsᴛ ᴀᴅᴍɪɴs 📋", callback_data="admin_list_btn")
        ],
        [
            InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="settings_menu_2")
        ]
    ]
    
    await edit_msg_with_pic(
        message=callback_query.message,
        text=text,
        buttons=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex("^admin_add_btn$"))
async def add_admin_btn_cb(client, callback_query):
    text = get_styled_text(
        "<b>➕ ᴀᴅᴅ ᴀᴅᴍɪɴ</b>\n\n"
        "sᴇɴᴅ ᴛʜᴇ <b>ᴜsᴇʀ ɪᴅ</b> ᴏғ ᴛʜᴇ ɴᴇᴡ ᴀᴅᴍɪɴ.\n"
        "<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_add_admin"}
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_add_admin"))

@Client.on_callback_query(filters.regex("^admin_del_btn$"))
async def del_admin_btn_cb(client, callback_query):
    text = get_styled_text(
        "<b>➖ ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ</b>\n\n"
        "sᴇɴᴅ ᴛʜᴇ <b>ᴜsᴇʀ ɪᴅ</b> ᴛᴏ ʀᴇᴍᴏᴠᴇ.\n"
        "<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_del_admin"}
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_del_admin"))

@Client.on_callback_query(filters.regex("^admin_ban_btn$"))
async def ban_user_btn_cb(client, callback_query):
    text = get_styled_text(
        "<b>🚫 ʙᴀɴ ᴜsᴇʀ</b>\n\n"
        "sᴇɴᴅ ᴛʜᴇ <b>ᴜsᴇʀ ɪᴅ</b> ᴛᴏ ʙᴀɴ.\n"
        "<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_ban_id"}
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_ban_id"))

@Client.on_callback_query(filters.regex("^admin_unban_btn$"))
async def unban_user_btn_cb(client, callback_query):
    text = get_styled_text(
        "<b>✅ ᴜɴʙᴀɴ ᴜsᴇʀ</b>\n\n"
        "sᴇɴᴅ ᴛʜᴇ <b>ᴜsᴇʀ ɪᴅ</b> ᴛᴏ ᴜɴʙᴀɴ.\n"
        "<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_unban_id"}
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_unban_id"))

@Client.on_callback_query(filters.regex("^admin_list_btn$"))
async def list_admins_cb(client, callback_query):
    try:
        admins = await Seishiro.get_admins()
        list_text = f"<b>👮‍♂️ ᴀᴅᴍɪɴ ʟɪsᴛ:</b>\n\n"
        
        try:
             owner = await client.get_users(Config.user_id)
             owner_name = owner.first_name
        except:
             owner_name = "ᴏᴡɴᴇʀ"
        list_text += f"• {owner_name} (`{Config.USER_ID}`) (ᴏᴡɴᴇʀ)\n"

        for uid in admins:
            try:
                user = await client.get_users(uid)
                name = user.first_name
            except:
                name = "ᴜɴᴋɴᴏᴡɴ"
            list_text += f"• {name} (`{uid}`)\n"
        
        buttons = [[InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="admin_menu_btn")]]
        await edit_msg_with_pic(callback_query.message, get_styled_text(list_text), InlineKeyboardMarkup(buttons))
    except Exception as e:
        await callback_query.answer(f"ᴇʀʀᴏʀ: {e}", show_alert=True)

# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat

        
@Client.on_callback_query(filters.regex("^fsub_config_btn$"))
async def fsub_config_menu(client, callback_query):
    channels = await Seishiro.get_fsub_channels()
    buttons = []
    for cid in channels:
        try:
            chat = await client.get_chat(cid)
            mode = await Seishiro.get_channel_mode(cid)
            status = "🟢" if mode == "on" else "🔴"
            buttons.append([InlineKeyboardButton(f"{status} {chat.title}", callback_data=f"rfs_ch_{cid}")])
        except Exception:
             buttons.append([InlineKeyboardButton(f"ɪɴᴠᴀʟɪᴅ {cid}", callback_data=f"rfs_ch_{cid}")])
    
    if not buttons:
        buttons.append([InlineKeyboardButton("ɴᴏ ᴄʜᴀɴɴᴇʟs ғᴏᴜɴᴅ", callback_data="no_channels")])
        
    buttons.append([InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="admin_menu_btn")])
        
    await edit_msg_with_pic(callback_query.message, get_styled_text("<b>📢 ғsᴜʙ ᴄᴏɴғɪɢᴜʀᴀᴛɪᴏɴ</b>\nᴛᴀᴘ ᴛᴏ ᴛᴏɢɢʟᴇ ᴍᴏᴅᴇ."), InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^admin_view_wm_btn$"))
async def view_wm_cb(client, callback_query):
    try:
        current_wm = await Seishiro.get_watermark()
        if current_wm:
            text = (
                f"<b>💧 ᴄᴜʀʀᴇɴᴛ ᴡᴀᴛᴇʀᴍᴀʀᴋ:</b>\n\n"
                f"<b>ᴛᴇxᴛ:</b> `{current_wm['text']}`\n"
                f"<b>ᴘᴏs:</b> `{current_wm['position']}`\n"
                f"<b>ᴄᴏʟ:</b> `{current_wm['color']}` | <b>ᴏᴘ:</b> `{current_wm['opacity']}`\n"
                f"<b>sɪᴢᴇ:</b> `{current_wm['font_size']}`"
            )
        else:
            text = "<b>💧 ᴡᴀᴛᴇʀᴍᴀʀᴋ:</b> ɴᴏᴛ sᴇᴛ"
            
        buttons = [[InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="settings_menu_2")]]
        await edit_msg_with_pic(callback_query.message, get_styled_text(text), InlineKeyboardMarkup(buttons))
    except Exception as e:
        await callback_query.answer(f"ᴇʀʀᴏʀ: {e}", show_alert=True)

@Client.on_callback_query(filters.regex("^add_fsub_btn$"))
async def add_fsub_btn_cb(client, callback_query):
    text = get_styled_text(
        "<b>➕ ᴀᴅᴅ ғᴏʀᴄᴇ-sᴜʙ ᴄʜᴀɴɴᴇʟ</b>\n\n"
        "sᴇɴᴅ ᴛʜᴇ <b>ᴄʜᴀɴɴᴇʟ ɪᴅ</b> (ʙᴏᴛ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ᴛʜᴇʀᴇ).\n"
        "<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_fsub_id"}
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_fsub_id"))

@Client.on_callback_query(filters.regex("^rem_fsub_btn$"))
async def rem_fsub_btn_cb(client, callback_query):
    text = get_styled_text(
        "<b>➖ ʀᴇᴍᴏᴠᴇ ғᴏʀᴄᴇ-sᴜʙ ᴄʜᴀɴɴᴇʟ</b>\n\n"
        "sᴇɴᴅ ᴛʜᴇ <b>ᴄʜᴀɴɴᴇʟ ɪᴅ</b> ᴛᴏ ʀᴇᴍᴏᴠᴇ.\n"
        "<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_fsub_rem_id"}
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_fsub_rem_id"))

@Client.on_callback_query(filters.regex("^broadcast_btn$"))
async def broadcast_btn_cb(client, callback_query):
    text = get_styled_text(
        "<b>📢 ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴇssᴀɢᴇ</b>\n\n"
        "sᴇɴᴅ ᴛʜᴇ ᴍᴇssᴀɢᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ ᴀʟʟ ᴜsᴇʀs.\n"
        "<i>(ᴛᴇxᴛ, ᴘʜᴏᴛᴏ, ᴠɪᴅᴇᴏ, sᴛɪᴄᴋᴇʀ, ᴇᴛᴄ.)</i>\n"
        "<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_broadcast_msg"}
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_broadcast_msg"))
    
# ====================== BAN / UNBAN SUB-MENU ======================
@Client.on_callback_query(filters.regex("^ban_unban_menu_btn$"))
async def ban_unban_menu_cb(client, callback_query):
    if callback_query.from_user.id != Config.USER_ID and not await Seishiro.is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ ᴀᴅᴍɪɴ ᴏɴʟʏ ᴀʀᴇᴀ!", show_alert=True)
        return

    text = get_styled_text(
        "<b>🚫 ʙᴀɴ / ᴜɴʙᴀɴ ᴜsᴇʀs</b>\n\n"
        "ᴍᴀɴᴀɢᴇ ᴜsᴇʀ ᴀᴄᴄᴇss ᴛᴏ ᴛʜᴇ ʙᴏᴛ.\n"
        "ʏᴏᴜ ᴄᴀɴ ʙᴀɴ ᴏʀ ᴜɴʙᴀɴ ᴀɴʏ ᴜsᴇʀ ʙʏ ᴛʜᴇɪʀ ᴜsᴇʀ ɪᴅ."
    )
    
    buttons = [
        [InlineKeyboardButton("🚫 ʙᴀɴ ᴜsᴇʀ", callback_data="admin_ban_btn")],
        [InlineKeyboardButton("✅ ᴜɴʙᴀɴ ᴜsᴇʀ", callback_data="admin_unban_btn")],
        [InlineKeyboardButton("📋 ʟɪsᴛ ʙᴀɴɴᴇᴅ ᴜsᴇʀs", callback_data="admin_list_banned_btn")],
        [InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="settings_menu_2")]
    ]
    
    await edit_msg_with_pic(
        message=callback_query.message,
        text=text,
        buttons=InlineKeyboardMarkup(buttons)
    )


# ====================== FSUB SUB-MENU ======================
@Client.on_callback_query(filters.regex("^fsub_menu_btn$"))
async def fsub_menu_cb(client, callback_query):
    if callback_query.from_user.id != Config.USER_ID and not await Seishiro.is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ ᴀᴅᴍɪɴ ᴏɴʟʏ ᴀʀᴇᴀ!", show_alert=True)
        return

    text = get_styled_text(
        "<b>📢 ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ sᴇᴛᴛɪɴɢs</b>\n\n"
        "ᴍᴀɴᴀɢᴇ ғᴏʀᴄᴇᴅ ᴄʜᴀɴɴᴇʟ sᴜʙsᴄʀɪᴘᴛɪᴏɴs ғᴏʀ ᴀʟʟ ᴜsᴇʀs.\n"
        "ᴜsᴇʀs ᴍᴜsᴛ ᴊᴏɪɴ ᴀʟʟ ᴀᴅᴅᴇᴅ ᴄʜᴀɴɴᴇʟs ᴛᴏ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ."
    )
    
    buttons = [
        [InlineKeyboardButton("📋 ᴠɪᴇᴡ & ᴛᴏɢɢʟᴇ ᴄʜᴀɴɴᴇʟs", callback_data="fsub_config_btn")],
        [InlineKeyboardButton("➕ ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ", callback_data="add_fsub_btn")],
        [InlineKeyboardButton("➖ ʀᴇᴍᴏᴠᴇ ᴄʜᴀɴɴᴇʟ", callback_data="rem_fsub_btn")],
        [InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="settings_menu_2")]
    ]
    
    await edit_msg_with_pic(
        message=callback_query.message,
        text=text,
        buttons=InlineKeyboardMarkup(buttons)
    )


# ====================== LIST BANNED USERS (EXTRA FEATURE) ======================
@Client.on_callback_query(filters.regex("^admin_list_banned_btn$"))
async def list_banned_users_cb(client, callback_query):
    if callback_query.from_user.id != Config.USER_ID and not await Seishiro.is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ ᴀᴅᴍɪɴ ᴏɴʟʏ ᴀʀᴇᴀ!", show_alert=True)
        return

    try:
        banned_users = await Seishiro.get_banned_users()  # Assuming you have this method in DB
        if not banned_users:
            list_text = "<b>🚫 ʙᴀɴɴᴇᴅ ᴜsᴇʀs:</b>\n\nɴᴏ ᴜsᴇʀs ᴀʀᴇ ʙᴀɴɴᴇᴅ ʏᴇᴛ."
        else:
            list_text = "<b>🚫 ʙᴀɴɴᴇᴅ ᴜsᴇʀs:</b>\n\n"
            for uid in banned_users:
                try:
                    user = await client.get_users(uid)
                    name = user.first_name or "Unknown"
                    if user.last_name:
                        name += f" {user.last_name}"
                except:
                    name = "ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ"
                list_text += f"• {name} (`{uid}`)\n"

        buttons = [[InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="ban_unban_menu_btn")]]
        await edit_msg_with_pic(
            message=callback_query.message,
            text=get_styled_text(list_text),
            buttons=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await callback_query.answer(f"ᴇʀʀᴏʀ: {e}", show_alert=True)



# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat
