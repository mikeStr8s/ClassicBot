from PIL import Image, ImageDraw, ImageFont, ImageOps

import textwrap
import uuid


BORDER_COLOR = (119,119,119)
BG_COLOR = (8,13,33)
WIDTH = 320
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
}

def build_tooltip_image(text_list):
    num_lines = get_lines_of_text(text_list)
    size = (WIDTH, LINE_HEIGHT * num_lines + LARGE_PADDING)
    img = Image.new('RGB', size,color=BG_COLOR)
    pos = SMALL_PADDING
    for item in text_list:
        if isinstance(item['text'], str) and len(item['text']) > MAX_CHARS:
            for text in textwrap.wrap(item['text'], MAX_CHARS):
                add_text(img, text, pos, COLORS[item['color']])
                pos += LINE_HEIGHT
        else:
            try:
                if item['indent']:
                    add_text(img, item['text'], pos, COLORS[item['color']], 15)
            except KeyError:
                add_text(img, item['text'], pos, COLORS[item['color']])
            pos += LINE_HEIGHT
    img = add_border(img)
    uid = str(uuid.uuid4()) + '.png'
    img.save(uid)
    return uid


def add_text(img, text, pos, color, indent=0):
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\micross.ttf', 12)
    d = ImageDraw.Draw(img)
    if isinstance(text, list):
        d.text((SMALL_PADDING, pos), text[0], font=fnt, fill=color)
        offset = d.textsize(text[1])
        print('here')
        d.text((WIDTH - offset[0] - LARGE_PADDING, pos), text[1], font=fnt, fill=color)
    else:
        d.text((5 + indent, pos), text, font=fnt, fill=color)


def add_border(img):
    return ImageOps.expand(img, 1, BORDER_COLOR)


def get_lines_of_text(text_list):
    num_lines = 0
    for item in text_list:
        if isinstance(item['text'], str):
            if len(item['text']) > MAX_CHARS:
                num_lines += len(textwrap.wrap(item['text'], MAX_CHARS))
            else:
                num_lines += 1
        else:
            num_lines += 1
    return num_lines