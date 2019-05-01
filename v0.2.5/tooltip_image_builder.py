from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO

import textwrap
import uuid
import requests


BORDER_COLOR = (119,119,119)
BG_COLOR = (8,13,33)
WIDTH = 320
HEIGHT = lambda x: LARGE_PADDING + LINE_HEIGHT * x
RIGHT_ALIGN = lambda x: WIDTH - LARGE_PADDING - x
LINE_HEIGHT = 17
LARGE_PADDING = 10
SMALL_PADDING = 5
MAX_CHARS = 49
COLORS = {
    'q': (255,209,0),   # Yellow (used for item levels)
    'q0': (157,157,157),    # Grey
    'q1': (255,255,255),    # Common
    'q2': (30,255,0),   # Uncommon
    'q3': (0,112,221),  # Rare
    'q4': (163,53,238), # Epic
    'q5': (255,128,0),  # Legendary
    'g': (211,185,63),
    's': (143,143,143),
    'c': (139,70,34)
}


def build_tooltip(text_list, icon_url):
    text_list = get_wrapped_text(text_list)
    img = Image.new('RGB', (WIDTH, HEIGHT(len(text_list))), color=BG_COLOR)
    pos = SMALL_PADDING
    for line in text_list:
        if line['args'] or line['args'] is not None:
            dispatch_line_item(img, line, pos)
        else:
            add_text(img, line['text'], pos, COLORS[line['color']])
        pos += LINE_HEIGHT
    img = add_border(img)
    img = add_icon(img, icon_url)
    uid = str(uuid.uuid4()) + '.png'
    img.save(uid)
    return uid


def add_icon(img, url):
    response = requests.get(url)
    icon = Image.open(BytesIO(response.content)).resize((3*LINE_HEIGHT, 3*LINE_HEIGHT))
    img.paste(icon, (320-(3*LINE_HEIGHT), 1))
    return img


def dispatch_line_item(img, line, pos):
    if 'indent' in line['args']:
        add_text(img, line['text'], pos, COLORS[line['color']], 15)
    elif 'split' in line['args']:
        add_text(img, line['text'], pos, COLORS[line['color']])
    elif 'money' in line['args']:
        add_money_text(img, line, pos)


def add_text(img, text, pos, color, indent=0):
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\micross.ttf', 12)
    d = ImageDraw.Draw(img)
    if isinstance(text, list):
        d.text((SMALL_PADDING, pos), text[0], font=fnt, fill=color)
        offset = d.textsize(text[1])
        d.text((RIGHT_ALIGN(offset[0]), pos), text[1], font=fnt, fill=color)
    else:
        d.text((5 + indent, pos), text, font=fnt, fill=color)


def add_money_text(img, text, pos):
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\micross.ttf', 12)
    d = ImageDraw.Draw(img)
    delims = {'money':'q1', 'moneygold':'g', 'moneysilver':'s', 'moneycopper':'c'}
    prev_text = ''
    offset = (0,0)
    for idx, arg in enumerate(text['args']):
        temp = text['text'][idx]
        d.text((SMALL_PADDING + offset[0], pos), temp, font=fnt, fill=COLORS['q1'])
        prev_text += temp
        offset = d.textsize(prev_text)
        if idx > 0:
            d.text((SMALL_PADDING + offset[0], pos), ' ' + delims[arg], font=fnt, fill=COLORS[delims[arg]])
            prev_text += ' ' + delims[arg]
            offset = d.textsize(prev_text)


def add_border(img):
    return ImageOps.expand(img, 1, BORDER_COLOR)


def get_wrapped_text(text_list):
    additional = []
    for item in text_list:
        if isinstance(item['text'], str):
            if len(item['text']) > MAX_CHARS:
                broken = textwrap.wrap(item['text'], MAX_CHARS)
                for seg in broken:
                    temp = dict()
                    for key, value in item.items():
                        temp[key] = value
                    temp['text'] = seg
                    additional.append(temp)
            else:
                additional.append(item)
        else:
            additional.append(item)
    return additional