# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
# Support group @rexbotschat


from pyrogram import Client, filters, enums
from Database.database import Seishiro
from Plugins.helper import user_states, get_styled_text
from config import Config
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


@Client.on_callback_query(filters.regex("^cancel_input$"))
async def cancel_input_cb(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id in user_states:
        del user_states[user_id]
    await callback_query.message.edit_text(
        get_styled_text("❌ ɪɴᴘᴜᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ."),
        parse_mode=enums.ParseMode.HTML
    )
    buttons = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings_menu")]]
    await callback_query.message.reply_text(
        "ᴄᴀɴᴄᴇʟʟᴇᴅ.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_message(filters.private & ~filters.command(["start", "help", "admin"]))
async def settings_input_listener(client, message):
    user_id = message.from_user.id
    if user_id not in user_states:
        return

    state_info = user_states[user_id]
    state = state_info.get("state")
    
    try:
        if state == "waiting_caption":
            await Seishiro.set_caption(message.text)
            await message.reply(
                get_styled_text("✅ ᴄᴀᴘᴛɪᴏɴ ᴜᴘᴅᴀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!"),
                parse_mode=enums.ParseMode.HTML
            )
            
            curr = await Seishiro.get_caption()
            curr_disp = "ꜱᴇᴛ" if curr else "ɴᴏɴᴇ"
            text = get_styled_text(
                "<b>ᴄᴀᴘᴛɪᴏɴ</b>\n\n"
                "<b>ꜰᴏʀᴍᴀᴛ:</b>\n"
                "➥ {manga_title}: ᴍᴀɴɢᴀ ɴᴀᴍᴇ\n"
                "➥ {chapter_num}: ᴄʜᴀᴘᴛᴇʀ ɴᴜᴍʙᴇʀ\n"
                "➥ {file_name}: ꜰɪʟᴇ ɴᴀᴍᴇ\n\n"
                f"➥ ʏᴏᴜʀ ᴠᴀʟᴜᴇ: {curr_disp}"
            )
            buttons = [
                [
                    InlineKeyboardButton("ꜱᴇᴛ / ᴄʜᴀɴɢᴇ", callback_data="set_caption_input"),
                    InlineKeyboardButton("ᴅᴇʟᴇᴛᴇ", callback_data="del_caption_btn")
                ],
                [
                    InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="settings_menu"),
                    InlineKeyboardButton("❄ ᴄʟᴏꜱᴇ ❄", callback_data="stats_close")
                ]
            ]
            await message.reply(
                text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )

        elif state == "waiting_format":
            await Seishiro.set_format(message.text)
            await message.reply(
                get_styled_text("✅ ꜰɪʟᴇ ɴᴀᴍᴇ ꜰᴏʀᴍᴀᴛ ᴜᴘᴅᴀᴛᴇᴅ!"),
                parse_mode=enums.ParseMode.HTML
            )

        elif state.startswith("waiting_banner_"):
            num = state.split("_")[-1]
            if message.photo:
                await Seishiro.set_config(f"banner_image_{num}", message.photo.file_id)
                
                from Plugins.Settings.media_settings import get_banner_menu
                text, markup = await get_banner_menu(client)
                await message.reply(text, reply_markup=markup, parse_mode=enums.ParseMode.HTML)
            else:
                await message.reply("❌ ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ.")
                return

        elif state == "waiting_dump_channel":
            try:
                cid = int(message.text)
                await Seishiro.set_config("dump_channel", cid)
                await message.reply(
                    get_styled_text(f"✅ ᴅᴜᴍᴘ ᴄʜᴀɴɴᴇʟ ꜱᴇᴛ: {cid}"),
                    parse_mode=enums.ParseMode.HTML
                )
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ɪᴅ.")
                return

        elif state == "waiting_auc_id":
            input_text = message.text.strip()
            
            if not input_text:
                await message.reply("❌ ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ.")
                return
            
            try:
                cid = int(input_text)
                
                # Try to get chat info first
                try:
                    chat = await client.get_chat(cid)
                    title = getattr(chat, 'title', f"Channel {cid}")
                except Exception as chat_err:
                    await message.reply(
                        f"❌ <b>ᴇʀʀᴏʀ:</b> ʙᴏᴛ ᴄᴀɴɴᴏᴛ ᴀᴄᴄᴇꜱꜱ ᴛʜɪꜱ ᴄʜᴀɴɴᴇʟ.\n\n"
                        f"<b>ᴘᴏꜱꜱɪʙʟᴇ ʀᴇᴀꜱᴏɴꜱ:</b>\n"
                        f"• ʙᴏᴛ ɪꜱ ɴᴏᴛ ᴀᴅᴅᴇᴅ ᴛᴏ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ\n"
                        f"• ʙᴏᴛ ɪꜱ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ\n"
                        f"• ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ\n\n"
                        f"<code>{str(chat_err)}</code>",
                        parse_mode=enums.ParseMode.HTML
                    )
                    return
                
                # Add to database
                success = await Seishiro.set_default_channel(cid)
                
                if not success:
                    await message.reply("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴅᴀᴛᴀʙᴀꜱᴇ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ.")
                    return
                
                # Success - clear state and send message
                if success:
                    await message.reply(
                        get_styled_text(
                            f"✅ ᴀᴅᴅᴇᴅ ᴜᴘʟᴏᴀᴅ ᴄʜᴀɴɴᴇʟ:\n\n"
                            f"📢 <b>ᴛɪᴛʟᴇ:</b> {title}\n"
                            f"🆔 <b>ɪᴅ:</b> <code>{cid}</code>",
                            reply_markup=InlineKeyboardMarkup(buttons),
                            parse_mode=enums.ParseMode.HTML)
                    )
                    buttons = [
                        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="header_auto_update_channels")],
                        [InlineKeyboardButton("❄ ᴄʟᴏꜱᴇ ❄", callback_data="stats_close")]
                    ]
                    
            except ValueError:
                await message.reply(
                    "❌ ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ ꜰᴏʀᴍᴀᴛ.\n\n"
                    "ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍᴇʀɪᴄ ɪᴅ (ᴇ.ɢ., -100123456789)"
                )
                return
            except Exception as e:
                await message.reply(f"❌ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ: {str(e)}")
                return

        elif state == "waiting_auc_rem_id":
            input_text = message.text.strip()
            
            if not input_text:
                await message.reply("❌ ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ.")
                return
                
            try:
                cid = int(input_text)
                success = await Seishiro.remove_default_channel(cid)
                
                if not success:
                    await message.reply(
                        "❌ ᴄʜᴀɴɴᴇʟ ɪᴅ ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ ᴜᴘʟᴏᴀᴅ ᴄʜᴀɴɴᴇʟꜱ ʟɪꜱᴛ.\n\n"
                        "ᴘʟᴇᴀꜱᴇ ᴄʜᴇᴄᴋ ᴛʜᴇ ɪᴅ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ."
                    )
                    return
                
                # Success - clear state and send message
                if user_id in user_states:
                    del user_states[user_id]
                
                text = get_styled_text(
                    f"✅ ʀᴇᴍᴏᴠᴇᴅ ᴜᴘʟᴏᴀᴅ ᴄʜᴀɴɴᴇʟ:\n\n"
                    f"🆔 <b>ɪᴅ:</b> <code>{cid}</code>"
                )
                buttons = [
                    [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="header_auto_update_channels")],
                    [InlineKeyboardButton("❄ ᴄʟᴏꜱᴇ ❄", callback_data="stats_close")]
                ]
                await message.reply(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    parse_mode=enums.ParseMode.HTML
                )
                    
            except ValueError:
                await message.reply(
                    "❌ ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ ꜰᴏʀᴍᴀᴛ.\n\n"
                    "ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍᴇʀɪᴄ ɪᴅ (ᴇ.ɢ., -100123456789)"
                )
                return
            except Exception as e:
                await message.reply(f"❌ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ: {str(e)}")
                return
        
        elif state == "waiting_password":
            if message.text.upper() == "OFF":
                await Seishiro.set_config("pdf_password", None)
                await message.reply(
                    get_styled_text("✅ ᴘᴀꜱꜱᴡᴏʀᴅ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ᴅɪꜱᴀʙʟᴇᴅ."),
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                await Seishiro.set_config("pdf_password", message.text)
                await message.reply(
                    get_styled_text(f"✅ ᴘᴀꜱꜱᴡᴏʀᴅ ꜱᴇᴛ: {message.text}"),
                    parse_mode=enums.ParseMode.HTML
                )

        elif state == "waiting_merge_size":
            try:
                size = int(message.text)
                await Seishiro.set_config("merge_size_limit", size)
                await message.reply(
                    get_styled_text(f"✅ ᴍᴇʀɢᴇ ꜱɪᴢᴇ ʟɪᴍɪᴛ: {size}ᴍʙ"),
                    parse_mode=enums.ParseMode.HTML
                )
            except ValueError:
                await message.reply("❌ ꜱᴇɴᴅ ᴀ ɴᴜᴍʙᴇʀ.")
                return

        elif state == "waiting_regex":
            await Seishiro.set_config("filename_regex", message.text)
            await message.reply(
                get_styled_text("✅ ʀᴇɢᴇx ᴘᴀᴛᴛᴇʀɴ ꜱᴀᴠᴇᴅ."),
                parse_mode=enums.ParseMode.HTML
            )

        elif state == "waiting_update_text":
            await Seishiro.set_config("update_text", message.text)
            await message.reply(
                get_styled_text("✅ ᴜᴘᴅᴀᴛᴇ ᴛᴇxᴛ ꜱᴀᴠᴇᴅ."),
                parse_mode=enums.ParseMode.HTML
            )
            
        elif state == "waiting_interval":
            try:
                val = int(message.text)
                if not (60 <= val <= 3600):
                    await message.reply("❌ ᴠᴀʟᴜᴇ ᴏᴜᴛ ᴏꜰ ʀᴀɴɢᴇ (60-3600).")
                    return

                if await Seishiro.set_check_interval(val):
                    await message.reply(
                        get_styled_text(f"✅ ᴄʜᴇᴄᴋ ɪɴᴛᴇʀᴠᴀʟ ꜱᴇᴛ: {val}ꜱ"),
                        parse_mode=enums.ParseMode.HTML
                    )
                else:
                    await message.reply("❌ ᴇʀʀᴏʀ ꜱᴇᴛᴛɪɴɢ ɪɴᴛᴇʀᴠᴀʟ.")
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.")
                return

        elif state == "waiting_fsub_id":
            try:
                cid = int(message.text)
                await client.get_chat(cid)
                await Seishiro.add_fsub_channel(cid)
                await message.reply(
                    get_styled_text(f"✅ ꜰꜱᴜʙ ᴄʜᴀɴɴᴇʟ ᴀᴅᴅᴇᴅ: {cid}"),
                    parse_mode=enums.ParseMode.HTML
                )
            except Exception:
                await message.reply("❌ ʙᴏᴛ ᴄᴀɴɴᴏᴛ ᴀᴄᴄᴇꜱꜱ ᴛʜɪꜱ ᴄʜᴀɴɴᴇʟ. ᴀᴅᴅ ʙᴏᴛ ᴀꜱ ᴀᴅᴍɪɴ ꜰɪʀꜱᴛ!")
                return

        elif state == "waiting_fsub_rem_id":
            try:
                cid = int(message.text)
                if await Seishiro.remove_fsub_channel(cid):
                    await message.reply(
                        get_styled_text(f"✅ ꜰꜱᴜʙ ᴄʜᴀɴɴᴇʟ ʀᴇᴍᴏᴠᴇᴅ: {cid}"),
                        parse_mode=enums.ParseMode.HTML
                    )
                else:
                    await message.reply("❌ ᴄʜᴀɴɴᴇʟ ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ ꜰꜱᴜʙ ʟɪꜱᴛ.")
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ɪᴅ.")
                return

        elif state == "waiting_wm_text":
            wm = await Seishiro.get_watermark() or {}
            await Seishiro.set_watermark(
                text=message.text,
                position=wm.get("position", "bottom-right"),
                color=wm.get("color", "#FFFFFF"),
                opacity=wm.get("opacity", 128),
                font_size=wm.get("font_size", 20)
            )
            await message.reply(
                get_styled_text("✅ ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴛᴇxᴛ ᴜᴘᴅᴀᴛᴇᴅ!"),
                parse_mode=enums.ParseMode.HTML
            )

        elif state == "waiting_wm_color":
            color = message.text.strip()
            if not color.startswith("#") or len(color) not in [4, 7]:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ. ᴜꜱᴇ #ʀʀɢɢʙʙ (ᴇ.ɢ. #ff0000).")
                return
            
            wm = await Seishiro.get_watermark() or {}
            await Seishiro.set_watermark(
                text=wm.get("text", "Default"),
                position=wm.get("position", "bottom-right"),
                color=color,
                opacity=wm.get("opacity", 128),
                font_size=wm.get("font_size", 20)
            )
            await message.reply(
                get_styled_text(f"✅ ᴄᴏʟᴏʀ ꜱᴇᴛ: {color}"),
                parse_mode=enums.ParseMode.HTML
            )

        elif state == "waiting_wm_opacity":
            try:
                op = int(message.text)
                if not (0 <= op <= 255):
                    raise ValueError
                
                wm = await Seishiro.get_watermark() or {}
                await Seishiro.set_watermark(
                    text=wm.get("text", "Default"),
                    position=wm.get("position", "bottom-right"),
                    color=wm.get("color", "#FFFFFF"),
                    opacity=op,
                    font_size=wm.get("font_size", 20)
                )
                await message.reply(
                    get_styled_text(f"✅ ᴏᴘᴀᴄɪᴛʏ ꜱᴇᴛ: {op}"),
                    parse_mode=enums.ParseMode.HTML
                )
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ (0-255).")
                return

        elif state == "waiting_deltimer":
            try:
                val = int(message.text)
                await Seishiro.set_del_timer(val)
                await message.reply(
                    get_styled_text(f"✅ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ ꜱᴇᴛ: {val}ꜱ"),
                    parse_mode=enums.ParseMode.HTML
                )
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.")
                return

        elif state == "waiting_thumb":
            if message.photo:
                file_id = message.photo.file_id
                await Seishiro.set_config("custom_thumbnail", file_id)
                await message.reply(
                    get_styled_text("✅ ᴄᴜꜱᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ ꜱᴇᴛ!"),
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                await message.reply("❌ ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ.")
                return

        elif state in ["waiting_channel_stickers", "waiting_update_sticker"]:
            val = None
            if message.sticker:
                val = message.sticker.file_id
            elif message.text:
                txt = message.text.strip()
                if len(txt) > 10:
                    val = txt
            
            if not val:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ɪɴᴘᴜᴛ. ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴀ ꜱᴛɪᴄᴋᴇʀ ᴏʀ ᴀ ᴠᴀʟɪᴅ ꜰɪʟᴇ ɪᴅ ꜱᴛʀɪɴɢ.")
                return

            key = state.replace("waiting_", "")
            await Seishiro.set_config(key, val)
            await message.reply(
                get_styled_text(f"✅ {key.replace('_', ' ').title()} ꜱᴀᴠᴇᴅ.\nɪᴅ: <code>{val}</code>"),
                parse_mode=enums.ParseMode.HTML
            )

        elif state == "waiting_add_admin":
            try:
                new_admin_id = int(message.text)
                await Seishiro.add_admin(new_admin_id)
                await message.reply(
                    get_styled_text(f"✅ ᴜꜱᴇʀ {new_admin_id} ᴀᴅᴅᴇᴅ ᴀꜱ ᴀᴅᴍɪɴ."),
                    parse_mode=enums.ParseMode.HTML
                )
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ.")
                return
            except Exception as e:
                await message.reply(f"❌ ᴇʀʀᴏʀ: {e}")
                return

        elif state == "waiting_del_admin":
            try:
                del_id = int(message.text)
                if del_id == Config.USER_ID:
                    await message.reply("❌ ᴄᴀɴɴᴏᴛ ʀᴇᴍᴏᴠᴇ ᴏᴡɴᴇʀ.")
                    return
                await Seishiro.remove_admin(del_id)
                await message.reply(
                    get_styled_text(f"✅ ᴜꜱᴇʀ {del_id} ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ᴀᴅᴍɪɴꜱ."),
                    parse_mode=enums.ParseMode.HTML
                )
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ.")
                return
            except Exception as e:
                await message.reply(f"❌ ᴇʀʀᴏʀ: {e}")
                return

        elif state == "waiting_broadcast_msg":
            try:
                status_msg = await message.reply("🚀 ᴘʀᴇᴘᴀʀɪɴɢ ʙʀᴏᴀᴅᴄᴀꜱᴛ...")
                all_users = await Seishiro.get_all_users()
                total = len(all_users)
                successful = 0
                unsuccessful = 0
                
                for uid in all_users:
                    try:
                        await message.copy(chat_id=uid)
                        successful += 1
                    except Exception:
                        unsuccessful += 1
                        
                    if (successful + unsuccessful) % 20 == 0:
                        try:
                            await status_msg.edit(f"🚀 ʙʀᴏᴀᴅᴄᴀꜱᴛɪɴɢ... {successful}/{total} ꜱᴇɴᴛ.")
                        except:
                            pass
                
                await status_msg.edit(
                    f"✅ **ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇ**\n\n"
                    f"👥 ᴛᴏᴛᴀʟ: {total}\n"
                    f"✅ ꜱᴇɴᴛ: {successful}\n"
                    f"❌ ꜰᴀɪʟᴇᴅ: {unsuccessful}",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
            except Exception as e:
                await message.reply(f"❌ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴇʀʀᴏʀ: {e}")
                return

        elif state == "waiting_ban_id":
            try:
                target_id = int(message.text)
                if target_id in [Config.USER_ID, message.from_user.id]:
                    await message.reply("❌ ᴄᴀɴɴᴏᴛ ʙᴀɴ ᴏᴡɴᴇʀ ᴏʀ ꜱᴇʟꜰ.")
                    return
                if await Seishiro.ban_user(target_id):
                    await message.reply(
                        get_styled_text(f"🚫 ᴜꜱᴇʀ {target_id} ʜᴀꜱ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ."),
                        parse_mode=enums.ParseMode.HTML
                    )
                else:
                    await message.reply("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ʙᴀɴ ᴜꜱᴇʀ.")
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ.")
                return

        elif state == "waiting_unban_id":
            try:
                target_id = int(message.text)
                if await Seishiro.unban_user(target_id):
                    await message.reply(
                        get_styled_text(f"✅ ᴜꜱᴇʀ {target_id} ʜᴀꜱ ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ."),
                        parse_mode=enums.ParseMode.HTML
                    )
                else:
                    await message.reply("❌ ᴜꜱᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ ʙᴀɴ ʟɪꜱᴛ.")
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ.")
                return

        # Clear the waiting state after successful handling
        if user_id in user_states:
            del user_states[user_id]

    except Exception as e:
        await message.reply(f"❌ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ: {e}")
        if user_id in user_states:
            del user_states[user_id]
