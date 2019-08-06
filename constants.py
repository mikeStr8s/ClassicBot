ITEM_URL = 'https://classic.wowhead.com/item={0}'

OPEN_SEARCH = 'http://{}classic.wowhead.com/search?q={}&opensearch'
TOOLTIP = 'https://{}classic.wowhead.com/tooltip/{}/{}&json&power'
ICON = 'https://wow.zamimg.com/images/wow/icons/large/{0}.jpg'
MONEY = 'https://wow.zamimg.com/images/icons/money-{}.gif'

SEARCH_OBJECT_TYPE = {
    'item': 3,
    'spell': 6,
    'npc': 1
}

Q_COLORS = ['q', 'q0', 'q1', 'q2', 'q3', 'q4', 'q5']

TOOLTIP_ARGS = ['indent', 'split', 'whtt-sellprice']

BORDER_COLOR = (119, 119, 119)
BG_COLOR = (8, 13, 33)
DISCORD_BG = (54, 57, 63)
WIDTH = 320
HEIGHT = lambda x: LARGE_PADDING + LINE_HEIGHT * x
RIGHT_ALIGN = lambda x: WIDTH - LARGE_PADDING - x
LINE_HEIGHT = 17
LARGE_PADDING = 10
SMALL_PADDING = 5
INDENT = 20
MAX_CHARS = 47
COLORS = {
    'q': (255, 209, 0),  # Yellow (used for item levels)
    'q0': (157, 157, 157),  # Grey
    'q1': (255, 255, 255),  # Common
    'q2': (30, 255, 0),  # Uncommon
    'q3': (0, 112, 221),  # Rare
    'q4': (163, 53, 238),  # Epic
    'q5': (255, 128, 0),  # Legendary
    'g': (211, 185, 63),
    's': (143, 143, 143),
    'c': (139, 70, 34)
}
