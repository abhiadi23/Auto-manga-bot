# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat


from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Database.database import Seishiro
from Plugins.helper import get_styled_text, user_states, edit_msg_with_pic
from Plugins.Settings.input_helper import timeout_handler
from Plugins.Settings.main_settings import settings_main_menu_2
from Plugins.Settings.admin_settings import *
import asyncio
import logging

logger = logging.getLogger(__name__)


def to_small_caps(text):
    """Convert text to small caps using Unicode characters"""
    small_caps_map = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ',
        'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ',
        'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x',
        'y': 'ʏ', 'z': 'ᴢ', 'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ғ',
        'G': 'ɢ', 'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ',
        'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ', 'S': 's', 'T': 'ᴛ', 'U': 'ᴜ', 'V': 'ᴠ',
        'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ'
    }
    return ''.join(small_caps_map.get(char, char) for char in text)


@Client.on_callback_query(filters.regex("^set_interval_btn$"))
async def set_interval_menu(client, callback_query):
    current = await Seishiro.get_check_interval()
    
    text = get_styled_text(
        f"<b>⏱ {to_small_caps('Set Check Interval')}</b>\n\n"
        f"{to_small_caps('Wait time between checking for new chapters.')}\n"
        f"{to_small_caps('Minimum: 60s (1 min), Maximum: 3600s (1 hour)')}\n\n"
        f"<b>{to_small_caps('Current:')}</b> {current}s"
    )
    
    buttons = [
        [
            InlineKeyboardButton(to_small_caps("5 min"), callback_data="set_int_300"),
            InlineKeyboardButton(to_small_caps("10 min"), callback_data="set_int_600"),
            InlineKeyboardButton(to_small_caps("30 min"), callback_data="set_int_1800")
        ],
        [
            InlineKeyboardButton(to_small_caps("1 hour"), callback_data="set_int_3600"),
            InlineKeyboardButton(to_small_caps("custom"), callback_data="set_int_custom")
        ],
        [
            InlineKeyboardButton(f"⬅ {to_small_caps('back')}", callback_data="settings_menu_2")
        ]
    ]
    
    await edit_msg_with_pic(
        message=callback_query.message,
        text=text,
        buttons=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^set_int_(\\d+)$"))
async def set_int_preset_cb(client, callback_query):
    seconds = int(callback_query.matches[0].group(1))
    success = await Seishiro.set_check_interval(seconds)
    if success:
        await callback_query.answer(f"✅ {to_small_caps('Interval set to')} {seconds}s", show_alert=True)
    else:
        await callback_query.answer(f"❌ {to_small_caps('Error setting interval')}", show_alert=True)
    await set_interval_menu(client, callback_query)

@Client.on_callback_query(filters.regex("^set_int_custom$"))
async def set_int_custom_cb(client, callback_query):
    text = get_styled_text(
        f"<b>⏱ {to_small_caps('Set Custom Interval')}</b>\n\n"
        f"{to_small_caps('Send the interval in seconds (60-3600).')}\n"
        f"<i>{to_small_caps('Send number now...')}</i>\n"
        f"<i>{to_small_caps('(Auto-close in 30s)')}</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_interval"}
    
    buttons = [[InlineKeyboardButton(f"❌ {to_small_caps('cancel')}", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_interval"))

@Client.on_callback_query(filters.regex("^set_watermark_btn$"))
async def watermark_menu(client, callback_query):
    wm = await Seishiro.get_watermark()
    status = to_small_caps("Set") if wm else to_small_caps("None")
    
    text = get_styled_text(
        f"<b>💧 {to_small_caps('Watermark Settings')}</b>\n\n"
        f"{to_small_caps('Add branding to your images.')}\n"
        f"<b>{to_small_caps('Status:')}</b> {status}\n\n"
        f"{to_small_caps('Variables:')} `{{manga_name}}`, `{{chapter}}`"
    )
    
    buttons = [
        [
            InlineKeyboardButton(to_small_caps("set text"), callback_data="wm_set_text"),
            InlineKeyboardButton(to_small_caps("set position"), callback_data="wm_set_pos")
        ],
        [
            InlineKeyboardButton(to_small_caps("set color"), callback_data="wm_set_color"),
            InlineKeyboardButton(to_small_caps("set opacity"), callback_data="wm_set_opacity")
        ],
        [
            InlineKeyboardButton(to_small_caps("delete watermark"), callback_data="wm_delete")
        ],
        [
            InlineKeyboardButton(to_small_caps("view watermark"), callback_data="admin_view_wm_btn")
        ],
        [
            InlineKeyboardButton(f"⬅ {to_small_caps('back')}", callback_data="settings_menu_2")
        ]
    ]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^wm_set_text$"))
async def wm_set_text_cb(client, callback_query):
    text = get_styled_text(
        f"<b>💧 {to_small_caps('Set Watermark Text')}</b>\n"
        f"{to_small_caps('Send the text you want to use.')}\n"
        f"<i>{to_small_caps('(Auto-close in 30s)')}</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_wm_text"}
    buttons = [[InlineKeyboardButton(f"❌ {to_small_caps('cancel')}", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_wm_text"))

# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat


@Client.on_callback_query(filters.regex("^wm_delete$"))
async def wm_delete_cb(client, callback_query):
    await Seishiro.delete_watermark()
    await callback_query.answer(f"{to_small_caps('Watermark deleted!')}", show_alert=True)
    await watermark_menu(client, callback_query)

@Client.on_callback_query(filters.regex("^wm_set_pos$"))
async def wm_set_pos_cb(client, callback_query):
    text = get_styled_text(f"<b>📍 {to_small_caps('Select Watermark Position')}</b>")
    buttons = [
        [
            InlineKeyboardButton(to_small_caps("top left"), callback_data="wm_pos_top-left"),
            InlineKeyboardButton(to_small_caps("top right"), callback_data="wm_pos_top-right")
        ],
        [
            InlineKeyboardButton(to_small_caps("bottom left"), callback_data="wm_pos_bottom-left"),
            InlineKeyboardButton(to_small_caps("bottom right"), callback_data="wm_pos_bottom-right")
        ],
        [
            InlineKeyboardButton(to_small_caps("center"), callback_data="wm_pos_center")
        ],
        [InlineKeyboardButton(f"⬅ {to_small_caps('back')}", callback_data="set_watermark_btn")]
    ]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^wm_pos_(.+)$"))
async def wm_pos_set_cb(client, callback_query):
    pos = callback_query.data.split("wm_pos_")[1]
    wm = await Seishiro.get_watermark() or {}
    await Seishiro.set_watermark(
        text=wm.get("text", "Default Watermark"),
        position=pos,
        color=wm.get("color", "#FFFFFF"),
        opacity=wm.get("opacity", 128),
        font_size=wm.get("font_size", 20)
    )
    await callback_query.answer(f"{to_small_caps('Position set to')} {pos}", show_alert=True)
    await watermark_menu(client, callback_query)

@Client.on_callback_query(filters.regex("^wm_set_color$"))
async def wm_set_color_cb(client, callback_query):
    text = get_styled_text(
        f"<b>🎨 {to_small_caps('Set Watermark Color')}</b>\n"
        f"{to_small_caps('Send Hex Color Code (e.g. #FF0000 for Red).')}\n"
        f"<i>{to_small_caps('(Auto-close in 30s)')}</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_wm_color"}
    buttons = [[InlineKeyboardButton(f"❌ {to_small_caps('cancel')}", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_wm_color"))

@Client.on_callback_query(filters.regex("^wm_set_opacity$"))
async def wm_set_opacity_cb(client, callback_query):
    text = get_styled_text(
        f"<b>👻 {to_small_caps('Set Watermark Opacity')}</b>\n"
        f"{to_small_caps('Send a number between 0 (Transparent) and 255 (Opaque).')}\n"
        f"<i>{to_small_caps('(Auto-close in 30s)')}</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_wm_opacity"}
    buttons = [[InlineKeyboardButton(f"❌ {to_small_caps('cancel')}", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_wm_opacity"))


@Client.on_callback_query(filters.regex("^set_deltimer_btn$"))
async def deltimer_menu(client, callback_query):
    current = await Seishiro.get_del_timer()
    text = get_styled_text(
        f"<b>⏲ {to_small_caps('Auto-Delete Timer')}</b>\n\n"
        f"{to_small_caps('Set how long to keep files in Dump Channel before deleting (if enabled).')}\n"
        f"<b>{to_small_caps('Current:')}</b> {current}s"
    )
    
    buttons = [
        [
            InlineKeyboardButton(to_small_caps("10 min"), callback_data="set_dt_600"),
            InlineKeyboardButton(to_small_caps("30 min"), callback_data="set_dt_1800"),
            InlineKeyboardButton(to_small_caps("1 hour"), callback_data="set_dt_3600")
        ],
        [
            InlineKeyboardButton(to_small_caps("custom"), callback_data="set_dt_custom"),
            InlineKeyboardButton(to_small_caps("disable (0)"), callback_data="set_dt_0")
        ],
        [
            InlineKeyboardButton(f"⬅ {to_small_caps('back')}", callback_data="settings_menu_2")
        ]
    ]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^set_dt_(\\d+)$"))
async def set_dt_preset(client, callback_query):
    val = int(callback_query.matches[0].group(1))
    await Seishiro.set_del_timer(val)
    await callback_query.answer(f"{to_small_caps('Timer set to')} {val}s", show_alert=True)
    await deltimer_menu(client, callback_query)

@Client.on_callback_query(filters.regex("^set_dt_custom$"))
async def set_dt_custom(client, callback_query):
    text = get_styled_text(f"<i>{to_small_caps('Send timer value in seconds...')}</i>")
    user_states[callback_query.from_user.id] = {"state": "waiting_deltimer"}
    buttons = [[InlineKeyboardButton(f"❌ {to_small_caps('cancel')}", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_deltimer"))


@Client.on_callback_query(filters.regex("^toggle_monitor$"))
async def toggle_monitor_cb(client, callback_query):
    current = await Seishiro.get_monitoring_status()
    # Default to True (enabled) if current is None
    if current is None:
        current = True
        await Seishiro.set_monitoring_status(True)
    
    new_status = not current
    await Seishiro.set_monitoring_status(new_status)
    
    status_text = to_small_caps("enabled") if new_status else to_small_caps("Disabled")
    await callback_query.answer(f"{to_small_caps('Monitoring')} {status_text}!", show_alert=True)
    
    if new_status:
        try:
            if hasattr(client, 'bot_instance'):
                asyncio.create_task(client.bot_instance.check_updates())
            else:
                logger.warning("bot_instance not attached to Client!")
        except Exception as e:
            logger.error(f"Failed to trigger immediate check: {e}")

    await settings_main_menu_2(client, callback_query)

@Client.on_callback_query(filters.regex("^view_progress$"))
async def view_progress_cb(client, callback_query):
    state = await Seishiro.get_upload_state()
    
    if not state:
        text = get_styled_text(
            f"<b>📊 {to_small_caps('Bot Progress')}</b>\n\n"
            f"➥ {to_small_caps('Idle (No active tasks)')}"
        )
    else:
        title = state.get('manga_title', 'Unknown Task')
        curr = state.get('processed', 0)
        total = state.get('total', 1)
        
        if total == 0: total = 1
        percent = (curr / total) * 100
        
        filled_len = int(10 * curr // total)
        bar = "█" * filled_len + "░" * (10 - filled_len)
        
        text = get_styled_text(
            f"<b>📊 {to_small_caps('Bot Progress')}</b>\n\n"
            f"<b>{to_small_caps('Task:')}</b> {title}\n"
            f"<b>{to_small_caps('Progress:')}</b> [{bar}] {percent:.1f}%\n"
            f"<b>{to_small_caps('Count:')}</b> {curr}/{total}"
        )
    
    buttons = [
        [InlineKeyboardButton(f"🔄 {to_small_caps('refresh')}", callback_data="view_progress")],
        [InlineKeyboardButton(f"⬅ {to_small_caps('back')}", callback_data="settings_menu_2")]
    ]
    
    try:
        if callback_query.message.photo:
            await callback_query.message.edit_caption(caption=text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
        else:
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    except Exception:
        pass # Ignore Message not modified errors


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat
