# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat


from pyrogram import Client, filters, enums
from config import Config
from Database.database import Seishiro
from pyrogram.types import InputMediaPhoto
from functools import wraps
import random

def admin_filter(filter, client, message):
    return message.from_user.id == Config.USER_ID or message.from_user.id in Seishiro.ADMINS

admin = filters.create(admin_filter)

user_states = {}
user_data = {} # For storing interaction context (e.g. download selections)
WAITING_RENAME_DB = "WAITING_RENAME_DB"
WAITING_THUMBNAIL = "WAITING_THUMBNAIL" 
WAITING_WATERMARK = "WAITING_WATERMARK"
WAITING_CHANNEL_ID = "WAITING_CHANNEL_ID"
WAITING_DUMP_CHANNEL = "WAITING_DUMP_CHANNEL"
WAITING_CHAPTER_INPUT = "WAITING_CHAPTER_INPUT" # NEW

def get_styled_text(text: str) -> str:
    """
    Apply consistent styling: Italic and Blockquote.
    HTML Format: <blockquote><i>text</i></blockquote>
    """
    return f"<blockquote><i>{text}</i></blockquote>"
    
def get_random_pic():
    if hasattr(Config, "PICS") and Config.PICS:
        return random.choice(Config.PICS)
    return "https://ibb.co/mVkSySr7"

async def edit_msg_with_pic(message, text, buttons):
    """
    Edits a Message with a new random photo and text.
    If original Message has photo, uses edit_media.
    Else, deletes and sends new photo.
    """
    pic = get_random_pic()
    try:
        if message.photo:
            await message.edit_media(
                media=InputMediaPhoto(media=pic, caption=text),
                reply_markup=buttons
            )
        else:
            await message.delete()
            await message.reply_photo(
                photo=pic,
                caption=text,
                reply_markup=buttons,
                parse_mode=enums.ParseMode.HTML
            )
    except Exception as e:
        try:
             await message.delete()
             await message.reply_photo(pic, caption=text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML)
        except:
             pass

def check_ban(func):
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        user_id = message.from_user.id
        logger.debug(f"check_ban decorator called for user {user_id}")
        
        try:
            # Check if user is banned
            user = await Seishiro.is_user_banned(user_id)
            
            if user:
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ ʜᴇʀᴇ...!!", url="https://t.me/rexbots_official")]]
                )
                logger.debug(f"User {user_id} is banned, sending ban message.")
                return await message.reply_text(
                    "Wᴛғ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴜsɪɴɢ ᴍᴇ ʙʏ ᴏᴜʀ ᴀᴅᴍɪɴ/ᴏᴡɴᴇʀ . Iғ ʏᴏᴜ ᴛʜɪɴᴋs ɪᴛ's ᴍɪsᴛᴀᴋᴇ ᴄʟɪᴄᴋ ᴏɴ ᴄᴏɴᴛᴀᴄᴛ ʜᴇʀᴇ...!!",
                    reply_markup=keyboard
                )
            
            logger.debug(f"User {user_id} is not banned, proceeding with function call.")
            return await func(client, message, *args, **kwargs)
        
        except Exception as e:
            logger.error(f"FATAL ERROR in check_ban: {e}")
            await message.reply_text(f"An unexpected error occurred: {e}. Please contact the developer.")
            return
    return wrapper

def check_fsub(func):
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        user_id = message.from_user.id
        logger.debug(f"check_fsub decorator called for user {user_id}")

        async def is_sub(client, user_id, channel_id):
            try:
                member = await client.get_chat_member(channel_id, user_id)
                return member.status in {
                    ChatMemberStatus.OWNER,
                    ChatMemberStatus.ADMINISTRATOR,
                    ChatMemberStatus.MEMBER
                }
            except UserNotParticipant:
                mode = await Seishiro.get_channel_mode(channel_id) or await Seishiro.get_channel_mode_all(channel_id)
                if mode == "on":
                    exists = await Seishiro.req_user_exist(channel_id, user_id)
                    return exists
                return False
            except Exception as e:
                logger.error(f"Error in is_sub(): {e}")
                return False

        async def is_subscribed(client, user_id):
            channel_ids = await Seishiro.get_fsub_channels()
            if not channel_ids:
                return True
            if user_id == OWNER_ID:
                return True
            for cid in channel_ids:
                if not await is_sub(client, user_id, cid):
                    mode = await Seishiro.get_channel_mode(cid) or await Seishiro.get_channel_mode_all(cid)
                    if mode == "on":
                        await asyncio.sleep(2)
                        if await is_sub(client, user_id, cid):
                            continue
                    return False
            return True

        async def not_joined(client, message):
            logger.debug(f"not_joined function called for user {message.from_user.id}")
            temp = await message.reply("<b><i>ᴡᴀɪᴛ ᴀ sᴇᴄ..</i></b>")

            # Add a check to ensure temp message exists before proceeding
            if not temp:
                logger.warning("Failed to send temporary message in not_joined")
                return

            user_id = message.from_user.id
            buttons = []
            count = 0

            try:
                all_channels = await Seishiro.get_fsub_channels()
                for chat_id in all_channels:
                    await message.reply_chat_action(ChatAction.TYPING)

                    is_member = False
                    try:
                        member = await client.get_chat_member(chat_id, user_id)
                        is_member = member.status in {
                            ChatMemberStatus.OWNER,
                            ChatMemberStatus.ADMINISTRATOR,
                            ChatMemberStatus.MEMBER
                        }
                    except UserNotParticipant:
                        is_member = False
                    except Exception as e:
                        is_member = False
                        logger.error(f"Error checking member in not_joined: {e}")

                    if not is_member:
                        try:
                            if chat_id in chat_data_cache:
                                data = chat_data_cache[chat_id]
                            else:
                                data = await client.get_chat(chat_id)
                                chat_data_cache[chat_id] = data

                            name = data.title
                            mode = await Seishiro.get_channel_mode(chat_id)

                            if mode == "on" and not data.username:
                                invite = await client.create_chat_invite_link(
                                    chat_id=chat_id,
                                    creates_join_request=True,
                                    expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY) if FSUB_LINK_EXPIRY else None
                                )
                                link = invite.invite_link
                            else:
                                if data.username:
                                    link = f"https://t.me/{data.username}"
                                else:
                                    invite = await client.create_chat_invite_link(
                                        chat_id=chat_id,
                                        expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY) if FSUB_LINK_EXPIRY else None
                                    )
                                    link = invite.invite_link

                            buttons.append([InlineKeyboardButton(text=name, url=link)])
                            count += 1
                            try:
                                await temp.edit(f"<b>{'! ' * count}</b>")
                            except Exception as e:
                                logger.warning(f"Failed to edit message in not_joined: {e}")

                        except Exception as e:
                            logger.error(f"Error with chat {chat_id}: {e}")
                            await temp.edit(
                                f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @seishiro_obito</i></b>\n"
                                f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
                            )
                            return

                try:
                    buttons.append([
                        InlineKeyboardButton(
                            text='• Jᴏɪɴᴇᴅ •',
                            url=f"https://t.me/{BOT_USERNAME}?start={message.command[1]}"
                        )
                    ])
                except IndexError:
                    pass

                text = "<b>Yᴏᴜ Bᴀᴋᴋᴀᴀ...!! \n\n<blockquote>Jᴏɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍʏ ᴏᴛʜᴇʀᴡɪsᴇ Yᴏᴜ ᴀʀᴇ ɪɴ ʙɪɢ sʜɪᴛ...!!</blockquote></b>"
                
                logger.debug(f"Sending final reply photo to user {user_id}")
                await message.reply_photo(
                    photo=pic,
                    caption=text,
                    reply_markup=InlineKeyboardMarkup(buttons),
                )

            except Exception as e:
                logger.error(f"Final Error in not_joined: {e}")
                await temp.edit(
                    f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @seishiro_obito</i></b>\n"
                    f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
                )
        
        try:
            is_sub_status = await is_subscribed(client, user_id)
            logger.debug(f"User {user_id} subscribed status: {is_sub_status}")
            
            if not is_sub_status:
                logger.debug(f"User {user_id} is not subscribed, calling not_joined.")
                return await not_joined(client, message)
            
            logger.debug(f"User {user_id} is subscribed, proceeding with function call.")
            return await func(client, message, *args, **kwargs)
        
        except Exception as e:
            logger.error(f"FATAL ERROR in check_fsub: {e}")
            await message.reply_text(f"An unexpected error occurred: {e}. Please contact the developer.")
            return
    return wrapper

# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat
