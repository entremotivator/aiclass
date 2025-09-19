"""
Configuration settings for the Enhanced Business AI Assistant
"""

# Application Settings
APP_CONFIG = {
    "title": "Enhanced Business AI Assistant",
    "icon": "🤖",
    "layout": "wide",
    "sidebar_state": "expanded"
}

# Model Configuration
DEFAULT_MODELS = {
    "chat": "gpt-4-turbo",
    "image": "dall-e-3"
}

# UI Settings
UI_CONFIG = {
    "max_chat_history": 50,  # Maximum number of messages to keep in memory
    "auto_scroll": True,
    "show_token_count": True,
    "show_cost_estimate": True
}

# Rate Limiting (optional - for production use)
RATE_LIMITS = {
    "requests_per_minute": 60,
    "tokens_per_hour": 100000,
    "images_per_hour": 20
}

# Feature Flags
FEATURES = {
    "image_generation": True,
    "chat_export": True,
    "usage_analytics": True,
    "bot_search": True,
    "cost_tracking": True
}
