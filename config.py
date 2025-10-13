# Configuration file for the Futbol Sevenler Attendance Tracker

# Application Settings
APP_TITLE = "Futbol Sevenler - Attendance Tracker"
APP_ICON = "⚽"
MAX_FILE_SIZE_MB = 10

# Response Detection Patterns

# Turkish Positive Patterns
POSITIVE_PATTERNS_TR = [
    "geliyorum", "gelirim", "varım", "katılıyorum", "katılırım",
    "evet", "tamam", "ok", "olur", "geleceğim", "ben de var",
    "ben varım", "bende varım", "tabii", "kesinlikle"
]

# Turkish Negative Patterns  
NEGATIVE_PATTERNS_TR = [
    "gelemem", "gelemiyorum", "yokum", "katılamam", "katılamıyorum",
    "hayır", "olmaz", "maalesef", "üzgünüm", "gidemem", "mümkün değil"
]

# Turkish Maybe Patterns
MAYBE_PATTERNS_TR = [
    "belki", "muhtemelen", "sanırım", "galiba", "bakacağım",
    "deneyeceğim", "emin değilim", "sonra söylerim", "bakarım"
]

# English Patterns
POSITIVE_PATTERNS_EN = [
    "yes", "coming", "will come", "count me in", "i'm in", "sure", "okay"
]

NEGATIVE_PATTERNS_EN = [
    "no", "can't", "cannot", "won't", "will not", "not coming", "sorry"
]

MAYBE_PATTERNS_EN = [
    "maybe", "probably", "might", "not sure", "will try", "let me check"
]

# Emoji Patterns
POSITIVE_EMOJIS = ["👍", "✅", "☑️", "✓", "👌", "💪", "⚽"]
NEGATIVE_EMOJIS = ["❌", "❎", "👎", "😢", "😞", "🚫"]
MAYBE_EMOJIS = ["🤔", "🤷", "❓", "❔", "🤷‍♂️", "🤷‍♀️"]

# UI Colors
COLORS = {
    "yes": "#28a745",
    "maybe": "#ffc107", 
    "no": "#dc3545",
    "primary": "#1f77b4",
    "background": "#f8f9fa"
}

# Export Settings
EXPORT_FORMATS = ["CSV", "Excel", "Text Summary"]
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"