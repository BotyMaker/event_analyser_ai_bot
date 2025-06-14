from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .localization import localization


def create_language_keyboard(current_language: str = "en") -> InlineKeyboardMarkup:
    """Create inline keyboard for language selection."""
    keyboard = []
    
    for lang_code in localization.SUPPORTED_LANGUAGES:
        lang_name = localization.get_language_name(lang_code, current_language)
        # Add checkmark for current language
        if lang_code == current_language:
            lang_name = f"✅ {lang_name}"
        
        keyboard.append([
            InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}")
        ])
    
    return InlineKeyboardMarkup(keyboard)


def create_onboarding_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard for language selection from start command."""
    keyboard = []
    
    for lang_code in localization.SUPPORTED_LANGUAGES:
        lang_name = localization.get_language_name(lang_code, lang_code)
        
        keyboard.append([
            InlineKeyboardButton(lang_name, callback_data=f"onboard_{lang_code}")
        ])
    
    return InlineKeyboardMarkup(keyboard)


def create_custom_instruction_keyboard(language: str = "en") -> InlineKeyboardMarkup:
    """Create inline keyboard for custom instruction selection during onboarding."""
    keyboard = [
        [
            InlineKeyboardButton(
                localization.get_text('onboarding.custom_instruction_default', language),
                callback_data="custom_default"
            )
        ],
        [
            InlineKeyboardButton(
                localization.get_text('onboarding.custom_instruction_custom', language),
                callback_data="custom_input"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def create_settings_keyboard(language: str = "en") -> InlineKeyboardMarkup:
    """Create inline keyboard for settings management."""
    keyboard = [
        [
            InlineKeyboardButton(
                localization.get_text('settings.keep_current', language),
                callback_data="settings_keep"
            )
        ],
        [
            InlineKeyboardButton(
                localization.get_text('settings.reset_default', language),
                callback_data="settings_reset"
            )
        ],
        [
            InlineKeyboardButton(
                localization.get_text('settings.change_custom', language),
                callback_data="settings_change"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard) 