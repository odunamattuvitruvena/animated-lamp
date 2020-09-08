#TM_Adminz
#MonkAno

import os
import re
import shlex
import random
import asyncio
import logging
import datetime
import traceback

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from ..config import Config


log = logging.getLogger(__name__)


def is_valid_file(msg):
    if not msg.media:
        return False
    if msg.video:
        return True
    if (msg.document) and any(mime in msg.document.mime_type for mime in ['video', "application/octet-stream"]):
        return True
    return False


def is_url(text):
    return text.startswith('http')


def get_random_start_at(seconds, dur=0):
    return random.randint(0, seconds-dur)


async def run_subprocess(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    return await process.communicate()


async def generate_thumbnail_file(file_path, uid):
    output_folder = Config.THUMB_OP_FLDR.joinpath(uid)
    os.makedirs(output_folder, exist_ok=True)
    
    thumb_file = output_folder.joinpath('thumb.jpg')
    ffmpeg_cmd = f"ffmpeg -ss 0 -i '{file_path}' -vframes 1 -vf \"scale=320:-1\" -y '{thumb_file}'"
    output = await run_subprocess(ffmpeg_cmd)
    if not thumb_file.exists():
        return None
    return thumb_file


def pack_id(msg):
    file_id = 0
    chat_id_offset = 2
    pack_bits = 32
    msg_id_offset = pack_bits + chat_id_offset
    
    file_id |= msg.chat.id << chat_id_offset
    file_id |= msg.message_id << msg_id_offset
    return file_id


def generate_stream_link(media_msg):
    file_id = pack_id(media_msg)
    return f"{Config.HOST}/stream/{file_id}"


async def get_dimentions(input_file_link):
    ffprobe_cmd = f"ffprobe -v error -show_entries stream=width,height -of csv=p=0:s=x -select_streams v:0 {shlex.quote(input_file_link)}"
    output = await run_subprocess(ffprobe_cmd)
    log.debug(output)
    try:
        width, height = [int(i.strip()) for i in output[0].decode().split('x')]
    except Exception as e:
        log.debug(e, exc_info=True)
        width, height = 1280, 534
    return width, height


async def get_duration(input_file_link):
    ffmpeg_dur_cmd = f"ffprobe -v error -show_entries format=duration -of csv=p=0:s=x -select_streams v:0 {shlex.quote(input_file_link)}"
    out, err = await run_subprocess(ffmpeg_dur_cmd)
    log.debug(f"{out} \n {err}")
    out = out.decode().strip()
    if not out:
        return err.decode()
    duration = round(float(out))
    if duration:
        return duration
    return 'No duration!'


async def fix_subtitle_codec(file_link):
    fixable_codecs = ['mov_text']
    
    ffmpeg_dur_cmd = f"ffprobe -v error -select_streams s -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1  {shlex.quote(file_link)}"
    
    out, err = await run_subprocess(ffmpeg_dur_cmd)
    log.debug(f"{out} \n {err}")
    out = out.decode().strip()
    if not out:
        return ''
    
    fix_cmd = ''
    codecs = [i.strip() for i in out.split('\n')]
    for indx, codec in enumerate(codecs):
        if any(fixable_codec in codec for fixable_codec in fixable_codecs):
            fix_cmd += f'-c:s:{indx} srt '
    
    return fix_cmd
    

async def edit_message_text(m, **kwargs):
    while True:
        try:
            return await m.edit_message_text(**kwargs)
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except:
            break


async def display_settings(c, m, cb=False):
    chat_id = m.from_user.id if cb else m.chat.id
    
    as_file = await c.db.is_as_file(chat_id)
    as_round = await c.db.is_as_round(chat_id)
    watermark_text = await c.db.get_watermark_text(chat_id)
    sample_duration = await c.db.get_sample_duration(chat_id)
    watermark_color_code = await c.db.get_watermark_color(chat_id)
    screenshot_mode = await c.db.get_screenshot_mode(chat_id)
    font_size = await c.db.get_font_size(chat_id)
    
    sv_btn = [
        InlineKeyboardButton("Sample Video Duration", 'rj'),
        InlineKeyboardButton(f"{sample_duration}s", 'set+sv')
    ]
    wc_btn = [
        InlineKeyboardButton("Watermark Color", 'rj'),
        InlineKeyboardButton(f"{Config.COLORS[watermark_color_code]}", 'set+wc')
    ]
    fs_btn = [
        InlineKeyboardButton("Watermark Font Size", 'rj'),
        InlineKeyboardButton(f"{Config.FONT_SIZES_NAME[font_size]}", 'set+fs')
    ]
    as_file_btn = [InlineKeyboardButton("Upload Mode", 'rj')]
    wm_btn = [InlineKeyboardButton("Watermark", 'rj')]
    sm_btn = [InlineKeyboardButton("Screenshot Generation Mode", 'rj')]
    
    
    if as_file:
        as_file_btn.append(InlineKeyboardButton("📁 Uploading as Document.", 'set+af'))
    else:
        as_file_btn.append(InlineKeyboardButton("🖼️ Uploading as Image.", 'set+af'))
    
    if watermark_text:
        wm_btn.append(InlineKeyboardButton(f"{watermark_text}", 'set+wm'))
    else:
        wm_btn.append(InlineKeyboardButton("No watermark exists!", 'set+wm'))
    
    if screenshot_mode == 0:
        sm_btn.append(InlineKeyboardButton("Equally spaced screenshots", 'set+sm'))
    else:
        sm_btn.append(InlineKeyboardButton("Random screenshots", 'set+sm'))
    
    settings_btn = [as_file_btn, wm_btn, wc_btn, fs_btn, sv_btn, sm_btn]
    
    if cb:
        try:
            await m.edit_message_reply_markup(
                InlineKeyboardMarkup(settings_btn)
            )
        except:
            pass
        return
    
    await m.reply_text(
        text = f"Here You can configure my behavior.",
        quote=True,
        reply_markup=InlineKeyboardMarkup(settings_btn)
    )


def gen_ik_buttons():
    btns = []
    i_keyboard = []
    for i in range(2, 11):
        i_keyboard.append(
            InlineKeyboardButton(
                f"{i}",
                f"scht+{i}"
            )
        )
        if (i>2) and (i%2) == 1:
            btns.append(i_keyboard)
            i_keyboard = []
        if i==10:
            btns.append(i_keyboard)
    btns.append([InlineKeyboardButton('Manual Screenshots!', 'mscht')])
    btns.append([InlineKeyboardButton('Trim Video!', 'trim')])
    return btns
