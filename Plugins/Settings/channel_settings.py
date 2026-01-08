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
import logging

logger = logging.getLogger(__name__)


@Client.on_callback_query(filters.regex("^header_auto_update_channels$"))
async def auc_menu(client, callback_query):
    text = get_styled_text("ʏᴏᴜʀ Uᴘʟᴏᴀᴅ ᴄʜᴀɴɴᴇʟ")
    
    buttons = [
        [
            InlineKeyboardButton("+ ᴀᴅᴅ +", callback_data="auc_add"),
            InlineKeyboardButton("- ʀᴇᴍᴏᴠᴇ ᴀʟʟ -", callback_data="auc_rem")
        ],
        [
            InlineKeyboardButton("ᴠɪᴇᴡ ᴄʜᴀɴɴᴇʟ", callback_data="auc_view_channels")
        ],
        [
            InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="settings_menu"),
            InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data="stats_close")
        ]
    ]
    
    await callback_query.message.edit_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex("^auc_add$"))
async def auc_add_cb(client, callback_query):
    text = get_styled_text(
        "<b>➕ ᴀᴅᴅ Uᴘʟᴏᴀᴅ ᴄʜᴀɴɴᴇʟ</b>\n\n"
        "sᴇɴᴅ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ (ᴇ.ɢ. -100xxx) ᴛᴏ ᴀᴅᴅ.\n"
        "<i>ʙᴏᴛ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴠᴇʀɪғʏ!</i>\n"
        "<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_auc_id"}
    
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_auc_id"))

@Client.on_callback_query(filters.regex("^auc_rem$"))
async def auc_rem_channel_cb(client, callback_query):
    await Seishiro.remove_default_channel()
    await callback_query.answer("✅ Uᴘʟᴏᴀᴅ ᴄʜᴀɴɴᴇʟ ʀᴇᴍᴏᴠᴇᴅ", show_alert=True)

@Client.on_callback_query(filters.regex("^auc_view_channels$"))
async def auc_view_channels_cb(client, callback_query):
    try:
        auto_ch = await Seishiro.get_default_channel()
        
        if not auto_ch:
            text = get_styled_text("<b>🤖 Uᴘʟᴏᴀᴅ ᴄʜᴀɴɴᴇʟ</b>\n\n➥ ɴᴏ ᴄʜᴀɴɴᴇʟ ғᴏᴜɴᴅ")
        else:
            text = get_styled_text("<b>🤖 Uᴘʟᴏᴀᴅ ᴄʜᴀɴɴᴇʟ</b>\n\n")
            for c in auto_ch:
                db_title = c.get('title', 'ᴜɴᴋɴᴏᴡɴ')
                cid = c.get('channel_id')
                try:
                    chat = await client.get_chat(int(cid))
                    text += f"• {chat.title}\n  ɪᴅ: `{cid}`"
                except:
                    text += f"• {db_title}\n  ɪᴅ: `{cid}` (ɪɴᴠᴀʟɪᴅ)"
        
        buttons = [[InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="header_auto_update_channels")]]
        await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    except Exception as e:
        await callback_query.answer(f"ᴇʀʀᴏʀ: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^set_channel_btn$"))
async def set_channel_cb(client, callback_query):
    text = get_styled_text(
        "<b>📢 sᴇᴛ ᴜᴘʟᴏᴀᴅ ᴄʜᴀɴɴᴇʟ</b>\n\n"
        "sᴇɴᴅ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ (-100...) ᴡʜᴇʀᴇ ᴍᴀɴɢᴀ ᴄʜᴀᴘᴛᴇʀs ᴡɪʟʟ ʙᴇ ᴜᴘʟᴏᴀᴅᴇᴅ.\n"
        "<i>ᴍᴀᴋᴇ sᴜʀᴇ ᴛʜᴇ ʙᴏᴛ ɪs ᴀᴅᴍɪɴ ᴛʜᴇʀᴇ!</i>\n"
        "<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_channel"}
    
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_channel"))

@Client.on_callback_query(filters.regex("^(header_dump_channel|set_dump_channel_btn)$"))
async def dump_channel_menu(client, callback_query):
    dump_id = await Seishiro.get_config("dump_channel")
    status = f"<code>{dump_id}</code>" if dump_id else "ɴᴏɴᴇ"
    
    text = (
        f"<b>➥ ᴅᴜᴍᴘ ᴄʜᴀɴɴᴇʟ</b>\n"
        f"<b>➥ ʏᴏᴜʀ ᴠᴀʟᴜᴇ: {status}</b>"
    )
    
    buttons = [
        [
            InlineKeyboardButton("sᴇᴛ / ᴄʜᴀɴɢᴇ", callback_data="set_dump_input"),
            InlineKeyboardButton("ᴅᴇʟᴇᴛᴇ", callback_data="rem_dump_channel")
        ],
        [
            InlineKeyboardButton("ᴠɪᴇᴡ ᴄʜᴀɴɴᴇʟ 👁", callback_data="view_dump_channel")
        ],
        [
            InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="settings_menu"),
            InlineKeyboardButton("* ᴄʟᴏsᴇ *", callback_data="stats_close")
        ]
    ]
    
    try:
        if callback_query.message.photo:
             await callback_query.message.edit_caption(caption=text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
        else:
             await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    except Exception as e:
         pass

# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat


@Client.on_callback_query(filters.regex("^set_dump_input$"))
async def set_dump_input_cb(client, callback_query):
    text = get_styled_text(
        "<b>🗑️ sᴇᴛ ᴅᴜᴍᴘ ᴄʜᴀɴɴᴇʟ</b>\n\n"
        "sᴇɴᴅ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ ғᴏʀ ᴛʜᴇ ᴅᴜᴍᴘ ᴄʜᴀɴɴᴇʟ.\n"
        "<i>sᴇɴᴅ ɪᴅ ɴᴏᴡ...</i>\n"
        "<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_dump_channel"}
    
    buttons = [
        [InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")],
        [InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="header_dump_channel")]
    ]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_dump_channel"))

@Client.on_callback_query(filters.regex("^rem_dump_channel$"))
async def rem_dump_channel_cb(client, callback_query):
    await Seishiro.set_config("dump_channel", None)
    await callback_query.answer("ᴅᴜᴍᴘ ᴄʜᴀɴɴᴇʟ ʀᴇᴍᴏᴠᴇᴅ!", show_alert=True)
    await dump_channel_menu(client, callback_query)


@Client.on_callback_query(filters.regex("^view_dump_channel$"))
async def view_dump_channel_cb(client, callback_query):
    try:
        dump_id = await Seishiro.get_config("dump_channel")
        
        if not dump_id:
            text = get_styled_text("<b>🗑️ ᴅᴜᴍᴘ ᴄʜᴀɴɴᴇʟ</b>\n\n➥ ɴᴏᴛ sᴇᴛ")
        else:
            try:
                chat = await client.get_chat(int(dump_id))
                text = get_styled_text(
                    f"<b>🗑️ ᴅᴜᴍᴘ ᴄʜᴀɴɴᴇʟ</b>\n\n"
                    f"<b>ᴄʜᴀɴɴᴇʟ:</b> {chat.title}\n"
                    f"<b>ɪᴅ:</b> `{dump_id}`"
                )
            except:
                text = get_styled_text(
                    f"<b>🗑️ ᴅᴜᴍᴘ ᴄʜᴀɴɴᴇʟ</b>\n\n"
                    f"<b>ɪᴅ:</b> `{dump_id}`\n"
                    f"<i>(ᴄᴀɴɴᴏᴛ ᴀᴄᴄᴇss ᴄʜᴀɴɴᴇʟ)</i>"
                )
        
        buttons = [[InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="header_dump_channel")]]
        await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    except Exception as e:
        await callback_query.answer(f"ᴇʀʀᴏʀ: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^set_chnl_btn$"))
async def set_chnl_btn_cb(client, callback_query):
    text = get_styled_text(
        "<b>📢 sᴇᴛ ᴜᴘʟᴏᴀᴅ ᴄʜᴀɴɴᴇʟ</b>\n\n"
        "sᴇɴᴅ ᴛʜᴇ <b>ᴄʜᴀɴɴᴇʟ ɪᴅ</b> (-100...).\n"
        "<i>(ᴀᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_upload_channel"}
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_upload_channel"))


@Client.on_callback_query(filters.regex("^view_chnl_btn$"))
async def view_chnl_btn_cb(client, callback_query):
    try:
        cid = await Seishiro.get_default_channel()
        
        if not cid:
            text = get_styled_text("<b>📺 ᴜᴘʟᴏᴀᴅ ᴄʜᴀɴɴᴇʟ</b>\n\n➥ ɴᴏᴛ sᴇᴛ")
        else:
            try:
                chat = await client.get_chat(int(cid))
                text = get_styled_text(
                    f"<b>📺 ᴜᴘʟᴏᴀᴅ ᴄʜᴀɴɴᴇʟ</b>\n\n"
                    f"<b>ᴄʜᴀɴɴᴇʟ:</b> {chat.title}\n"
                    f"<b>ɪᴅ:</b> `{cid}`"
                )
            except:
                text = get_styled_text(
                    f"<b>📺 ᴜᴘʟᴏᴀᴅ ᴄʜᴀɴɴᴇʟ</b>\n\n"
                    f"<b>ɪᴅ:</b> `{cid}`\n"
                    f"<i>(ᴄᴀɴɴᴏᴛ ᴀᴄᴄᴇss ᴄʜᴀɴɴᴇʟ)</i>"
                )
        
        buttons = [[InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="settings_menu")]]
        await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    except Exception as e:
        await callback_query.answer(f"ᴇʀʀᴏʀ: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^rem_chnl_btn$"))
async def rem_chnl_btn_cb(client, callback_query):
    await Seishiro.set_default_channel(None)
    await callback_query.answer("✅ ᴜᴘʟᴏᴀᴅ ᴄʜᴀɴɴᴇʟ ʀᴇᴍᴏᴠᴇᴅ", show_alert=True)


@Client.on_callback_query(filters.regex("^admin_channels_btn$"))
async def admin_channels_cb(client, callback_query):
    try:
        dump_id = await Seishiro.get_config("dump_channel")
        update_id = await Seishiro.get_default_channel()
        auto_chs = await Seishiro.get_auto_update_channels()

        async def get_name(cid):
            if not cid: return "ɴᴏᴛ sᴇᴛ"
            try:
                chat = await client.get_chat(int(cid))
                return f"{chat.title} (`{cid}`)"
            except:
                return f"ᴜɴᴋɴᴏᴡɴ (`{cid}`)"

        dump_str = await get_name(dump_id)
        update_str = await get_name(update_id)
        
        auto_text = ""
        if auto_chs:
            for c in auto_chs:
                db_title = c.get('title', 'ᴜɴᴋɴᴏᴡɴ')
                cid = c.get('_id')
                auto_text += f"\n• {db_title} (`{cid}`)"
        else:
            auto_text = "\n• ɴᴏɴᴇ"

        text = get_styled_text(
            f"<b>📺 ᴄʜᴀɴɴᴇʟ ᴄᴏɴғɪɢᴜʀᴀᴛɪᴏɴ</b>\n\n"
            f"<b>🗑️ ᴅᴜᴍᴘ ᴄʜᴀɴɴᴇʟ:</b>\n➥ {dump_str}\n\n"
            f"<b>📢 ᴜᴘʟᴏᴀᴅ ᴄʜᴀɴɴᴇʟ:</b>\n➥ {update_str}\n\n"
            f"<b>🤖 ᴀᴜᴛᴏ-ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟs:</b>{auto_text}"
        )
        
        buttons = [[InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="admin_menu_btn")]]
        await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    except Exception as e:
        await callback_query.answer(f"ᴇʀʀᴏʀ: {e}", show_alert=True)


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat
