import re

# Color extraction patterns
HEX_RE = re.compile(r"#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b")
RGB_RE = re.compile(r"rgb\s*\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)")

# Social media hosts
SOCIAL_HOSTS = {
    "x": ("twitter.com", "x.com"),
    "instagram": ("instagram.com",),
    "facebook": ("facebook.com", "fb.com"),
    "youtube": ("youtube.com", "youtu.be"),
    "tiktok": ("tiktok.com",)
}

# Brand-related URL patterns for filtering
BRAND_PATTERNS = [
    "*/brand*",
    "*/branding*",
    "*/identity*",
    "*/communications*",
    "*/marketing*",
    "*/media*",
    "*/logos*",
    "*/downloads*"
]

# Calendar-related URL patterns for filtering
CALENDAR_PATTERNS = [
    "*/calendar*",
    "*/schedule*",
    "*/events*",
    "*/games*",
    "*/matches*",
    "*/fixtures*",
    "*/tickets*"
]

# Event keywords for calendar extraction
EVENT_KEYWORDS = [
    "game", "match", "event", "competition", "tournament", "meet", "championship",
    "vs", "at", "@", "home", "away", "neutral", "final", "semifinal", "quarterfinal"
]

# Image category keywords
IMAGE_CATEGORY_KEYWORDS = {
    'logos': ['logo', 'wordmark', 'brand', 'identity', 'site', 'header'],
    'dashboard_hero': ['hero', 'banner', 'main', 'featured', 'dashboard', 'splash', 'jumbotron'],
    'memory_achievement': ['championship', 'win', 'trophy', 'celebration', 'memory', 'historic', 'legacy', 'champion'],
    'action_shots': ['game', 'play', 'action', 'player', 'team', 'sport', 'match', 'competition'],
    'backgrounds': ['background', 'bg', 'wallpaper', 'pattern', 'texture'],
    'content_news': ['news', 'article', 'story', 'event', 'update', 'announcement'],
    'facilities': ['stadium', 'arena', 'field', 'court', 'facility', 'venue', 'building']
}

# Mascot patterns
MASCOT_PATTERNS = [
    r'trojans?', r'bruins?', r'cardinal', r'gators?', r'bulldogs?', r'wildcats?',
    r'eagles?', r'lions?', r'tigers?', r'bears?', r'hawks?', r'panthers?',
    r'wolves?', r'cougars?', r'falcons?', r'ravens?', r'ducks?', r'beavers?'
]

# Font extraction patterns
FONT_PATTERNS = [
    r"font-family\s*:\s*([^;}{]+)",
    r"font-family\s*=\s*['\"]([^'\"]+)['\"]",
    r"font\s*:\s*[^;]*?([A-Za-z][A-Za-z\s]+?)(?:,|;|$)"
]

# CSS color patterns
CSS_COLOR_PATTERNS = [
    r'color\s*:\s*(#[0-9A-Fa-f]{3,6}|rgb\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\))',
    r'background-color\s*:\s*(#[0-9A-Fa-f]{3,6}|rgb\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\))',
    r'border-color\s*:\s*(#[0-9A-Fa-f]{3,6}|rgb\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\))'
]

# Icon patterns
ICON_PATTERNS = [
    r'<link[^>]*rel\s*=\s*["\'](?:icon|shortcut icon|apple-touch-icon|mask-icon)["\'][^>]*href\s*=\s*["\']([^"\']+)["\']',
    r'<link[^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*rel\s*=\s*["\'](?:icon|shortcut icon|apple-touch-icon|mask-icon)["\']',
    r'<meta[^>]*name\s*=\s*["\']msapplication-TileImage["\'][^>]*content\s*=\s*["\']([^"\']+)["\']'
]

# Brand guide keywords
BRAND_KEYWORDS = ['brand', 'branding', 'identity', 'communications', 'marketing', 'media', 'press', 'media kit']

# Usage guideline patterns
GUIDELINE_PATTERNS = [
    (r'usage\s+guidelines?[^<]*', 'usage_guidelines'),
    (r'brand\s+rules?[^<]*', 'brand_rules'),
    (r'logo\s+usage[^<]*', 'logo_usage'),
    (r'do\s+not[^<]*', 'do_not'),
    (r'requirements?[^<]*', 'requirements'),
    (r'clear\s+space[^<]*', 'clear_space'),
    (r'minimum\s+size[^<]*', 'minimum_size')
]

# Rally cry patterns
RALLY_PATTERNS = [
    r'rally\s+cry[^<]*?([^.!?]+)',
    r'slogan[^<]*?([^.!?]+)',
    r'motto[^<]*?([^.!?]+)'
]

# Team-specific color mappings
TEAM_COLORS = {
    'usc': {
        'primary': ['#990000', '#FFD700'],  # USC Cardinal Red and Gold
        'description': 'USC Trojans colors'
    },
    'boston college': {
        'primary': ['#8B0000', '#FFD700'],  # BC Maroon and Gold
        'description': 'Boston College Eagles colors'
    }
}

# Team-specific font mappings
TEAM_FONTS = {
    'usc': ['Gotham', 'Arial', 'Helvetica'],
    'boston college': ['Georgia', 'Times New Roman', 'Arial']
}