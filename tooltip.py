import textwrap
import requests
import uuid

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from constants import MAX_CHARS, ICON, LINE_HEIGHT, SMALL_PADDING, HEIGHT, DISCORD_BG, BG_COLOR, COLORS, INDENT, MONEY


def build_tooltip(lines, icon_name):
    lines, max_length = wrap_text(lines)
    icon = get_icon(icon_name)
    container = get_image_container(icon.size, len(lines), max_length)
    container.paste(icon)
    tt_container = get_tooltip_container(max_length, len(lines))
    add_tooltip_text(tt_container, lines, max_length)
    container.paste(tt_container, (icon.size[0], 0))
    img_id = str(uuid.uuid4()) + '.png'
    container.save(img_id)
    return img_id


def add_tooltip_text(container, lines, max_length):
    fnt = ImageFont.truetype('micross.ttf', 12)
    for idx, line in enumerate(lines):
        drawer = ImageDraw.Draw(container)
        if line['args'] is not None:
            icons = add_style_text(drawer, line, idx * LINE_HEIGHT, fnt, max_length)
            if icons:
                for icon in icons:
                    container.paste(icon['icon'], icon['pos'])
        else:
            drawer.text((SMALL_PADDING, idx * LINE_HEIGHT), line['text'], font=fnt, fill=COLORS[line['color']])


def add_style_text(drawer, line, position, fnt, max_length):
    style = line['args']['style']
    extra_icons = []
    if style == 'indent':
        drawer.text((INDENT, position), line['text'], font=fnt, fill=COLORS[line['color']])
    elif style == 'split':
        idx = line['args']['value'][0]
        one = line['text'][:idx]
        two = line['text'][idx:]
        offset = (max_length + SMALL_PADDING) - drawer.textsize(two)[0]
        drawer.text((SMALL_PADDING, position), one, font=fnt, fill=COLORS[line['color']])
        drawer.text((offset, position), two, font=fnt, fill=COLORS[line['color']])
    elif style == 'whtt-sellprice':
        text = line['text']
        values = line['args']['value']
        offset = SMALL_PADDING
        inc = 0
        for value in values:
            for label, idx in value.items():
                if label == 'pre':
                    temp = text[inc:inc + idx]
                    drawer.text((offset, position), temp, font=fnt, fill=COLORS[line['color']])
                    offset += drawer.textsize(temp)[0]
                    inc += idx
                else:
                    temp = text[inc:inc + idx]
                    drawer.text((offset, position), temp, font=fnt, fill=COLORS[line['color']])
                    offset += drawer.textsize(temp)[0]
                    icon = get_icon(label, url=MONEY, resize=False)
                    extra_icons.append({'icon': icon, 'pos': (offset + 2, position + 2)})
                    offset += icon.size[0]
                    inc += idx
    return extra_icons


def get_tooltip_container(line_width, num_lines):
    width = line_width + (2 * SMALL_PADDING)
    height = HEIGHT(num_lines)
    return Image.new('RGB', (width, height), color=BG_COLOR)


def get_image_container(icon, lines, line_width):
    container_width = icon[0] + line_width + (2 * SMALL_PADDING)
    container_height = HEIGHT(lines)
    return Image.new('RGB', (container_width, container_height), color=DISCORD_BG)


def get_icon(name, url=ICON, resize=True, dims=(3 * LINE_HEIGHT, 3 * LINE_HEIGHT)):
    response = requests.get(url.format(name))
    if resize:
        icon = Image.open(BytesIO(response.content)).resize(dims)
    else:
        icon = Image.open(BytesIO(response.content))
    return icon


def wrap_text(lines):
    wrapped_lines = []
    max_line = ''
    for line in lines:
        text = line['text']
        if len(text) >= MAX_CHARS:
            split_text = textwrap.wrap(text, MAX_CHARS)
            for segment in split_text:
                temp = dict()
                for key, val in line.items():
                    temp[key] = val
                temp['text'] = segment
                wrapped_lines.append(temp)
                if len(segment) > len(max_line):
                    max_line = segment
        else:
            if line['args'] is not None:
                if line['args']['style'] == 'split':
                    text += '        '
            wrapped_lines.append(line)
            if len(text) > len(max_line):
                max_line = text
    drawer = ImageDraw.Draw(Image.new('RGB', (100, 100), color=BG_COLOR))
    max_line_length = drawer.textsize(max_line, ImageFont.truetype('micross.ttf', 12))[0]
    if max_line_length < 85: max_line_length = 85
    return wrapped_lines, max_line_length
